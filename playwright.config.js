const path = require("path");
const { defineConfig } = require("@playwright/test");

const ci = Boolean(process.env.CI);

// Run with `bench --site <site> run-ui-tests community_platform --headless`.
// Bench sets BASE_URL to the site and ADMIN_PASSWORD from its config.
module.exports = defineConfig({
	testDir: "./playwright/tests",
	// Bench runs Playwright from frappe's node_modules, so pin outputs to this app.
	outputDir: path.join(__dirname, "test-results"),
	fullyParallel: false,
	workers: 1,
	forbidOnly: ci,
	retries: ci ? 1 : 0,
	timeout: 60000,
	expect: { timeout: 15000 },
	reporter: ci ? [["list"], ["github"], ["html", { open: "never", outputFolder: path.join(__dirname, "playwright-report") }]] : [["list"]],
	use: {
		baseURL: process.env.BASE_URL || "http://community.localhost:8001",
		viewport: { width: 1400, height: 960 },
		actionTimeout: 15000,
		navigationTimeout: 30000,
		trace: "on-first-retry",
		screenshot: "only-on-failure",
	},
});
