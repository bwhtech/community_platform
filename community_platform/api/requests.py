from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import frappe
from frappe import _

from community_platform import points
from community_platform.api.common import (
	current_contributor,
	is_moderator,
	people,
	product_map,
	require_contributor,
	require_moderator,
)
from community_platform.utils import IST, today_ist

EDIT_WINDOW = timedelta(hours=24)
DAILY_REQUEST_LIMIT = 5
REACTIONS = ["❤️", "🎉", "🚀", "👀", "😕"]
UPVOTE_ACTION = "request_upvote_received"
SORTS = {"top", "trending", "new"}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def list_requests(product: str = "all", sort: str = "top", query: str = "") -> list[dict]:
	filters = {}
	if not is_moderator():
		filters["hidden"] = 0
	if product and product != "all":
		filters["product"] = product
	if query.strip():
		filters["title"] = ["like", f"%{query.strip()}%"]

	requests = frappe.get_all(
		"Feature Request",
		filters=filters,
		fields=[
			"name",
			"title",
			"description",
			"product",
			"contributor",
			"creation",
			"hidden",
			"upvote_count",
		],
		limit=500,
	)
	summaries = summarize(requests)
	week_ago = frappe.utils.add_days(today_ist(), -7)
	recent = recent_votes([r.name for r in requests], week_ago)
	for s in summaries:
		s["recentUpvotes"] = recent.get(s["id"], 0)
	return sorted(summaries, key=SORT_KEYS[sort if sort in SORTS else "top"])


SORT_KEYS = {
	"top": lambda r: (-r["upvotes"], _neg_time(r["createdAt"])),
	"trending": lambda r: (-r["recentUpvotes"], -r["upvotes"]),
	"new": lambda r: _neg_time(r["createdAt"]),
}


def _neg_time(iso: str) -> float:
	return -datetime.fromisoformat(iso).timestamp()


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_request(id: int) -> dict | None:
	request = load(id)
	if not request or (request.hidden and not is_moderator()):
		return None
	summary = summarize([request])[0]
	voters = frappe.get_all(
		"Feature Request Vote",
		filters={"feature_request": request.name},
		fields=["contributor"],
		order_by="voted_on desc, creation desc",
		pluck="contributor",
	)
	cards = people(voters)
	summary["voters"] = [cards[v] for v in voters]
	summary["can"] = {"edit": can_edit(request), "delete": can_delete(request), "moderate": is_moderator()}
	return summary


@frappe.whitelist(methods=["POST"])
def create_request(title: str, description: str, product: str) -> int:
	me = require_contributor()
	validate_fields(title, description, product)
	if posted_today(me) >= DAILY_REQUEST_LIMIT:
		frappe.throw(_("You can post up to {0} requests a day.").format(DAILY_REQUEST_LIMIT))

	request = frappe.get_doc(
		{
			"doctype": "Feature Request",
			"title": title.strip(),
			"description": description.strip(),
			"product": product,
			"contributor": me,
		}
	).insert(ignore_permissions=True)
	# The author's own upvote counts toward the total but earns no points.
	add_vote(request.name, me)
	return request.name


