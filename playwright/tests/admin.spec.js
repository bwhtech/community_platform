import { expect, test } from "../support";

test.describe("Admin", () => {
	test.beforeEach(async ({ login }) => {
		await login();
	});

	test("admin opens point rules from the sidebar", async ({ page }) => {
		await page.goto("/leaderboard");
		await page.getByRole("link", { name: "Point rules" }).click();
		await expect(page).toHaveURL(/\/admin\/point-rules$/);
		await expect(page.getByText("Pull request merged")).toBeVisible();
	});
});
