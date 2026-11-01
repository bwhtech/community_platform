"""Serves the Vue SPA for every community route, with per-route meta tags so
shared profile and request links preview well."""

import frappe
from frappe.utils import get_url

from community_platform.api.session import get_boot
from community_platform.points import cached_total

no_cache = 1

SITE_TITLE = "Frappe Community"
SITE_DESCRIPTION = "Points, badges and feature requests for everyone building with Frappe."


def get_context(context):
	# Each key becomes a window global in the built index.html.
	context.boot = {**get_boot(), "csrf_token": frappe.sessions.get_csrf_token()}
	context.site_name = frappe.local.site
	context.meta = route_meta(frappe.local.request.path)
	frappe.db.commit()
	return context


def route_meta(path: str) -> dict:
	meta = {"title": SITE_TITLE, "description": SITE_DESCRIPTION, "image": None, "url": get_url(path)}
	parts = [p for p in path.split("/") if p]
	if len(parts) == 2 and parts[0] == "u":
		profile_meta(meta, parts[1])
	elif len(parts) == 2 and parts[0] == "requests" and parts[1].isdigit():
		request_meta(meta, int(parts[1]))
	elif parts[:1] == ["leaderboard"]:
		meta["title"] = f"Leaderboard · {SITE_TITLE}"
	elif parts[:1] == ["requests"]:
		meta["title"] = f"Feature requests · {SITE_TITLE}"
	return meta


def profile_meta(meta: dict, login: str):
	user = frappe.db.get_value("Contributor", login, "user")
	if not user:
		return
	u = frappe.db.get_value("User", user, ["full_name", "user_image", "bio"], as_dict=True)
	meta["title"] = f"{u.full_name or login} · {SITE_TITLE}"
	meta["description"] = f"{cached_total(login):,} points. {u.bio or ''}".strip()
	meta["image"] = get_url(u.user_image) if u.user_image else None


def request_meta(meta: dict, request_id: int):
	r = frappe.db.get_value(
		"Feature Request", {"name": request_id, "hidden": 0}, ["title", "upvote_count"], as_dict=True
	)
	if not r:
		return
	meta["title"] = f"{r.title} · {SITE_TITLE}"
	meta["description"] = f"{r.upvote_count} upvotes on the Frappe community feature requests."


@frappe.whitelist(allow_guest=True, methods=["POST"])
def get_context_for_dev() -> dict:
	"""Boot data for the Vite dev server, which can't render the Jinja template."""
	if not frappe.conf.developer_mode:
		frappe.throw("This method is only meant for developer mode")
	return {**get_boot(), "csrf_token": frappe.sessions.get_csrf_token()}