@frappe.whitelist(methods=["POST"])
def update_request(id: int, title: str, description: str, product: str) -> None:
	request = load(id)
	if not can_edit(request):
		frappe.throw(_("Requests can only be edited by the author within 24 hours."), frappe.PermissionError)
	validate_fields(title, description, product)
	request.update({"title": title.strip(), "description": description.strip(), "product": product})
	request.save(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def delete_request(id: int) -> None:
	request = load(id)
	if not can_delete(request):
		frappe.throw(
			_("This request already has upvotes, so only a moderator can delete it."), frappe.PermissionError
		)
	revoke_upvote_points(request.name, "Feature request deleted")
	frappe.db.delete("Feature Request Vote", {"feature_request": request.name})
	frappe.db.delete("Feature Request Reaction", {"feature_request": request.name})
	frappe.delete_doc("Feature Request", request.name, ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def set_hidden(id: int, hidden: bool) -> None:
	require_moderator()
	request = load(id)
	request.db_set("hidden", int(hidden))
	if hidden:
		revoke_upvote_points(request.name, "Feature request hidden by a moderator")
	else:
		for voter in frappe.get_all(
			"Feature Request Vote", {"feature_request": request.name}, pluck="contributor"
		):
			award_upvote_point(request, voter)


@frappe.whitelist(methods=["POST"])
def toggle_upvote(id: int) -> None:
	me = require_contributor()
	request = load(id)
	if request.contributor == me:
		return
	existing = frappe.db.get_value(
		"Feature Request Vote", {"feature_request": request.name, "contributor": me}
	)
	if existing:
		frappe.delete_doc("Feature Request Vote", existing, ignore_permissions=True)
		row = points.active_row(request.contributor, UPVOTE_ACTION, upvote_id(request.name, me))
		if row:
			points.revoke(row, "Upvote withdrawn")
	else:
		add_vote(request.name, me)
		if not request.hidden:
			award_upvote_point(request, me)
	refresh_upvote_count(request.name)


@frappe.whitelist(methods=["POST"])
def toggle_reaction(id: int, emoji: str) -> None:
	me = require_contributor()
	if emoji not in REACTIONS:
		frappe.throw(_("Unknown reaction"))
	request = load(id)
	filters = {"feature_request": request.name, "contributor": me, "emoji": emoji}
	if existing := frappe.db.get_value("Feature Request Reaction", filters):
		frappe.delete_doc("Feature Request Reaction", existing, ignore_permissions=True)
	else:
		frappe.get_doc({"doctype": "Feature Request Reaction", **filters}).insert(ignore_permissions=True)


# -- Helpers --------------------------------------------------------------------


def load(id):
	name = frappe.utils.cint(id)
	if not frappe.db.exists("Feature Request", name):
		return None
	return frappe.get_doc("Feature Request", name)


def summarize(requests) -> list[dict]:
	names = [r.name for r in requests]
	me = current_contributor()
	votes = frappe.get_all(
		"Feature Request Vote", {"feature_request": ["in", names or [""]]}, ["feature_request", "contributor"]
	)
	reactions = frappe.get_all(
		"Feature Request Reaction",
		{"feature_request": ["in", names or [""]]},
		["feature_request", "contributor", "emoji"],
	)
	cards = people([r.contributor for r in requests])
	products = product_map()

	out = []
	for r in requests:
		# Link columns hold the autoincrement id as text.
		request_votes = [v for v in votes if v.feature_request == str(r.name)]
		request_reactions = [x for x in reactions if x.feature_request == str(r.name)]
		out.append(
			{
				"id": r.name,
				"title": r.title,
				"description": r.description,
				"product": r.product,
				"productInfo": products.get(r.product),
				"author": cards[r.contributor],
				"createdAt": r.creation.isoformat(),
				"hidden": bool(r.hidden),
				"upvotes": len(request_votes),
				"upvoted": any(v.contributor == me for v in request_votes),
				"isMine": bool(me) and r.contributor == me,
				"reactions": [
					{
						"emoji": emoji,
						"count": sum(1 for x in request_reactions if x.emoji == emoji),
						"mine": any(x.emoji == emoji and x.contributor == me for x in request_reactions),
					}
					for emoji in REACTIONS
				],
			}
		)
	return out


def recent_votes(names: list, since: str) -> dict:
	if not names:
		return {}
	rows = frappe.db.sql(
		"""select feature_request, count(*) from `tabFeature Request Vote`
		where feature_request in %(names)s and voted_on >= %(since)s
		group by feature_request""",
		{"names": tuple(names), "since": since},
	)
	return {int(name): n for name, n in rows}


def can_edit(request) -> bool:
	if not request or request.contributor != current_contributor():
		return False
	return frappe.utils.now_datetime() - frappe.utils.get_datetime(request.creation) < EDIT_WINDOW


def can_delete(request) -> bool:
	if not request or frappe.session.user == "Guest":
		return False
	if is_moderator():
		return True
	other_votes = frappe.db.count(
		"Feature Request Vote", {"feature_request": request.name, "contributor": ["!=", request.contributor]}
	)
	return request.contributor == current_contributor() and other_votes == 0


def validate_fields(title: str, description: str, product: str):
	if len(title.strip()) < 8:
		frappe.throw(_("Title needs at least 8 characters."))
	if len(description.strip()) < 20:
		frappe.throw(_("Description needs at least 20 characters."))
	if not frappe.db.exists("Product", product):
		frappe.throw(_("Pick a product."))


def posted_today(contributor: str) -> int:
	"""Requests since IST midnight. `creation` is stored in the system timezone."""
	midnight = datetime.fromisoformat(today_ist()).replace(tzinfo=IST)
	system_tz = ZoneInfo(frappe.utils.get_system_timezone())
	since = midnight.astimezone(system_tz).replace(tzinfo=None)
	return frappe.db.count("Feature Request", {"contributor": contributor, "creation": [">=", since]})


def add_vote(request_name, contributor: str):
	frappe.get_doc(
		{
			"doctype": "Feature Request Vote",
			"feature_request": request_name,
			"contributor": contributor,
			"voted_on": today_ist(),
		}
	).insert(ignore_permissions=True)
	refresh_upvote_count(request_name)


def refresh_upvote_count(request_name):
	count = frappe.db.count("Feature Request Vote", {"feature_request": request_name})
	frappe.db.set_value("Feature Request", request_name, "upvote_count", count, update_modified=False)


def upvote_id(request_name, voter: str) -> str:
	return f"fr:{request_name}:{voter}"


def award_upvote_point(request, voter: str):
	if voter == request.contributor:
		return
	points.award(
		request.contributor,
		UPVOTE_ACTION,
		external_id=upvote_id(request.name, voter),
		cap_target=f"fr:{request.name}",
		title=request.title,
		url=f"/requests/{request.name}",
		event_date=today_ist(),
	)


def revoke_upvote_points(request_name, reason: str):
	contributor = frappe.db.get_value("Feature Request", request_name, "contributor")
	for voter in frappe.get_all(
		"Feature Request Vote", {"feature_request": request_name}, pluck="contributor"
	):
		row = points.active_row(contributor, UPVOTE_ACTION, upvote_id(request_name, voter))
		if row:
			points.revoke(row, reason)
