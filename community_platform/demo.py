"""Demo community for local development: 38 fictional contributors, ~18 months
of activity, events, certifications and feature requests.

    bench --site community.localhost execute community_platform.demo.create_demo_data
    bench --site community.localhost execute community_platform.demo.delete_demo_data

Every contributor gets a website User that holds their name, avatar, bio and
location. The demo links `link_user` (Administrator by default) to the
contributor `rohan-mehta` instead, so "My profile" works without setting up
GitHub login. That User keeps its own name and only gains the fields it lacks.
"""

import random
from datetime import datetime, timedelta

import frappe
from frappe.utils import add_days, getdate

from community_platform.points import clear_total, evaluate, give_badge
from community_platform.utils import today_ist

ME = "rohan-mehta"
HISTORY_DAYS = 540
AVATAR = "/assets/community_platform/avatars/{}.jpg"
EMAIL = "{}@example.com"
DEMO_DOCTYPES = [
	"Feature Request Reaction",
	"Feature Request Vote",
	"Feature Request",
	"Contributor Badge",
	"Point Ledger",
	"Contributor",
]

PEOPLE = [
	("rohan-mehta", "Rohan Mehta", "Pune, India", "Self-employed", "dev"),
	("ananya-rao", "Ananya Rao", "Bengaluru, India", "Cloudnine Systems", "dev"),
	("vikram-desai", "Vikram Desai", "Mumbai, India", "Ledgerline", "dev"),
	("sara-okafor", "Sara Okafor", "Lagos, Nigeria", "Kora Digital", "dev"),
	("li-wei", "Li Wei", "Singapore", "Harbor ERP", "dev"),
	("priya-nair", "Priya Nair", "Kochi, India", "Backwater Labs", "functional"),
	("omar-haddad", "Omar Haddad", "Dubai, UAE", "Dune Consulting", "functional"),
	("meera-iyer", "Meera Iyer", "Chennai, India", "Saffron Tech", "dev"),
	("lukas-brandt", "Lukas Brandt", "Berlin, Germany", "Nordwerk GmbH", "dev"),
	("fatima-zahra", "Fatima Zahra", "Casablanca, Morocco", "Atlas ERP", "functional"),
	("arjun-kapoor", "Arjun Kapoor", "Delhi, India", "Northstar Apps", "dev"),
	("nisha-patel", "Nisha Patel", "Ahmedabad, India", "Kite Software", "functional"),
	("diego-ramos", "Diego Ramos", "Bogotá, Colombia", "Andes Cloud", "dev"),
	("kavya-reddy", "Kavya Reddy", "Hyderabad, India", "Pearl Analytics", "dev"),
	("tom-alvarez", "Tom Alvarez", "Austin, USA", "Lonestar Ops", "functional"),
	("aisha-khan", "Aisha Khan", "Karachi, Pakistan", "Indus Works", "dev"),
	("rahul-verma", "Rahul Verma", "Jaipur, India", "Pink City Tech", "dev"),
	("emma-larsen", "Emma Larsen", "Oslo, Norway", "Fjord Systems", "functional"),
	("siddharth-joshi", "Siddharth Joshi", "Nagpur, India", "Orange Grid", "dev"),
	("grace-mwangi", "Grace Mwangi", "Nairobi, Kenya", "Savanna Soft", "functional"),
	("karthik-s", "Karthik S", "Coimbatore, India", "Loom ERP", "dev"),
	("hana-sato", "Hana Sato", "Osaka, Japan", "Sakura Tech", "dev"),
	("neha-gupta", "Neha Gupta", "Lucknow, India", "Awadh Apps", "functional"),
	("marco-bianchi", "Marco Bianchi", "Milan, Italy", "Duomo Digital", "dev"),
	("ishaan-malhotra", "Ishaan Malhotra", "Chandigarh, India", "Sukhna Labs", "dev"),
	("zainab-ali", "Zainab Ali", "Riyadh, Saudi Arabia", "Najd Systems", "functional"),
	("pooja-shah", "Pooja Shah", "Surat, India", "Diamond ERP", "functional"),
	("ethan-cole", "Ethan Cole", "Toronto, Canada", "Maple Ops", "dev"),
	("divya-menon", "Divya Menon", "Thiruvananthapuram, India", "Coastline", "dev"),
	("yusuf-demir", "Yusuf Demir", "Istanbul, Türkiye", "Bosphorus Soft", "dev"),
	("tanvi-kulkarni", "Tanvi Kulkarni", "Nashik, India", "Vineyard Tech", "functional"),
	("ben-carter", "Ben Carter", "Manchester, UK", "Redbrick ERP", "dev"),
	("manish-yadav", "Manish Yadav", "Indore, India", "Malwa Systems", "dev"),
	("chloe-martin", "Chloe Martin", "Lyon, France", "Rhône Logiciel", "functional"),
	("aditya-bose", "Aditya Bose", "Kolkata, India", "Hooghly Tech", "dev"),
	("sneha-pillai", "Sneha Pillai", "Mysuru, India", "Palace Apps", "functional"),
	("jonas-weber", "Jonas Weber", "Zurich, Switzerland", "Alpen ERP", "dev"),
	("riya-chawla", "Riya Chawla", "Gurugram, India", "Cyber Hub Labs", "dev"),
]

