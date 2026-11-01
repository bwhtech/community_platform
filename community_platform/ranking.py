"""Leaderboard maths over the Point Ledger."""

import frappe

from community_platform.utils import month_bounds


def rank_contributors(month: str | None = None, product: str | None = None) -> list[dict]:
	"""Contributors with positive points, best first. Ties go to whoever reached
	the score first, read as the earlier last-activity date."""
	conditions, values = [], {}
	if month:
		values["start"], values["end"] = month_bounds(month)
		conditions.append("event_date between %(start)s and %(end)s")
	if product:
		values["product"] = product
		conditions.append("product = %(product)s")
	where = f"where {' and '.join(conditions)}" if conditions else ""

	rows = frappe.db.sql(
		f"""
		select
			contributor as login,
			sum(points) as points,
			sum(case when is_revoke = 0 then 1 else 0 end) as contributions,
			max(event_date) as last_date
		from `tabPoint Ledger`
		{where}
		group by contributor
		having sum(points) > 0
		order by points desc, last_date asc
		""",
		values,
		as_dict=True,
	)
	for rank, row in enumerate(rows, start=1):
		row["rank"] = rank
		row["points"] = int(row["points"])
		row["contributions"] = int(row["contributions"])
	return rows


def month_breakdowns(month: str) -> dict[str, dict]:
	"""Points per source and counts per action, per contributor, for one month."""
	start, end = month_bounds(month)
	rows = frappe.db.sql(
		"""
		select contributor, source, action, is_revoke, sum(points) as points, count(*) as n
		from `tabPoint Ledger`
		where event_date between %s and %s
		group by contributor, source, action, is_revoke
		""",
		(start, end),
		as_dict=True,
	)
	out: dict[str, dict] = {}
	for row in rows:
		entry = out.setdefault(row.contributor, {"bySource": {}, "counts": {}})
		entry["bySource"][row.source] = entry["bySource"].get(row.source, 0) + int(row.points)
		if not row.is_revoke:
			entry["counts"][row.action] = entry["counts"].get(row.action, 0) + int(row.n)
	return out
