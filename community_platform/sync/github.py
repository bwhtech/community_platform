"""GitHub activity in the configured org, pulled through the Search API.

Three searches per contributor: issues they opened, PRs they authored that got
merged, and merged PRs by others that they reviewed. The first run backfills
history one year at a time (search caps results at 1,000 per query); later
runs only ask for items updated since the last sync.
"""

import time
from datetime import date

import frappe
import requests

from community_platform import points
from community_platform.api.common import products
from community_platform.utils import to_ist_date

API = "https://api.github.com/search/issues"
PER_PAGE = 100
MAX_PAGES = 10
FIRST_YEAR = 2010
# Revoke points for issues that turn out not to be real work.
REJECTED_REASONS = {"not_planned", "duplicate"}


def sync_all():
	"""Hourly: every contributor, one after another."""
	settings = frappe.get_cached_doc("Community Settings")
	if not settings.enable_github_sync:
		return
	for login in frappe.get_all("Contributor", pluck="name"):
		sync_contributor(login)
		frappe.db.commit()


def sync_contributor(login: str):
	contributor = frappe.get_doc("Contributor", login)
	settings = frappe.get_cached_doc("Community Settings")
	client = SearchClient(settings.get_password("github_token", raise_exception=False))
	repo_products = product_by_repo()

	windows = (
		[f"updated:>={contributor.last_github_sync.date().isoformat()}"]
		if contributor.github_backfilled and contributor.last_github_sync
		else year_windows()
	)
	started = frappe.utils.now_datetime()
	for window in windows:
		sync_issues(client, settings.github_org, login, window, repo_products)
		sync_merged_prs(client, settings.github_org, login, window, repo_products)
		sync_reviews(client, settings.github_org, login, window, repo_products)

	contributor.db_set({"last_github_sync": started, "github_backfilled": 1}, update_modified=False)
	points.evaluate(login)


def sync_issues(client, org, login, window, repo_products):
	for item in client.search(f"org:{org} author:{login} type:issue {window}"):
		repo = repo_of(item)
		external_id = f"{repo}#{item['number']}"
		row = points.award(
			login,
			"github_issue_opened",
			external_id=external_id,
			title=item["title"],
			url=item["html_url"],
			event_date=to_ist_date(item["created_at"]),
			product=repo_products.get(repo),
			evaluate_badges=False,
		) or points.active_row(login, "github_issue_opened", external_id)
		if row and item.get("state_reason") in REJECTED_REASONS:
			points.revoke(
				row,
				f"Issue closed as {item['state_reason'].replace('_', ' ')}",
				to_ist_date(item["closed_at"]),
			)


def sync_merged_prs(client, org, login, window, repo_products):
	for item in client.search(f"org:{org} author:{login} type:pr is:merged {window}"):
		repo = repo_of(item)
		points.award(
			login,
			"github_pr_merged",
			external_id=f"{repo}#{item['number']}",
			title=item["title"],
			url=item["html_url"],
			event_date=to_ist_date(merged_at(item)),
			product=repo_products.get(repo),
			evaluate_badges=False,
		)


def sync_reviews(client, org, login, window, repo_products):
	for item in client.search(f"org:{org} reviewed-by:{login} -author:{login} type:pr is:merged {window}"):
		repo = repo_of(item)
		points.award(
			login,
			"github_pr_reviewed",
			external_id=f"{repo}#{item['number']}:review",
			title=item["title"],
			url=item["html_url"],
			# Dated by the merge, which saves a reviews API call per PR.
			event_date=to_ist_date(merged_at(item)),
			product=repo_products.get(repo),
			evaluate_badges=False,
		)


class SearchClient:
	def __init__(self, token: str | None):
		self.session = requests.Session()
		self.session.headers["Accept"] = "application/vnd.github+json"
		if token:
			self.session.headers["Authorization"] = f"Bearer {token}"
		# 30 searches a minute with a token, 10 without.
		self.pause = 2.1 if token else 6.1

	def search(self, query: str):
		for page in range(1, MAX_PAGES + 1):
			response = self.get(
				{"q": query, "per_page": PER_PAGE, "page": page, "sort": "created", "order": "asc"}
			)
			items = response.get("items", [])
			yield from items
			if len(items) < PER_PAGE:
				return

	def get(self, params: dict) -> dict:
		time.sleep(self.pause)
		response = self.session.get(API, params=params, timeout=30)
		if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
			reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
			time.sleep(max(reset - time.time(), 1) + 1)
			response = self.session.get(API, params=params, timeout=30)
		if response.status_code == 422:
			# The user has no public activity GitHub can search, e.g. a renamed account.
			return {}
		response.raise_for_status()
		return response.json()


def year_windows() -> list[str]:
	return [f"created:{year}-01-01..{year}-12-31" for year in range(FIRST_YEAR, date.today().year + 1)]


def product_by_repo() -> dict[str, str]:
	return {repo: p["id"] for p in products() for repo in p["repos"]}


def repo_of(item: dict) -> str:
	# repository_url is https://api.github.com/repos/<owner>/<repo>
	return "/".join(item["repository_url"].rsplit("/", 2)[-2:])


def merged_at(item: dict) -> str:
	return (item.get("pull_request") or {}).get("merged_at") or item["closed_at"]