EVENTS = [
	("fv-2025", "Frappeverse 2025", "Mumbai", "2025-12-06"),
	("meetup-blr-2026-02", "Frappe Meetup", "Bengaluru", "2026-02-21"),
	("meetup-pune-2026-04", "Frappe Meetup", "Pune", "2026-04-18"),
	("meetup-dubai-2026-05", "Frappe Meetup", "Dubai", "2026-05-23"),
	("meetup-delhi-2026-07", "Frappe Meetup", "Delhi", "2026-07-11"),
	("fv-2026", "Frappeverse 2026", "Bengaluru", "2026-09-12"),
	("meetup-chennai-2026-10", "Frappe Meetup", "Chennai", "2026-10-17"),
]

TALK_TITLES = [
	"Scaling ERPNext to 500 concurrent users",
	"Building a frappe-ui app in a weekend",
	"What we learned migrating 40 sites to v16",
	"Background jobs without tears",
	"Designing print formats people actually like",
	"Testing Frappe apps the boring way",
	"Selling open source ERP to manufacturers",
	"Query builder deep dive",
]

CERTIFICATIONS = [
	("Frappe Framework Developer", "frappe"),
	("ERPNext Functional Consultant", "erpnext"),
	("ERPNext Manufacturing", "erpnext"),
	("Frappe HR Implementation", "hrms"),
]

WORK_TITLES = {
	"frappe": [
		"fix: preserve filters when switching list views",
		"feat: add `frappe.qb` support for window functions",
		"fix: handle null in `get_value` with `as_dict`",
		"perf: cache doctype meta on first read",
		"fix: timezone drift in scheduler logs",
		"feat: keyboard shortcut to duplicate row in grid",
	],
	"erpnext": [
		"fix: rounding difference in Sales Invoice totals",
		"feat: allow partial reconciliation of payment entries",
		"fix: stock ledger reposting for backdated entries",
		"fix: BOM cost not updating on rate change",
		"feat: GST e-invoice cancellation reason",
		"fix: wrong exchange rate on multi-currency Journal Entry",
	],
	"hrms": [
		"fix: leave allocation overlapping with previous period",
		"feat: shift auto-attendance grace period per employee",
		"fix: salary slip with zero working days",
	],
	"crm": [
		"feat: kanban swimlanes by deal owner",
		"fix: email thread missing replies",
		"fix: duplicate lead on webform submit",
	],
	"helpdesk": [
		"fix: SLA pause on customer reply",
		"feat: canned responses with variables",
		"fix: agent assignment round robin skips",
	],
	"insights": [
		"feat: pivot table subtotals",
		"fix: date filter ignores timezone",
		"fix: chart legend overflow",
	],
	"lms": ["feat: quiz time limit", "fix: certificate PDF font", "fix: batch enrollment count"],
	"gameplan": ["fix: mention autocomplete in comments", "feat: pin discussions in space"],
	"drive": ["fix: upload progress stuck at 99%", "feat: share link expiry"],
	None: ["fix: bench update fails on detached HEAD", "feat: press site migration progress"],
}
UNMAPPED_REPOS = ["frappe/bench", "frappe/press"]

