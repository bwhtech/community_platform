import { expect, test } from "../support";

test.describe("Feature requests", () => {
	test.beforeEach(async ({ login }) => {
		await login();
	});

	test("contributor posts a request and finds it in the list", async ({ page, call }) => {
		const title = `Playwright request ${Date.now()}`;

		await page.goto("/requests");
		await page.getByRole("button", { name: "New request" }).first().click();

		const dialog = page.getByRole("dialog");
		await dialog.getByLabel("Title").fill(title);
		await dialog.getByLabel("Product").click();
		await page.getByRole("option", { name: "Frappe Framework" }).click();
		await dialog.locator(".ProseMirror").fill("Steps the test runner took to post this feature request.");
		await dialog.getByRole("button", { name: "Post request" }).click();

		await expect(page).toHaveURL(/\/requests\/\d+$/);
		const id = Number(page.url().split("/").pop());
		try {
			await expect(page.getByRole("heading", { name: title })).toBeVisible();
			// The author's own upvote is added on post.
			await expect(page.getByRole("button", { name: "Upvote, 1 votes" })).toBeVisible();

			await page.goto("/requests?sort=new");
			await expect(page.getByText(title)).toBeVisible();
		} finally {
			await call("community_platform.api.requests.delete_request", { id });
		}
	});

	test("short fields show validation errors", async ({ page }) => {
		await page.goto("/requests");
		await page.getByRole("button", { name: "New request" }).first().click();

		const dialog = page.getByRole("dialog");
		await dialog.getByLabel("Title").fill("Short");
		await dialog.getByRole("button", { name: "Post request" }).click();

		await expect(dialog.getByText("Write at least 8 characters.")).toBeVisible();
		await expect(dialog.getByText("Pick a product.")).toBeVisible();
		await expect(dialog.getByText("Write at least 20 characters.")).toBeVisible();
	});
});
