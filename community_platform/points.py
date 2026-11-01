"""The only write path into the Point Ledger, plus badge evaluation.

Rows are frozen when written: the points come from the rule at that moment and
later rule edits never touch them. A revoke is a new negative row that points
at the original. Badges are permanent once earned.
"""

import frappe
from frappe.query_builder.functions import Count, Sum
from frappe.utils import getdate

from community_platform.utils import today_ist

LEDGER = "Point Ledger"
TOTAL_CACHE_TTL = 10 * 60


def award(
	contributor: str,
	action: str,
	*,
	external_id: str,
	title: str,
	event_date,
	url: str | None = None,
	product: str | None = None,
	cap_target: str | None = None,
	evaluate_badges: bool = True,
) -> str | None:
	"""Write a ledger row unless the rule is off, it is a duplicate, or the cap is reached."""
	rule = frappe.db.get_value(
		"Point Rule", action, ["source", "points", "enabled", "cap_per_target"], as_dict=True
	)
	if not rule or not rule.enabled:
		return None
	if active_row(contributor, action, external_id):
		return None
	if rule.cap_per_target and cap_target and cap_used(action, cap_target) >= rule.cap_per_target:
		return None

	row = frappe.get_doc(
		{
			"doctype": LEDGER,
			"contributor": contributor,
			"action": action,
			"source": rule.source,
			"points": rule.points,
			"product": product,
			"external_id": external_id,
			"cap_target": cap_target,
			"title": (title or "")[:500],
			"url": url,
			"event_date": getdate(event_date),
		}
	).insert(ignore_permissions=True)

	if evaluate_badges:
		evaluate(contributor, row.event_date)
	return row.name


def revoke(row_name: str, reason: str, event_date=None) -> str | None:
	"""Add a negative row cancelling `row_name`. Returns None if already revoked."""
	row = frappe.get_doc(LEDGER, row_name)
	if row.is_revoke or is_revoked(row.name):
		return None
	revoke_row = frappe.get_doc(
		{
			"doctype": LEDGER,
			"contributor": row.contributor,
			"action": row.action,
			"source": row.source,
			"points": -row.points,
			"product": row.product,
			"external_id": row.external_id,
			"cap_target": row.cap_target,
			"title": row.title,
			"url": row.url,
			"event_date": getdate(event_date or today_ist()),
			"is_revoke": 1,
			"revokes": row.name,
			"reason": reason,
		}
	).insert(ignore_permissions=True)
	return revoke_row.name


def active_row(contributor: str, action: str, external_id: str) -> str | None:
	"""The positive row for this activity that has not been revoked, if any."""
	ledger = frappe.qb.DocType(LEDGER)
	revokes = frappe.qb.DocType(LEDGER).as_("r")
	rows = (
		frappe.qb.from_(ledger)
		.left_join(revokes)
		.on(revokes.revokes == ledger.name)
		.select(ledger.name)
		.where(
			(ledger.contributor == contributor)
			& (ledger.action == action)
			& (ledger.external_id == external_id)
			& (ledger.is_revoke == 0)
			& revokes.name.isnull()
		)
		.limit(1)
	).run()
	return rows[0][0] if rows else None


def is_revoked(row_name: str) -> bool:
	return bool(frappe.db.exists(LEDGER, {"revokes": row_name}))


def cap_used(action: str, cap_target: str) -> int:
	"""Net count of awards against one item: each award +1, each revoke -1."""
	positive = frappe.db.count(LEDGER, {"action": action, "cap_target": cap_target, "is_revoke": 0})
	negative = frappe.db.count(LEDGER, {"action": action, "cap_target": cap_target, "is_revoke": 1})
	return positive - negative


def cached_total(contributor: str) -> int:
	"""`total_for`, kept in Redis for a while. Every ledger write clears it."""
	key = total_cache_key(contributor)
	total = frappe.cache.get_value(key)
	if total is None:
		total = total_for(contributor)
		frappe.cache.set_value(key, total, expires_in_sec=TOTAL_CACHE_TTL)
	return total


def clear_total(contributor: str):
	frappe.cache.delete_value(total_cache_key(contributor))


def total_cache_key(contributor: str) -> str:
	return f"community_platform:total_points:{contributor}"


# -- Badges ---------------------------------------------------------------------


def evaluate(contributor: str, awarded_on=None):
	"""Award every count- or points-based badge the contributor now qualifies for."""
	earned = set(frappe.get_all("Contributor Badge", {"contributor": contributor}, pluck="badge"))
	badges = frappe.get_all(
		"Badge",
		filters={"criteria_type": ["in", ["action_count", "points_total"]]},
		fields=["name", "criteria_type", "action", "threshold", "product"],
	)
	pending = [b for b in badges if b.name not in earned]
	if not pending:
		return

	total = cached_total(contributor)
	counts = action_counts(contributor)
	for badge in pending:
		if qualifies(badge, total, counts):
			give_badge(contributor, badge.name, awarded_on or today_ist())


def qualifies(badge, total: int, counts: dict) -> bool:
	if badge.criteria_type == "points_total":
		return total >= (badge.threshold or 0)
	key = (badge.action, badge.product) if badge.product else (badge.action, None)
	return counts.get(key, 0) >= max(badge.threshold or 1, 1)


def action_counts(contributor: str) -> dict:
	"""{(action, product): n, (action, None): n} over kept (non-revoked) rows."""
	ledger = frappe.qb.DocType(LEDGER)
	revokes = frappe.qb.DocType(LEDGER).as_("r")
	rows = (
		frappe.qb.from_(ledger)
		.left_join(revokes)
		.on(revokes.revokes == ledger.name)
		.select(ledger.action, ledger.product, Count(ledger.name))
		.where((ledger.contributor == contributor) & (ledger.is_revoke == 0) & revokes.name.isnull())
		.groupby(ledger.action, ledger.product)
	).run()
	counts = {}
	for action, product, n in rows:
		counts[(action, product)] = n
		counts[(action, None)] = counts.get((action, None), 0) + n
	return counts


def give_badge(contributor: str, badge: str, awarded_on, period: str | None = None):
	frappe.get_doc(
		{
			"doctype": "Contributor Badge",
			"contributor": contributor,
			"badge": badge,
			"awarded_on": getdate(awarded_on),
			"period": period,
		}
	).insert(ignore_permissions=True)


def award_monthly_rank_badges(month: str):
	"""Runs on the 1st for the month before: top-N contributors get a dated badge."""
	from community_platform.ranking import rank_contributors

	for badge in frappe.get_all(
		"Badge", {"criteria_type": "monthly_rank"}, ["name", "rank_limit", "product"]
	):
		rows = rank_contributors(month=month, product=badge.product)
		for row in rows[: badge.rank_limit or 0]:
			if not frappe.db.exists(
				"Contributor Badge", {"contributor": row["login"], "badge": badge.name, "period": month}
			):
				give_badge(row["login"], badge.name, f"{month}-28", period=month)


def total_for(contributor: str) -> int:
	ledger = frappe.qb.DocType(LEDGER)
	result = frappe.qb.from_(ledger).select(Sum(ledger.points)).where(ledger.contributor == contributor).run()
	return int(result[0][0] or 0)
