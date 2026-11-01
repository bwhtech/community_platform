import frappe

from community_platform.api.common import current_contributor, is_admin, is_moderator, person, products


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def get_boot() -> dict:
	"""Everything the SPA needs before its first render."""
	login = current_contributor()
	return {
		"user": frappe.session.user,
		"me": person(login) if login else None,
		"isModerator": is_moderator(),
		"isAdmin": is_admin(),
		"products": products(),
		"githubLoginUrl": github_login_url(),
	}


def github_login_url() -> str | None:
	"""Entry point of the GitHub login, or None until a Social Login Key is set up."""
	if not github_enabled():
		return None
	return "/api/method/community_platform.api.session.github_login"


@frappe.whitelist(allow_guest=True, methods=["GET"])
def github_login(redirect_to: str = "/me") -> None:
	"""Starts the OAuth flow on click, so page views don't mint OAuth state."""
	from frappe.utils.oauth import get_oauth2_authorize_url

	if not github_enabled():
		frappe.throw("GitHub login is not set up yet.")
	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = get_oauth2_authorize_url("github", redirect_to)


def github_enabled() -> bool:
	return bool(
		frappe.db.get_value("Social Login Key", {"social_login_provider": "GitHub", "enable_social_login": 1})
	)
