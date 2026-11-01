// Day boundaries are IST everywhere: leaderboard months and heatmap days.
const IST = 'Asia/Kolkata'

export function todayIST() {
  return new Date().toLocaleDateString('en-CA', { timeZone: IST })
}

export function nowISO() {
  return new Date().toISOString()
}

export function addDays(isoDate, days) {
  const d = new Date(`${isoDate}T00:00:00Z`)
  d.setUTCDate(d.getUTCDate() + days)
  return d.toISOString().slice(0, 10)
}

export function dayOfWeek(isoDate) {
  return new Date(`${isoDate}T00:00:00Z`).getUTCDay()
}

export function formatDate(isoDate) {
  return new Date(`${isoDate.slice(0, 10)}T00:00:00Z`).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

export function formatMonth(month) {
  return new Date(`${month}-01T00:00:00Z`).toLocaleDateString('en-GB', {
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

export function timeAgo(iso) {
  const seconds = (Date.now() - new Date(iso).getTime()) / 1000
  const steps = [
    [60, 'second'],
    [60, 'minute'],
    [24, 'hour'],
    [30, 'day'],
    [12, 'month'],
    [Infinity, 'year'],
  ]
  let value = seconds
  for (const [size, unit] of steps) {
    if (Math.abs(value) < size) {
      const n = Math.max(1, Math.floor(value))
      return unit === 'second' ? 'just now' : `${n} ${unit}${n === 1 ? '' : 's'} ago`
    }
    value /= size
  }
}
