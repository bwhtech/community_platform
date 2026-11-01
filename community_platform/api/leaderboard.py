import frappe

from community_platform.api.common import current_contributor, people
from community_platform.ranking import month_breakdowns, rank_contributors
from community_platform.utils import month_bounds, previous_month, today_ist

LEADERBOARD_SIZE = 50


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_leaderboard(month: str) -> dict:
	rows = rank_contributors(month=month)
	previous_ranks = {r["login"]: r["rank"] for r in rank_contributors(month=previous_month(month))}
	breakdowns = month_breakdowns(month)
	me = current_contributor()
	my_index = next((i for i, r in enumerate(rows) if r["login"] == me), None)

	shown = rows[:LEADERBOARD_SIZE]
	extra = rows[max(my_index - 1, 0) : my_index + 1] if my_index is not None else []
	cards = people([r["login"] for r in shown + extra])

	def enrich(row):
		breakdown = breakdowns.get(row["login"], {})
		return {
			**row,
			**cards[row["login"]],
			"previousRank": previous_ranks.get(row["login"]),
			"bySource": breakdown.get("bySource", {}),
			"counts": breakdown.get("counts", {}),
		}

	return {
		"rows": [enrich(r) for r in shown],
		"me": (
			{**enrich(rows[my_index]), "ahead": enrich(rows[my_index - 1]) if my_index > 0 else None}
			if my_index is not None
			else None
		),
		"total": len(rows),
	}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_month_summary(month: str) -> dict:
	start, end = month_bounds(month)
	row = frappe.db.sql(
		"""
		select
			coalesce(sum(points), 0) as points,
			count(distinct case when is_revoke = 0 then contributor end) as contributors,
			sum(case when is_revoke = 0 and action = 'github_pr_merged' then 1 else 0 end) as prs_merged,
			sum(case when is_revoke = 0 and action = 'discuss_solution' then 1 else 0 end) as solutions
		from `tabPoint Ledger`
		where event_date between %s and %s
		""",
		(start, end),
		as_dict=True,
	)[0]
	return {
		"points": int(row.points or 0),
		"contributors": int(row.contributors or 0),
		"prsMerged": int(row.prs_merged or 0),
		"solutions": int(row.solutions or 0),
	}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_months(count: int = 12) -> list[str]:
	"""The last `count` months, newest first, as YYYY-MM."""
	months, month = [], today_ist()[:7]
	for _ in range(max(1, min(count, 36))):
		months.append(month)
		month = previous_month(month)
	return months
