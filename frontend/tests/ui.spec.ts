import { test, expect } from '@playwright/test';

// Basic UI smoke test (Playwright will start the dev server via webServer in config)
test('dashboard loads and shows NetworkMap', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('SCADA Monitoring Interface')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start Simulation' })).toBeVisible();
  await page.getByRole('button', { name: 'Start Simulation' }).click();
  await expect(page.getByText('Monitored Flow: A to E')).toBeVisible();
});
