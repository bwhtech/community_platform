import { expect, test } from "../support";

test.describe("Guest browsing", () => {
	test("home redirects to the leaderboard", async ({ page }) => {
		await page.goto("/");
		await expect(page).toHaveURL(/\/leaderboard$/);
		await expect(page.getByRole("button", { name: "Log in with GitHub" })).toBeVisible();
	});

	test("leaderboard links to a contributor profile", async ({ page }) => {
		// Demo data fills last month; the current one can still be empty.
		await page.goto(`/leaderboard?month=${lastMonth()}`);
		const row = page.locator('a[href^="/u/"]').first();
		const href = await row.getAttribute("href");
		await row.click();
		await expect(page).toHaveURL(new RegExp(`${href}$`));
	});

	test("posting a request asks a guest to log in", async ({ page }) => {
		await page.goto("/requests");
		await page.getByRole("button", { name: "New request" }).first().click();
		await expect(page).toHaveURL(/\/join\?redirect=/);
		await expect(page.getByRole("heading", { name: "Join the Frappe community" })).toBeVisible();
	});

	test("admin pages send a guest back to the leaderboard", async ({ page }) => {
		await page.goto("/admin/point-rules");
		await expect(page).toHaveURL(/\/leaderboard$/);
	});
});

function lastMonth() {
	const now = new Date();
	return new Date(Date.UTC(now.getFullYear(), now.getMonth() - 1, 1)).toISOString().slice(0, 7);
}
