import frappe

from community_platform.api.common import product_map
from community_platform.points import cached_total
from community_platform.ranking import rank_contributors
from community_platform.utils import today_ist

PUBLIC_FIELDS = [
	"name",
	"user",
	"company",
	"website",
	"x_handle",
	"linkedin",
	"youtube",
	"discuss_username",
	"joined_on",
	"creation",
]
PUBLIC_USER_FIELDS = ["full_name", "user_image", "bio", "location"]


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_profile(login: str) -> dict | None:
	c = frappe.db.get_value("Contributor", login, PUBLIC_FIELDS, as_dict=True)
	if not c:
		return None
	user = frappe.db.get_value("User", c.user, PUBLIC_USER_FIELDS, as_dict=True) or frappe._dict()
	month = today_ist()[:7]
	kept = kept_rows(login)
	return {
		"login": c.name,
		"fullName": user.full_name or c.name,
		"avatar": user.user_image,
		"bio": user.bio,
		"company": c.company,
		"location": user.location,
		"website": c.website,
		"x": c.x_handle,
		"linkedin": c.linkedin,
		"youtube": c.youtube,
		"discussUsername": c.discuss_username,
		"joinedOn": str(c.joined_on or c.creation.date()),
		"products": frappe.get_all(
			"Contributor Product",
			{"parent": login, "parenttype": "Contributor"},
			pluck="product",
			order_by="idx",
		),
		"totalPoints": cached_total(login),
		"overallRank": rank_of(login),
		"monthRank": rank_of(login, month),
		"monthPoints": month_points(login, month),
		"badges": badges_of(login),
		"certifications": [r for r in kept if r["action"] == "school_certification"],
		"talks": [r for r in kept if r["action"] == "event_talk"],
		"eventsAttended": [r for r in kept if r["action"] == "event_attended"],
		"stats": {
			"prsMerged": count(kept, "github_pr_merged"),
			"issuesOpened": count(kept, "github_issue_opened"),
			"reviews": count(kept, "github_pr_reviewed"),
			"solutions": count(kept, "discuss_solution"),
		},
		"heatmapYears": heatmap_years(login),
	}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_heatmap(login: str, period: str = "last", source: str = "all") -> dict:
	"""Daily activity counts for the last 12 months, or for one calendar year."""
	today = today_ist()
	if period == "last":
		start = frappe.utils.add_days(today, -364)
		end = today
	else:
		start, end = f"{int(period)}-01-01", min(f"{int(period)}-12-31", today)

	values = {"login": login, "start": start, "end": end}
	source_clause = ""
	if source and source != "all":
		values["source"] = source
		source_clause = "and source = %(source)s"
	# Negative rows count against totals but never show on the heatmap.
	rows = frappe.db.sql(
		f"""
		select event_date, count(*) as n
		from `tabPoint Ledger`
		where contributor = %(login)s and is_revoke = 0
			and event_date between %(start)s and %(end)s {source_clause}
		group by event_date
		""",
		values,
		as_dict=True,
	)
	counts = {str(r.event_date): int(r.n) for r in rows}
	return {"start": str(start), "end": str(end), "counts": counts, "total": sum(counts.values())}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_activity(login: str, source: str = "all", date: str | None = None, limit: int = 7) -> dict:
	filters = {"contributor": login, "is_revoke": 0}
	if source and source != "all":
		filters["source"] = source
	if date:
		filters["event_date"] = date
	limit = max(1, min(int(limit), 500))
	rows = frappe.get_all(
		"Point Ledger",
		filters=filters,
		fields=["name", "action", "source", "points", "title", "url", "external_id", "product", "event_date"],
		order_by="event_date desc, creation desc",
		limit=limit + 1,
	)
	revoked = revoked_names([r.name for r in rows])
	products = product_map()
	return {
		"rows": [
			{
				"id": r.name,
				"action": r.action,
				"source": r.source,
				"points": r.points,
				"title": r.title,
				"url": r.url,
				"externalId": r.external_id,
				"product": r.product,
				"productInfo": products.get(r.product),
				"date": str(r.event_date),
				"revoked": r.name in revoked,
			}
			for r in rows[:limit]
		],
		"hasMore": len(rows) > limit,
	}


def kept_rows(login: str) -> list[dict]:
	rows = frappe.get_all(
		"Point Ledger",
		filters={"contributor": login, "is_revoke": 0},
		fields=["name", "action", "title", "url", "event_date"],
		order_by="event_date desc",
	)
	revoked = revoked_names([r.name for r in rows])
	return [
		{"id": r.name, "action": r.action, "title": r.title, "url": r.url, "date": str(r.event_date)}
		for r in rows
		if r.name not in revoked
	]


def revoked_names(names: list[str]) -> set[str]:
	if not names:
		return set()
	return set(frappe.get_all("Point Ledger", {"revokes": ["in", names]}, pluck="revokes"))


def count(rows: list[dict], action: str) -> int:
	return sum(1 for r in rows if r["action"] == action)


def rank_of(login: str, month: str | None = None) -> int | None:
	return next((r["rank"] for r in rank_contributors(month=month) if r["login"] == login), None)


def month_points(login: str, month: str) -> int:
	result = frappe.db.sql(
		"""select coalesce(sum(points), 0) from `tabPoint Ledger`
		where contributor = %s and event_date like %s""",
		(login, f"{month}-%"),
	)
	return int(result[0][0])


def badges_of(login: str) -> list[dict]:
	awards = frappe.get_all(
		"Contributor Badge",
		filters={"contributor": login},
		fields=["badge", "awarded_on", "period"],
		order_by="awarded_on desc",
	)
	badges = {
		b.name: b
		for b in frappe.get_all(
			"Badge",
			filters={"name": ["in", [a.badge for a in awards]]},
			fields=["name", "title", "icon", "color", "description"],
		)
	}
	return [
		{
			"id": a.badge,
			"title": badges[a.badge].title,
			"icon": badges[a.badge].icon,
			"color": badges[a.badge].color,
			"description": badges[a.badge].description,
			"awardedOn": str(a.awarded_on),
			"period": a.period,
		}
		for a in awards
		if a.badge in badges
	]


def heatmap_years(login: str) -> list[int]:
	first = frappe.db.get_value(
		"Point Ledger", {"contributor": login}, "event_date", order_by="event_date asc"
	)
	last = int(today_ist()[:4])
	first_year = first.year if first else last
	return list(range(last, first_year - 1, -1))
