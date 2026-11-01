from datetime import datetime
from zoneinfo import ZoneInfo

# Day boundaries are IST everywhere: leaderboard months and heatmap days.
IST = ZoneInfo("Asia/Kolkata")


def today_ist() -> str:
	return datetime.now(IST).date().isoformat()


def to_ist_date(value: str | datetime) -> str:
	"""ISO timestamp from an external API (UTC or offset-aware) → IST date string."""
	if isinstance(value, str):
		value = datetime.fromisoformat(value.replace("Z", "+00:00"))
	if value.tzinfo is None:
		value = value.replace(tzinfo=ZoneInfo("UTC"))
	return value.astimezone(IST).date().isoformat()


def previous_month(month: str) -> str:
	year, mon = map(int, month.split("-"))
	return f"{year - 1}-12" if mon == 1 else f"{year}-{mon - 1:02d}"


def month_bounds(month: str) -> tuple[str, str]:
	"""First and last day of a YYYY-MM month as ISO dates."""
	year, mon = map(int, month.split("-"))
	next_year, next_mon = (year + 1, 1) if mon == 12 else (year, mon + 1)
	last = datetime(next_year, next_mon, 1).date().toordinal() - 1
	return f"{month}-01", datetime.fromordinal(last).date().isoformat()


def split_lines(text: str | None) -> list[str]:
	return [line.strip() for line in (text or "").splitlines() if line.strip()]
