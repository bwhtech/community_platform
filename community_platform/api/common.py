"""Helpers shared by the API modules. Responses use the camelCase shapes the
frontend reads, so pages don't translate field names."""

import frappe
from frappe import _

from community_platform.utils import split_lines

ADMIN_ROLES = {"System Manager", "Community Admin"}
MODERATOR_ROLES = ADMIN_ROLES | {"Community Moderator"}


def current_contributor() -> str | None:
	"""GitHub login of the logged-in user's Contributor, if they have one."""
	if frappe.session.user == "Guest":
		return None
	return frappe.db.get_value("Contributor", {"user": frappe.session.user}, "name")


def require_contributor() -> str:
	login = current_contributor()
	if not login:
		frappe.throw(_("Log in with GitHub to do that."), frappe.PermissionError)
	return login


def is_admin() -> bool:
	return bool(ADMIN_ROLES & set(frappe.get_roles()))


def is_moderator() -> bool:
	return bool(MODERATOR_ROLES & set(frappe.get_roles()))


def require_admin():
	if not is_admin():
		frappe.throw(_("Only community admins can do that."), frappe.PermissionError)


def require_moderator():
	if not is_moderator():
		frappe.throw(_("Only moderators can do that."), frappe.PermissionError)


def people(logins) -> dict[str, dict]:
	"""Public card data for many contributors in one query."""
	logins = list({login for login in logins if login})
	if not logins:
		return {}
	contributor = frappe.qb.DocType("Contributor")
	user = frappe.qb.DocType("User")
	rows = (
		frappe.qb.from_(contributor)
		.join(user)
		.on(user.name == contributor.user)
		.select(contributor.name, user.full_name, user.user_image.as_("avatar"))
		.where(contributor.name.isin(logins))
	).run(as_dict=True)
	found = {row.name: card(row) for row in rows}
	return {
		login: found.get(login) or {"login": login, "fullName": login, "avatar": None} for login in logins
	}


def person(login: str | None) -> dict | None:
	return people([login]).get(login) if login else None


def card(row) -> dict:
	return {"login": row.name, "fullName": row.full_name or row.name, "avatar": row.avatar}


def products() -> list[dict]:
	return [
		{
			"id": row.name,
			"name": row.product_name,
			"logo": row.logo,
			"repos": split_lines(row.repos),
			"discussCategories": split_lines(row.discuss_categories),
			"schoolCourses": split_lines(row.school_courses),
		}
		for row in frappe.get_all(
			"Product",
			fields=["name", "product_name", "logo", "repos", "discuss_categories", "school_courses"],
			order_by="sort_order asc, product_name asc",
		)
	]


def product_map() -> dict[str, dict]:
	return {p["id"]: p for p in products()}
