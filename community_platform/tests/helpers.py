import frappe

from community_platform.points import clear_total


def make_contributor(login: str, user: str | None = None) -> str:
	if not frappe.db.exists("Contributor", login):
		frappe.get_doc(
			{
				"doctype": "Contributor",
				"github_login": login,
				"user": user or make_user(f"{login}@example.com"),
			}
		).insert(ignore_permissions=True)
	# Test rollbacks don't reach Redis.
	clear_total(login)
	return login


def make_user(email: str) -> str:
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": email.split("@")[0], "send_welcome_email": 0}
		).insert(ignore_permissions=True)
	return email
