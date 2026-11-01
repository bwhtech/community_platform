import { test as base, expect } from "@playwright/test";

// Demo data links Administrator to the contributor `rohan-mehta`, so this
// user can post and vote like any GitHub-linked member, and is also an admin.
export const ADMIN = "Administrator";
export const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "admin";
export const ADMIN_LOGIN = "rohan-mehta";

export const test = base.extend({
	// Pages start as Guest. Specs that need a session call `login()` first.
	login: async ({ page }, use) => {
		await use(async () => {
			const res = await page.request.post("/api/method/login", {
				data: { usr: ADMIN, pwd: ADMIN_PASSWORD },
			});
			expect(res.status(), `login: ${await res.text()}`).toBe(200);
		});
	},

	// Calls a whitelisted method with the page's session and CSRF token.
	// The page must be on an SPA route, which is where the token comes from.
	call: async ({ page }, use) => {
		await use(async (method, args = {}) => {
			const token = await page.evaluate(() => window.csrf_token);
			const res = await page.request.post(`/api/method/${method}`, {
				data: args,
				headers: { "X-Frappe-CSRF-Token": token },
			});
			expect(res.status(), `${method}: ${await res.text()}`).toBe(200);
			return (await res.json()).message;
		});
	},
});

export { expect };
