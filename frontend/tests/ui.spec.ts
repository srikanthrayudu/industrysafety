import { test, expect } from '@playwright/test';

// Basic UI smoke test (Playwright will start the dev server via webServer in config)
test('dashboard loads and shows NetworkMap', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Industrial Network Reliability Simulator')).toBeVisible();
  await expect(page.locator('svg.network-map')).toBeVisible();
});
