"""Certifications from Frappe School (the LMS app), matched by verified email."""

import frappe
import requests

from community_platform import points
from community_platform.api.common import products
from community_platform.utils import split_lines


def sync_all():
	settings = frappe.get_cached_doc("Community Settings")
	if not settings.enable_school_sync or not settings.school_api_key:
		return
	client = FrappeClient(
		settings.school_url, settings.school_api_key, settings.get_password("school_api_secret")
	)
	course_products = {course.lower(): p["id"] for p in products() for course in p["schoolCourses"]}

	for c in frappe.get_all(
		"Contributor", filters={"verified_emails": ["is", "set"]}, fields=["name", "verified_emails"]
	):
		for cert in client.get_list(
			"LMS Certificate",
			filters=[["member", "in", split_lines(c.verified_emails)]],
			fields=["name", "course_title", "issue_date"],
		):
			title = cert.get("course_title") or "Certification"
			points.award(
				c.name,
				"school_certification",
				external_id=f"school:{cert['name']}",
				title=title,
				url=f"{settings.school_url.rstrip('/')}/courses/certification/{cert['name']}",
				event_date=cert["issue_date"],
				product=course_products.get(title.lower()),
			)
		frappe.db.commit()


class FrappeClient:
	"""Just enough of the REST API to read a list with token auth."""

	def __init__(self, url: str, key: str, secret: str):
		self.url = url.rstrip("/")
		self.session = requests.Session()
		self.session.headers["Authorization"] = f"token {key}:{secret}"

	def get_list(self, doctype: str, filters: list, fields: list) -> list[dict]:
		response = self.session.get(
			f"{self.url}/api/resource/{doctype}",
			params={
				"filters": frappe.as_json(filters),
				"fields": frappe.as_json(fields),
				"limit_page_length": 0,
			},
			timeout=60,
		)
		response.raise_for_status()
		return response.json().get("data", [])
