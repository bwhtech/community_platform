import frappe
from frappe import _
from frappe.auth import LoginAttemptTracker
from frappe.rate_limiter import rate_limit
from frappe.utils.password import check_password, update_password

from community_platform.api.common import require_contributor

# SVG is left out: served from this origin it can run scripts.
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

# Name, photo, bio and location live on the User; the rest is community-only.
USER_FIELDS = {"bio": "bio", "location": "location"}
CONTRIBUTOR_FIELDS = {
	"company": "company",
	"website": "website",
	"x": "x_handle",
	"linkedin": "linkedin",
	"youtube": "youtube",
}


@frappe.whitelist(methods=["GET"])
def get_my_profile() -> dict:
	doc = frappe.get_doc("Contributor", require_contributor())
	user = frappe.db.get_value(
		"User", doc.user, ["full_name", "email", "user_image", *USER_FIELDS.values()], as_dict=True
	)
	return {
		"login": doc.name,
		"fullName": user.full_name or "",
		"email": user.email,
		"avatar": user.user_image,
		"hasPassword": has_password(doc.user),
		**{key: user.get(field) or "" for key, field in USER_FIELDS.items()},
		**{key: doc.get(field) or "" for key, field in CONTRIBUTOR_FIELDS.items()},
		"products": [row.product for row in doc.products],
		"discussUsername": doc.discuss_username,
		"emails": [e.strip() for e in (doc.verified_emails or "").splitlines() if e.strip()],
		"lastGithubSync": str(doc.last_github_sync) if doc.last_github_sync else None,
	}


@frappe.whitelist(methods=["POST"])
def update_profile(profile: dict) -> None:
	doc = frappe.get_doc("Contributor", require_contributor())
	save_user({field: (profile[key] or "").strip() for key, field in USER_FIELDS.items() if key in profile})
	for key, field in CONTRIBUTOR_FIELDS.items():
		if key in profile:
			doc.set(field, (profile[key] or "").strip())
	if "products" in profile:
		doc.set("products", [{"product": p} for p in profile["products"] if frappe.db.exists("Product", p)])
	doc.save(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def update_name(full_name: str) -> None:
	full_name = full_name.strip()
	if not full_name:
		frappe.throw(_("Name is required."))
	first_name, *rest = full_name.split(None, 1)
	save_user({"first_name": first_name, "middle_name": None, "last_name": rest[0] if rest else None})


@frappe.whitelist(methods=["POST"])
def update_photo(file_url: str | None = None) -> None:
	"""Set the photo to a public image the user uploaded, or clear it."""
	if file_url and not (
		file_url.lower().endswith(IMAGE_EXTENSIONS)
		and frappe.db.exists("File", {"file_url": file_url, "owner": frappe.session.user, "is_private": 0})
	):
		frappe.throw(_("Upload an image first."))
	save_user({"user_image": file_url or None})


def save_user(values: dict):
	"""Write profile fields that live on the User. Website users can't save it themselves."""
	require_contributor()
	user = frappe.get_doc("User", frappe.session.user)
	user.update(values)
	user.save(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=5, seconds=300)
def change_password(old_password: str, new_password: str) -> None:
	"""Failed attempts count towards the same lockout as the login page."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("You must be logged in to change your password"), frappe.AuthenticationError)

	tracker = LoginAttemptTracker(user)
	if not tracker.is_user_allowed():
		frappe.throw(_("Too many failed attempts. Please try again after some time."))

	if old_password == new_password:
		frappe.throw(_("New password cannot be the same as current password."))

	try:
		check_password(user, old_password)
	except frappe.AuthenticationError:
		tracker.add_failure_attempt()
		frappe.throw(_("Incorrect current password. Please try again."))
	else:
		tracker.add_success_attempt()

	from frappe.core.doctype.user.user import test_password_strength

	feedback = test_password_strength(new_password).get("feedback", {})
	if not feedback.get("password_policy_validation_passed", False):
		frappe.throw(_("Password is too weak. {0}").format(" ".join(feedback.get("suggestions", []))))

	update_password(user=user, pwd=new_password, logout_all_sessions=False)


def has_password(user: str) -> bool:
	"""GitHub-only accounts have none. Passwords are hashed rows in `__Auth`
	with `encrypted = 0`, which `get_decrypted_password` never reads."""
	auth = frappe.qb.Table("__Auth")
	return bool(
		(
			frappe.qb.from_(auth)
			.select(auth.name)
			.where(
				(auth.doctype == "User")
				& (auth.name == user)
				& (auth.fieldname == "password")
				& (auth.encrypted == 0)
			)
			.limit(1)
		).run()
	)


@frappe.whitelist(methods=["POST"])
def connect_discuss(username: str) -> None:
	# TODO: replace with the Discourse User API Key flow so the username is verified.
	username = username.strip().lstrip("@")
	if not username:
		frappe.throw(_("Enter your Discuss username."))
	login = require_contributor()
	frappe.db.set_value("Contributor", login, "discuss_username", username)
	frappe.enqueue("community_platform.sync.discuss.sync_contributor", login=login, enqueue_after_commit=True)


@frappe.whitelist(methods=["POST"])
def disconnect_discuss() -> None:
	frappe.db.set_value("Contributor", require_contributor(), "discuss_username", None)


@frappe.whitelist(methods=["POST"])
def sync_github() -> None:
	login = require_contributor()
	frappe.enqueue(
		"community_platform.sync.github.sync_contributor",
		login=login,
		queue="long",
		job_id=f"github-sync-{login}",
		deduplicate=True,
		enqueue_after_commit=True,
	)
