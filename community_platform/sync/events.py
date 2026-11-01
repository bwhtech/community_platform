"""Attendance and talks from events.frappe.io, matched by verified email.

The DocType and field names below are a best guess at the events app and
must be confirmed against the real site before enabling the sync.
"""

import frappe

from community_platform import points
from community_platform.sync.school import FrappeClient
from community_platform.utils import split_lines

ATTENDEE_DOCTYPE = "Event Ticket"  # fields: attendee_email, event, event_title, event_date
TALK_DOCTYPE = "Event Talk"  # fields: speaker_email, title, event, event_title, event_date


def sync_all():
	settings = frappe.get_cached_doc("Community Settings")
	if not settings.enable_events_sync or not settings.events_api_key:
		return
	client = FrappeClient(
		settings.events_url, settings.events_api_key, settings.get_password("events_api_secret")
	)
	base = settings.events_url.rstrip("/")

	for c in frappe.get_all(
		"Contributor", filters={"verified_emails": ["is", "set"]}, fields=["name", "verified_emails"]
	):
		emails = split_lines(c.verified_emails)
		for ticket in client.get_list(
			ATTENDEE_DOCTYPE,
			filters=[["attendee_email", "in", emails]],
			fields=["event", "event_title", "event_date"],
		):
			points.award(
				c.name,
				"event_attended",
				external_id=f"event:{ticket['event']}",
				title=ticket.get("event_title") or ticket["event"],
				url=f"{base}/{ticket['event']}",
				event_date=ticket["event_date"],
			)
		for talk in client.get_list(
			TALK_DOCTYPE,
			filters=[["speaker_email", "in", emails]],
			fields=["name", "title", "event", "event_title", "event_date"],
		):
			points.award(
				c.name,
				"event_talk",
				external_id=f"talk:{talk['name']}",
				title=f"{talk['title']} — {talk.get('event_title') or talk['event']}",
				url=f"{base}/{talk['event']}",
				event_date=talk["event_date"],
			)
		frappe.db.commit()