DISCUSS_TOPICS = [
	"How to set default warehouse per item group?",
	"Custom print format not picking letter head",
	"Payroll entry stuck in queued state",
	"Best way to import opening stock?",
	"Permission query conditions for child tables",
	"Webhook retries on failure",
	"Multi-company setup with shared customers",
	"Scheduler not running after migrate",
]

FEATURE_REQUESTS = [
	(
		"erpnext",
		"Bulk edit item prices from list view",
		"Updating prices for hundreds of items means opening each Item Price. A bulk edit dialog in the list view (like the one for Item) would save hours every quarter.",
	),
	(
		"erpnext",
		"Recurring journal entries",
		"Monthly accruals and depreciation adjustments are entered by hand. A schedule on Journal Entry that creates drafts each period would remove a lot of busy work.",
	),
	(
		"frappe",
		"Dark mode for print preview",
		"Print preview flashes bright white in dark mode. A dark canvas around the page (page itself stays white) would be easier on the eyes.",
	),
	(
		"frappe",
		"Saved filter sets shared with a role",
		"We set up the same filters for every user in Sales. Let us save a filter set and share it with a role.",
	),
	(
		"hrms",
		"Leave calendar view for managers",
		"Managers want a team calendar with who is on leave this week, without opening reports.",
	),
	(
		"crm",
		"WhatsApp templates inside CRM deal page",
		"Sales reps switch to another tool to send approved templates. Sending from the deal page would keep the timeline complete.",
	),
	(
		"helpdesk",
		"Customer satisfaction survey after resolve",
		"Send a one-question CSAT survey when a ticket is resolved, and show the score on the agent dashboard.",
	),
	(
		"insights",
		"Schedule a dashboard as PDF email",
		"Leadership wants the weekly dashboard in their inbox every Monday morning.",
	),
	(
		"lms",
		"Offline download for course videos",
		"Learners on slow connections want to download lessons and watch later.",
	),
	(
		"erpnext",
		"Barcode scanning in stock reconciliation",
		"Scanning items during stock take would make physical counts much faster.",
	),
	(
		"frappe",
		"Undo for accidental row delete in child table",
		"Deleting a row in a child table by mistake loses data until reload. A short undo toast would help.",
	),
	(
		"drive",
		"Folder level permissions inherited by subfolders",
		"Setting permissions on each subfolder is tedious. Inherit from parent by default.",
	),
	(
		"gameplan",
		"Weekly digest email for spaces",
		"A digest of new discussions in spaces I follow, once a week.",
	),
	(
		"erpnext",
		"Multi-level approval on Purchase Orders by amount",
		"Orders above a threshold should need a second approver without writing custom workflow code.",
	),
	(
		"hrms",
		"Expense claim from receipt photo",
		"Upload a photo of a receipt and pre-fill amount, date and vendor.",
	),
	(
		"frappe",
		"Command palette search inside child tables",
		"Jump to a row in a long child table by searching from the command palette.",
	),
]

DEV_MIX = [
	("github_issue_opened", 30),
	("github_pr_merged", 38),
	("github_pr_reviewed", 20),
	("discuss_solution", 12),
]
FUNCTIONAL_MIX = [("github_issue_opened", 35), ("discuss_solution", 65)]


