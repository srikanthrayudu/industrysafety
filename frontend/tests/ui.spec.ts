import { test, expect } from '@playwright/test';

// Basic UI smoke test (Playwright will start the dev server via webServer in config)
test('dashboard loads and shows industrial safety console', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Smart Industrial Safety Monitoring and Emergency Response Simulator')).toBeVisible();
  await expect(page.getByText('Safety Sensor Status')).toBeVisible();
  await expect(page.getByText('Industrial Plant Control Network')).toBeVisible();
});
