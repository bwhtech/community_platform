import frappe
from frappe import _

from community_platform import points
from community_platform.api.badges import BADGE_FIELDS, describe, serialize
from community_platform.api.common import people, require_admin

RULE_FIELDS = {"points": "points", "cap": "cap_per_target", "enabled": "enabled"}
BADGE_INPUT = {
	"title": "title",
	"description": "description",
	"icon": "icon",
	"color": "color",
	"criteriaType": "criteria_type",
	"action": "action",
	"threshold": "threshold",
	"rankLimit": "rank_limit",
	"product": "product",
}


@frappe.whitelist(methods=["GET"])
def list_point_rules() -> list[dict]:
	require_admin()
	return [
		{
			"action": r.name,
			"label": r.label,
			"source": r.source,
			"points": r.points,
			"cap": r.cap_per_target or None,
			"enabled": bool(r.enabled),
		}
		for r in frappe.get_all(
			"Point Rule",
			fields=["name", "label", "source", "points", "cap_per_target", "enabled"],
			order_by="creation asc",
		)
	]


@frappe.whitelist(methods=["POST"])
def update_point_rule(action: str, patch: dict) -> None:
	require_admin()
	doc = frappe.get_doc("Point Rule", action)
	for key, field in RULE_FIELDS.items():
		if key in patch:
			doc.set(field, patch[key])
	doc.save(ignore_permissions=True)


@frappe.whitelist(methods=["GET"])
def list_badges() -> list[dict]:
	require_admin()
	labels = dict(frappe.get_all("Point Rule", fields=["name", "label"], as_list=True))
	products = dict(frappe.get_all("Product", fields=["name", "product_name"], as_list=True))
	counts = dict(
		frappe.db.sql("select badge, count(distinct contributor) from `tabContributor Badge` group by badge")
	)
	return [
		{**serialize(b), "criteria": describe(b, labels, products), "earnedCount": counts.get(b.name, 0)}
		for b in frappe.get_all("Badge", fields=BADGE_FIELDS, order_by="creation asc")
	]


@frappe.whitelist(methods=["POST"])
def save_badge(badge: dict) -> str:
	require_admin()
	doc = frappe.get_doc("Badge", badge["id"]) if badge.get("id") else frappe.new_doc("Badge")
	for key, field in BADGE_INPUT.items():
		if key in badge:
			doc.set(field, badge[key] or None)
	doc.save(ignore_permissions=True)
	return doc.name


@frappe.whitelist(methods=["POST"])
def delete_badge(id: str) -> None:
	require_admin()
	frappe.db.delete("Contributor Badge", {"badge": id})
	frappe.delete_doc("Badge", id, ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def award_badge(id: str, login: str) -> None:
	require_admin()
	if frappe.db.exists("Contributor Badge", {"badge": id, "contributor": login}):
		frappe.throw(_("{0} already has this badge.").format(login))
	points.give_badge(login, id, frappe.utils.today())


@frappe.whitelist(methods=["POST"])
def update_product(id: str, patch: dict) -> None:
	require_admin()
	doc = frappe.get_doc("Product", id)
	for key, field in {
		"repos": "repos",
		"discussCategories": "discuss_categories",
		"schoolCourses": "school_courses",
	}.items():
		if key in patch:
			doc.set(field, "\n".join(patch[key]))
	doc.save(ignore_permissions=True)


@frappe.whitelist(methods=["GET"])
def list_ledger(login: str | None = None, source: str = "all", limit: int = 50) -> dict:
	require_admin()
	filters = {}
	if login:
		filters["contributor"] = login
	if source and source != "all":
		filters["source"] = source
	limit = max(1, min(int(limit), 1000))
	rows = frappe.get_all(
		"Point Ledger",
		filters=filters,
		fields=[
			"name",
			"contributor",
			"action",
			"source",
			"points",
			"title",
			"event_date",
			"is_revoke",
			"reason",
		],
		order_by="event_date desc, creation desc",
		limit=limit + 1,
	)
	shown = rows[:limit]
	revoked = set(
		frappe.get_all("Point Ledger", {"revokes": ["in", [r.name for r in shown] or [""]]}, pluck="revokes")
	)
	cards = people([r.contributor for r in shown])
	return {
		"rows": [
			{
				"id": r.name,
				"login": r.contributor,
				"person": cards[r.contributor],
				"action": r.action,
				"source": r.source,
				"points": r.points,
				"title": r.title,
				"date": str(r.event_date),
				"isRevoke": bool(r.is_revoke),
				"reason": r.reason,
				"revoked": r.name in revoked,
			}
			for r in shown
		],
		"hasMore": len(rows) > limit,
	}


@frappe.whitelist(methods=["POST"])
def revoke_entry(id: str, reason: str) -> None:
	require_admin()
	if not reason.strip():
		frappe.throw(_("Give a reason."))
	if not points.revoke(id, reason.strip()):
		frappe.throw(_("This entry is already revoked."))


@frappe.whitelist(methods=["GET"])
def list_contributors() -> list[dict]:
	require_admin()
	cards = people(frappe.get_all("Contributor", pluck="name"))
	return sorted(cards.values(), key=lambda card: card["fullName"].lower())
