import frappe

from community_platform.api.common import current_contributor, people

BADGE_FIELDS = [
	"name",
	"title",
	"icon",
	"color",
	"description",
	"criteria_type",
	"action",
	"threshold",
	"rank_limit",
	"product",
]


@frappe.whitelist(allow_guest=True, methods=["GET"])
def list_badges() -> list[dict]:
	me = current_contributor()
	badges = frappe.get_all("Badge", fields=BADGE_FIELDS, order_by="creation asc")
	awards = frappe.get_all(
		"Contributor Badge", fields=["badge", "contributor", "awarded_on"], order_by="awarded_on desc"
	)
	labels = dict(frappe.get_all("Point Rule", fields=["name", "label"], as_list=True))
	products = dict(frappe.get_all("Product", fields=["name", "product_name"], as_list=True))

	out = []
	for b in badges:
		badge_awards = [a for a in awards if a.badge == b.name]
		earners = list(dict.fromkeys(a.contributor for a in badge_awards))
		cards = people(earners[:6])
		mine = next((a for a in badge_awards if a.contributor == me), None)
		out.append(
			{
				**serialize(b),
				"criteria": describe(b, labels, products),
				"earnedCount": len(earners),
				"recentEarners": [cards[login] for login in earners[:6]],
				"earnedByMe": str(mine.awarded_on) if mine else None,
			}
		)
	return out


def serialize(b) -> dict:
	return {
		"id": b.name,
		"title": b.title,
		"icon": b.icon,
		"color": b.color,
		"description": b.description,
		"criteriaType": b.criteria_type,
		"action": b.action,
		"threshold": b.threshold,
		"rankLimit": b.rank_limit,
		"product": b.product,
	}


def describe(b, labels: dict, products: dict) -> str:
	scope = f" in {products.get(b.product, b.product)}" if b.product else ""
	if b.criteria_type == "action_count":
		return f"{b.threshold} \u00d7 {labels.get(b.action, b.action).lower()}{scope}"
	if b.criteria_type == "points_total":
		return f"{b.threshold:,} points in total"
	if b.criteria_type == "monthly_rank":
		return f"Top {b.rank_limit} on the monthly leaderboard{scope}"
	return "Awarded by admins"
