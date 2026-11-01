"""Accepted solutions on Discuss (Discourse), read from the public user actions feed."""

import frappe
import requests

from community_platform import points
from community_platform.api.common import products
from community_platform.utils import to_ist_date

SOLVED_FILTER = 15  # Discourse user action type for "solution accepted"
PAGE_SIZE = 30


def sync_all():
	"""Daily: everyone who connected Discuss."""
	if not frappe.get_cached_doc("Community Settings").enable_discuss_sync:
		return
	for login in frappe.get_all("Contributor", filters={"discuss_username": ["is", "set"]}, pluck="name"):
		sync_contributor(login)
		frappe.db.commit()


def sync_contributor(login: str):
	username = frappe.db.get_value("Contributor", login, "discuss_username")
	if not username:
		return
	base = (frappe.get_cached_doc("Community Settings").discuss_url or "https://discuss.frappe.io").rstrip(
		"/"
	)
	category_products = product_by_category(base)

	for action in solved_actions(base, username):
		points.award(
			login,
			"discuss_solution",
			external_id=f"discuss:{action['topic_id']}",
			title=action.get("title") or "Discuss topic",
			url=f"{base}/t/{action.get('slug', '-')}/{action['topic_id']}",
			event_date=to_ist_date(action["created_at"]),
			product=category_products.get(action.get("category_id")),
			evaluate_badges=False,
		)
	points.evaluate(login)


def solved_actions(base: str, username: str):
	offset = 0
	while True:
		response = requests.get(
			f"{base}/user_actions.json",
			params={"username": username, "filter": SOLVED_FILTER, "offset": offset},
			timeout=30,
		)
		if response.status_code == 404:
			return
		response.raise_for_status()
		actions = response.json().get("user_actions", [])
		yield from actions
		if len(actions) < PAGE_SIZE:
			return
		offset += len(actions)


def product_by_category(base: str) -> dict[int, str]:
	"""Discourse category id → product, matched on the names admins list per product."""
	by_name = {name.lower(): p["id"] for p in products() for name in p["discussCategories"]}
	response = requests.get(f"{base}/categories.json", params={"include_subcategories": "true"}, timeout=30)
	response.raise_for_status()
	out = {}
	for category in response.json().get("category_list", {}).get("categories", []):
		for c in [category, *category.get("subcategory_list", [])]:
			if product := by_name.get(c["name"].lower()):
				out[c["id"]] = product
	return out
