import frappe

from community_platform.points import award_monthly_rank_badges
from community_platform.utils import previous_month, today_ist


def award_last_month_badges():
	"""Runs daily; only acts on the 1st (IST) for the month that just ended."""
	today = today_ist()
	if not today.endswith("-01"):
		return
	award_monthly_rank_badges(previous_month(today[:7]))
	frappe.db.commit()