def create_demo_data(link_user: str = "Administrator"):
	if frappe.db.exists("Contributor", ME):
		print("Demo data already exists. Run delete_demo_data first.")
		return
	seeder = Seeder(random.Random(42), today_ist())
	seeder.run(link_user)
	frappe.db.commit()
	print(f"Created {len(PEOPLE)} contributors and {seeder.ledger_count} ledger rows.")


def delete_demo_data():
	logins = [p[0] for p in PEOPLE]
	requests = frappe.get_all("Feature Request", {"contributor": ["in", logins]}, pluck="name")
	for doctype in DEMO_DOCTYPES:
		if doctype.startswith("Feature Request ") and requests:
			frappe.db.delete(doctype, {"feature_request": ["in", requests]})
		elif doctype == "Feature Request":
			frappe.db.delete(doctype, {"name": ["in", requests or [0]]})
		elif doctype == "Contributor":
			frappe.db.delete("Contributor Product", {"parent": ["in", logins], "parenttype": "Contributor"})
			frappe.db.delete(doctype, {"name": ["in", logins]})
		else:
			frappe.db.delete(doctype, {"contributor": ["in", logins]})
	for user in frappe.get_all(
		"User", {"name": ["in", [EMAIL.format(login) for login in logins]]}, pluck="name"
	):
		frappe.delete_doc("User", user, ignore_permissions=True, force=True)
	for login in logins:
		clear_total(login)
	frappe.db.commit()
	print("Demo data deleted.")


