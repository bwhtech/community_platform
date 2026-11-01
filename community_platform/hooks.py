app_name = "community_platform"
app_title = "Community Platform"
app_publisher = "BWH"
app_description = "Frappeverse Community Platform"
app_email = "developers@bwh.tech"
app_license = "mit"

# Send non-GET requests for this app's endpoints as native `application/json`
# bodies instead of form-encoded, per-key JSON-stringified values.
use_json_request_body = True

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "community_platform",
# 		"logo": "/assets/community_platform/logo.png",
# 		"title": "Community Platform",
# 		"route": "/community_platform",
# 		"has_permission": "community_platform.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `community_platform/dock/community_platform/community_platform.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/community_platform/css/community_platform.css"
# app_include_js = "/assets/community_platform/js/community_platform.js"

# include js, css files in header of web template
# web_include_css = "/assets/community_platform/css/community_platform.css"
# web_include_js = "/assets/community_platform/js/community_platform.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "community_platform/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "community_platform/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Setup Wizard
# ------------

# open a fresh site's setup in this app's own UI instead of the desk wizard.
# must be a non-desk route (not under /desk or /app); to customize setup within
# desk, use setup_wizard_stages / setup_wizard_complete instead.
# setup_wizard_url = "/community_platform/setup"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "community_platform.utils.jinja_methods",
# 	"filters": "community_platform.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "community_platform.install.before_install"
# after_install = "community_platform.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "community_platform.uninstall.before_uninstall"
# after_uninstall = "community_platform.uninstall.after_uninstall"

# Disable / Enable
# ----------------
# Called when this app is logically disabled or re-enabled on a site,
# without uninstalling it. Use this to hide/restore fields this app adds
# to other apps' doctypes.

# before_disable = "community_platform.uninstall.before_disable"
# after_disable = "community_platform.uninstall.after_disable"
# before_enable = "community_platform.install.before_enable"
# after_enable = "community_platform.install.after_enable"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "community_platform.utils.before_app_install"
# after_app_install = "community_platform.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "community_platform.utils.before_app_uninstall"
# after_app_uninstall = "community_platform.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "community_platform.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "community_platform.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "community_platform.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["community_platform.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"community_platform.tasks.all"
# 	],
# 	"daily": [
# 		"community_platform.tasks.daily"
# 	],
# 	"hourly": [
# 		"community_platform.tasks.hourly"
# 	],
# 	"weekly": [
# 		"community_platform.tasks.weekly"
# 	],
# 	"monthly": [
# 		"community_platform.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "community_platform.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "community_platform.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "community_platform.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "community_platform.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["community_platform.utils.before_request"]
# after_request = ["community_platform.utils.after_request"]

# Job Events
# ----------
# before_job = ["community_platform.utils.before_job"]
# after_job = ["community_platform.utils.after_job"]

# after_file_upload = ["community_platform.utils.after_file_upload"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"community_platform.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


# Community Platform
# ------------------

before_migrate = "community_platform.setup.before_migrate"
after_migrate = "community_platform.setup.after_migrate"
after_install = "community_platform.setup.after_install"

on_session_creation = "community_platform.auth.on_session_creation"

# The SPA lives at the site root. Each top-level route it owns renders
# www/community.html; Frappe keeps /app, /login, /api and /assets.
home_page = "community"
website_route_rules = [
	{"from_route": "/leaderboard", "to_route": "community"},
	{"from_route": "/u/<path:login>", "to_route": "community"},
	{"from_route": "/requests", "to_route": "community"},
	{"from_route": "/requests/<path:id>", "to_route": "community"},
	{"from_route": "/badges", "to_route": "community"},
	{"from_route": "/me", "to_route": "community"},
	{"from_route": "/join", "to_route": "community"},
	{"from_route": "/admin/<path:page>", "to_route": "community"},
]

scheduler_events = {
	"hourly_long": ["community_platform.sync.github.sync_all"],
	"daily_long": [
		"community_platform.sync.discuss.sync_all",
		"community_platform.sync.school.sync_all",
		"community_platform.sync.events.sync_all",
	],
	"daily": ["community_platform.tasks.award_last_month_badges"],
}
