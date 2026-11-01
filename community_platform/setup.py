"""Roles and starting data. Every step only adds what is missing, so admin
edits to rules, products and badges survive later migrations."""

import frappe

ROLES = ("Community Admin", "Community Moderator")

POINT_RULES = [
	("github_issue_opened", "Issue opened", "github", 5, 0),
	("github_pr_merged", "Pull request merged", "github", 20, 0),
	("github_pr_reviewed", "Pull request reviewed", "github", 5, 0),
	("discuss_solution", "Accepted solution on Discuss", "discuss", 10, 0),
	("event_attended", "Attended an event", "events", 10, 0),
	("event_talk", "Gave a talk", "events", 50, 0),
	("school_certification", "Certification earned", "school", 30, 0),
	("request_upvote_received", "Upvote on your feature request", "platform", 1, 50),
]

LOGO = "/assets/community_platform/logos/{}"

PRODUCTS = [
	(
		"frappe",
		"Frappe Framework",
		"frappe.svg",
		["frappe/frappe", "frappe/frappe-ui"],
		["Frappe Framework"],
		["Frappe Framework Developer"],
	),
	(
		"erpnext",
		"ERPNext",
		"erpnext.svg",
		["frappe/erpnext"],
		["ERPNext", "Accounting", "Manufacturing"],
		["ERPNext Functional Consultant", "ERPNext Manufacturing"],
	),
	("hrms", "Frappe HR", "hrms.svg", ["frappe/hrms"], ["Frappe HR"], ["Frappe HR Implementation"]),
	("crm", "Frappe CRM", "crm.svg", ["frappe/crm"], ["CRM"], []),
	("helpdesk", "Helpdesk", "helpdesk.svg", ["frappe/helpdesk"], ["Helpdesk"], []),
	("insights", "Insights", "insights.svg", ["frappe/insights"], ["Insights"], []),
	("lms", "Learning", "lms.png", ["frappe/lms"], ["Learning"], []),
	("gameplan", "Gameplan", "gameplan.svg", ["frappe/gameplan"], [], []),
	("drive", "Drive", "drive.svg", ["frappe/drive"], [], []),
]

BADGES = [
	(
		"First merge",
		"lucide-git-merge",
		"green",
		"Got a first pull request merged.",
		"action_count",
		"github_pr_merged",
		1,
		None,
	),
	(
		"Ten merges",
		"lucide-git-pull-request",
		"green",
		"Got 10 pull requests merged.",
		"action_count",
		"github_pr_merged",
		10,
		None,
	),
	(
		"Core contributor",
		"lucide-rocket",
		"violet",
		"Got 50 pull requests merged.",
		"action_count",
		"github_pr_merged",
		50,
		None,
	),
	("Bug hunter", "lucide-bug", "red", "Opened 25 issues.", "action_count", "github_issue_opened", 25, None),
	(
		"Reviewer",
		"lucide-eye",
		"blue",
		"Reviewed 10 pull requests that were merged.",
		"action_count",
		"github_pr_reviewed",
		10,
		None,
	),
	(
		"ERPNext builder",
		"lucide-boxes",
		"blue",
		"Got 10 pull requests merged in ERPNext.",
		"action_count",
		"github_pr_merged",
		10,
		"erpnext",
	),
	(
		"Discuss solver",
		"lucide-messages-square",
		"amber",
		"Had 10 answers accepted on Discuss.",
		"action_count",
		"discuss_solution",
		10,
		None,
	),
	(
		"Speaker",
		"lucide-mic",
		"violet",
		"Gave a talk at a Frappe event.",
		"action_count",
		"event_talk",
		1,
		None,
	),
	(
		"Regular",
		"lucide-ticket",
		"amber",
		"Attended 3 Frappe events.",
		"action_count",
		"event_attended",
		3,
		None,
	),
	(
		"Certified",
		"lucide-graduation-cap",
		"green",
		"Earned a certification on Frappe School.",
		"action_count",
		"school_certification",
		1,
		None,
	),
	("1,000 club", "lucide-gem", "violet", "Reached 1,000 points.", "points_total", None, 1000, None),
	(
		"Top 3 of the month",
		"lucide-trophy",
		"amber",
		"Finished in the top 3 of the monthly leaderboard.",
		"monthly_rank",
		None,
		3,
		None,
	),
	("Core team", "lucide-shield-check", "gray", "Member of the Frappe core team.", "manual", None, 0, None),
]


def before_migrate():
	create_roles()


def after_install():
	create_roles()
	create_defaults()


def after_migrate():
	create_defaults()


def create_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
				ignore_permissions=True
			)


def create_defaults():
	create_point_rules()
	create_products()
	create_badges()


def create_point_rules():
	for action, label, source, points, cap in POINT_RULES:
		if not frappe.db.exists("Point Rule", action):
			frappe.get_doc(
				{
					"doctype": "Point Rule",
					"action": action,
					"label": label,
					"source": source,
					"points": points,
					"cap_per_target": cap,
					"enabled": 1,
				}
			).insert(ignore_permissions=True)


def create_products():
	for index, (slug, name, logo, repos, categories, courses) in enumerate(PRODUCTS):
		if not frappe.db.exists("Product", slug):
			frappe.get_doc(
				{
					"doctype": "Product",
					"slug": slug,
					"product_name": name,
					"logo": LOGO.format(logo),
					"sort_order": index,
					"repos": "\n".join(repos),
					"discuss_categories": "\n".join(categories),
					"school_courses": "\n".join(courses),
				}
			).insert(ignore_permissions=True)


def create_badges():
	for title, icon, color, description, criteria, action, threshold, product in BADGES:
		if frappe.db.exists("Badge", {"title": title}):
			continue
		frappe.get_doc(
			{
				"doctype": "Badge",
				"title": title,
				"icon": icon,
				"color": color,
				"description": description,
				"criteria_type": criteria,
				"action": action,
				"threshold": threshold if criteria != "monthly_rank" else 0,
				"rank_limit": threshold if criteria == "monthly_rank" else 0,
				"product": product,
			}
		).insert(ignore_permissions=True)
