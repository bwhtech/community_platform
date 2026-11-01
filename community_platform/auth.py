"""Turns a GitHub login into a Contributor."""

import frappe

from community_platform.utils import today_ist


def on_session_creation(login_manager=None):
	user = frappe.session.user
	if user in ("Guest", "Administrator") or frappe.db.exists("Contributor", {"user": user}):
		return
	github = frappe.db.get_value(
		"User Social Login", {"parent": user, "provider": "github"}, ["userid", "username"], as_dict=True
	)
	if not github or not github.username:
		return
	login = link_contributor(user, github.username, github.userid)
	# Backfill full history in the background; the profile fills in as it runs.
	frappe.enqueue(
		"community_platform.sync.github.sync_contributor",
		login=login,
		queue="long",
		job_id=f"github-sync-{login}",
		deduplicate=True,
		enqueue_after_commit=True,
	)


def link_contributor(user: str, github_login: str, github_id=None) -> str:
	"""Attach the user to their Contributor, creating it on first login. Name,
	avatar, bio and location stay on the User."""
	user_doc = frappe.get_doc("User", user)
	if frappe.db.exists("Contributor", github_login):
		contributor = frappe.get_doc("Contributor", github_login)
	else:
		contributor = frappe.new_doc("Contributor")
		contributor.update({"github_login": github_login, "joined_on": today_ist()})
	contributor.user = user
	contributor.github_id = frappe.utils.cint(github_id) or contributor.github_id
	emails = set((contributor.verified_emails or "").split())
	emails.add(user_doc.email)
	contributor.verified_emails = "\n".join(sorted(emails))
	contributor.save(ignore_permissions=True)
	return contributor.name