class Seeder:
	def __init__(self, rand: random.Random, today: str):
		self.rand = rand
		self.today = today
		self.rules = {r.name: r for r in frappe.get_all("Point Rule", fields=["name", "source", "points"])}
		self.products = {
			p.name: p.repos.splitlines() for p in frappe.get_all("Product", fields=["name", "repos"])
		}
		self.rows = []
		self.ledger_count = 0

	def run(self, link_user: str):
		focus = {}
		for index, person in enumerate(PEOPLE):
			focus[person[0]] = self.create_contributor(index, person, link_user)
		for login, _name, _loc, _company, kind in PEOPLE:
			self.seed_work(login, kind, focus[login])
		self.seed_events()
		self.seed_certifications()
		self.flush()
		self.seed_feature_requests()
		self.flush()
		for login, *_ in PEOPLE:
			clear_total(login)
			evaluate(login, self.today)
		self.seed_monthly_badges()
		give_badge("ananya-rao", self.badge("Core team"), "2025-06-01")
		give_badge("lukas-brandt", self.badge("Core team"), "2025-06-01")

	def create_contributor(self, index, person, link_user) -> list[str]:
		login, full_name, location, company, kind = person
		rand = self.rand
		first = full_name.split()[0].lower()
		products = rand.sample(list(self.products), 3 if kind == "dev" else 2)
		bio = (
			f"Building on Frappe since {2017 + rand.randrange(7)}. {rand.choice(['Mostly ERPNext.', 'Framework nerd.', 'frappe-ui fan.', 'Accounting edge cases are my thing.'])}"
			if kind == "dev"
			else f"{rand.choice(['ERPNext consultant', 'Implementation lead', 'Functional consultant'])} helping {rand.choice(['manufacturers', 'retailers', 'NGOs', 'distributors'])} go live."
		)
		user = self.create_user(login, full_name, bio, location, link_user if login == ME else None)
		frappe.get_doc(
			{
				"doctype": "Contributor",
				"github_login": login,
				"github_id": 100000 + index * 7919,
				"user": user,
				"company": company,
				"website": f"https://{login}.dev" if index % 3 == 0 else None,
				"x_handle": login.replace("-", "_") if index % 2 == 0 else None,
				"linkedin": login if index % 4 != 1 else None,
				"youtube": f"@{first}builds" if index % 9 == 0 else None,
				"products": [{"product": p} for p in products],
				"discuss_username": None if index % 5 == 3 else login.replace("-", "_"),
				"verified_emails": f"{first}@example.com",
				"joined_on": add_days(self.today, -rand.randrange(30, 430)),
			}
		).insert(ignore_permissions=True)
		return products

	def create_user(self, login, full_name, bio, location, link_user) -> str:
		profile = {"user_image": AVATAR.format(login), "bio": bio, "location": location}
		if link_user and frappe.db.exists("User", link_user):
			user = frappe.get_doc("User", link_user)
			user.update({field: user.get(field) or value for field, value in profile.items()})
			user.save(ignore_permissions=True)
			return user.name
		email = EMAIL.format(login)
		if frappe.db.exists("User", email):
			return email
		first_name, last_name = full_name.split(None, 1)
		frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
				"user_type": "Website User",
				"send_welcome_email": 0,
				**profile,
			}
		).insert(ignore_permissions=True)
		return email

	def seed_work(self, login, kind, focus):
		activity = 0.1 if login == ME else 0.03 + self.rand.random() ** 2 * 0.45
		mix = DEV_MIX if kind == "dev" else FUNCTIONAL_MIX
		for days_ago in range(HISTORY_DAYS, -1, -1):
			day = add_days(self.today, -days_ago)
			if self.rand.random() >= activity:
				continue
			for _ in range(1 + self.rand.randrange(3)):
				self.write_work(login, weighted(self.rand, mix), focus, str(day))

	def write_work(self, login, action, focus, day):
		rand = self.rand
		product = rand.choice(focus) if rand.random() < 0.85 else None
		repo = rand.choice(self.products[product]) if product else rand.choice(UNMAPPED_REPOS)
		number = rand.randrange(1000, 41000)
		if action == "discuss_solution":
			topic = rand.randrange(10000, 100000)
			self.add(
				login,
				action,
				f"discuss:{topic}",
				rand.choice(DISCUSS_TOPICS),
				f"https://discuss.frappe.io/t/{topic}",
				day,
				product,
			)
			return
		kind = "issues" if action == "github_issue_opened" else "pull"
		suffix = ":review" if action == "github_pr_reviewed" else ""
		row = self.add(
			login,
			action,
			f"{repo}#{number}{suffix}",
			rand.choice(WORK_TITLES[product]),
			f"https://github.com/{repo}/{kind}/{number}",
			day,
			product,
		)
		closed_on = str(add_days(day, 3))
		if action == "github_issue_opened" and rand.random() < 0.06 and closed_on <= self.today:
			self.add_revoke(row, "Issue closed as not planned", closed_on)

	def seed_events(self):
		for event_id, title, city, day in EVENTS:
			if day > self.today:
				continue
			conference = title.startswith("Frappeverse")
			label = f"{title} · {city}"
			for login, *_ in PEOPLE:
				if login != ME and self.rand.random() >= (0.45 if conference else 0.15):
					continue
				url = f"https://events.frappe.io/{event_id}"
				self.add(login, "event_attended", f"event:{event_id}", label, url, day)
				talks = (
					event_id == "meetup-pune-2026-04"
					if login == ME
					else self.rand.random() < (0.12 if conference else 0.08)
				)
				if talks:
					self.add(
						login,
						"event_talk",
						f"talk:{event_id}:{login}",
						f"{self.rand.choice(TALK_TITLES)} — {label}",
						url,
						day,
					)

	def seed_certifications(self):
		for login, *_ in PEOPLE:
			count = 2 if login == ME else (1 + self.rand.randrange(2) if self.rand.random() < 0.4 else 0)
			for title, product in self.rand.sample(CERTIFICATIONS, count):
				day = str(add_days(self.today, -self.rand.randrange(HISTORY_DAYS)))
				self.add(
					login,
					"school_certification",
					f"school:{title}:{login}",
					title,
					"https://school.frappe.io",
					day,
					product,
				)

	def seed_feature_requests(self):
		logins = [p[0] for p in PEOPLE]
		for index, (product, title, description) in enumerate(FEATURE_REQUESTS):
			owner = ME if index == 2 else self.rand.choice(logins)
			created = getdate(add_days(self.today, -self.rand.randrange(2, 202)))
			request = frappe.get_doc(
				{
					"doctype": "Feature Request",
					"title": title,
					"description": description,
					"product": product,
					"contributor": owner,
				}
			)
			request.insert(ignore_permissions=True)
			request.db_set(
				"creation",
				datetime.combine(created, datetime.min.time()) + timedelta(hours=10),
				update_modified=False,
			)
			others = [login for login in logins if login != owner]
			voters = [owner, *self.rand.sample(others, int(self.rand.random() ** 1.5 * 34))]
			for voter in voters:
				voted_on = (
					min(str(add_days(created, self.rand.randrange(30))), self.today)
					if voter != owner
					else str(created)
				)
				frappe.get_doc(
					{
						"doctype": "Feature Request Vote",
						"feature_request": request.name,
						"contributor": voter,
						"voted_on": voted_on,
					}
				).db_insert()
				if voter != owner:
					self.add(
						owner,
						"request_upvote_received",
						f"fr:{request.name}:{voter}",
						title,
						f"/requests/{request.name}",
						voted_on,
						cap_target=f"fr:{request.name}",
					)
			request.db_set("upvote_count", len(voters), update_modified=False)
			for reactor in self.rand.sample(logins, self.rand.randrange(10)):
				frappe.get_doc(
					{
						"doctype": "Feature Request Reaction",
						"feature_request": request.name,
						"contributor": reactor,
						"emoji": self.rand.choice(["❤️", "🎉", "🚀", "👀", "😕"]),
					}
				).db_insert()

	def seed_monthly_badges(self):
		from community_platform.points import award_monthly_rank_badges

		month = add_days(f"{self.today[:7]}-01", -HISTORY_DAYS)
		last = str(add_days(f"{self.today[:7]}-01", -1))[:7]
		current = str(month)[:7]
		while current <= last:
			award_monthly_rank_badges(current)
			year, mon = map(int, current.split("-"))
			current = f"{year + 1}-01" if mon == 12 else f"{year}-{mon + 1:02d}"

	def add(self, login, action, external_id, title, url, day, product=None, cap_target=None) -> dict:
		rule = self.rules[action]
		row = {
			"name": frappe.generate_hash(length=10),
			"contributor": login,
			"action": action,
			"source": rule.source,
			"points": rule.points,
			"product": product,
			"external_id": external_id,
			"cap_target": cap_target,
			"title": title,
			"url": url,
			"event_date": str(day),
			"is_revoke": 0,
			"revokes": None,
			"reason": None,
		}
		self.rows.append(row)
		return row

	def add_revoke(self, row, reason, day):
		self.rows.append(
			{
				**row,
				"name": frappe.generate_hash(length=10),
				"points": -row["points"],
				"event_date": day,
				"is_revoke": 1,
				"revokes": row["name"],
				"reason": reason,
			}
		)

	def flush(self):
		if not self.rows:
			return
		now = frappe.utils.now()
		fields = [
			"name",
			"creation",
			"modified",
			"owner",
			"modified_by",
			*[k for k in self.rows[0] if k != "name"],
		]
		values = [
			(row["name"], now, now, "Administrator", "Administrator", *[row[k] for k in fields[5:]])
			for row in self.rows
		]
		frappe.db.bulk_insert("Point Ledger", fields, values, chunk_size=2000)
		self.ledger_count += len(self.rows)
		self.rows = []

	def badge(self, title: str) -> str:
		return frappe.db.get_value("Badge", {"title": title})


def weighted(rand: random.Random, mix) -> str:
	return rand.choices([value for value, _ in mix], weights=[w for _, w in mix])[0]
