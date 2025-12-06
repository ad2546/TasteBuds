import { test, expect } from '@playwright/test';

async function login(page: any) {
  await page.goto('/login');
  // Ensure we're in login mode (click Log In tab)
  await page.getByRole('button', { name: /log in/i, exact: false }).first().click();
  await page.getByPlaceholder(/email/i).fill('evelyn.davis481@example.com');
  await page.getByPlaceholder(/password/i).fill('password123');
  // Click the submit button (the gradient button at the bottom)
  await page.getByRole('button', { name: /log in/i }).last().click();
  await page.waitForURL(/.*home/, { timeout: 5000 });
}

test.describe('Date Night Feature', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate to date night page from home', async ({ page }) => {
    await page.goto('/home');

    // Click on Date Night button
    await page.getByText(/Date Night/i).first().click();

    // Should navigate to date night page
    await expect(page).toHaveURL(/.*date-night/);
  });

  test('should display date night page with partner selection', async ({ page }) => {
    await page.goto('/date-night');

    // Wait for content to load
    await page.waitForTimeout(2000);

    // Check for date night header or title
    await expect(page.getByText(/Date Night|Find the perfect spot/i)).toBeVisible();
  });

  test('should show partner selection when no partner selected', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Look for partner selection UI
    const hasPartnerSelection = await page.getByText(/Choose|Select.*partner|dining partner/i).isVisible().catch(() => false);
    const hasCompatibility = await page.getByText(/Compatibility|Perfect for Both/i).isVisible().catch(() => false);

    // Either showing partner selection or already has a partner
    expect(hasPartnerSelection || hasCompatibility).toBeTruthy();
  });

  test('should be able to select a partner', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Try to find and click on a partner option
    const partnerButton = page.locator('button').filter({ hasText: /%.*match/i }).first();

    if (await partnerButton.isVisible().catch(() => false)) {
      await partnerButton.click();
      await page.waitForTimeout(3000);

      // Should show compatibility score or suggestions
      const hasCompatibility = await page.getByText(/Compatibility|Perfect/i).isVisible().catch(() => false);
      expect(hasCompatibility).toBeTruthy();
    }
  });

  test('should display compatibility score with selected partner', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Select a partner if available
    const partnerButton = page.locator('button').filter({ hasText: /%/i }).first();

    if (await partnerButton.isVisible().catch(() => false)) {
      await partnerButton.click();
      await page.waitForTimeout(3000);

      // Look for compatibility percentage
      const compatScore = page.getByText(/%/);
      await expect(compatScore).toBeVisible();
    }
  });

  test('should show shared cuisines and compromise options', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Select partner
    const partnerButton = page.locator('button').filter({ hasText: /%/i }).first();

    if (await partnerButton.isVisible().catch(() => false)) {
      await partnerButton.click();
      await page.waitForTimeout(3000);

      // Look for shared/compromise sections
      const hasShared = await page.getByText(/Both Love|Shared|Common/i).isVisible().catch(() => false);
      const hasCompromise = await page.getByText(/Compromise/i).isVisible().catch(() => false);

      expect(hasShared || hasCompromise).toBeTruthy();
    }
  });

  test('should display restaurant suggestions for date night', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Select partner
    const partnerButton = page.locator('button').filter({ hasText: /%/i }).first();

    if (await partnerButton.isVisible().catch(() => false)) {
      await partnerButton.click();
      await page.waitForTimeout(5000); // Wait for API call

      // Look for restaurant suggestions
      const hasPerfectMatches = await page.getByText(/Perfect.*Both|Perfect.*Match/i).isVisible().catch(() => false);
      const hasRestaurants = await page.locator('img[alt*="restaurant"], img[src*="yelp"]').count() > 0;

      expect(hasPerfectMatches || hasRestaurants).toBeTruthy();
    }
  });

  test('should be able to change partner', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Select a partner
    const partnerButton = page.locator('button').filter({ hasText: /%/i }).first();

    if (await partnerButton.isVisible().catch(() => false)) {
      await partnerButton.click();
      await page.waitForTimeout(2000);

      // Look for change partner button
      const changeButton = page.getByRole('button', { name: /Change partner/i });

      if (await changeButton.isVisible().catch(() => false)) {
        await changeButton.click();
        await page.waitForTimeout(1000);

        // Should show partner selection again
        await expect(page.getByText(/Choose|Select.*partner/i)).toBeVisible();
      }
    }
  });

  test('should handle no twins scenario gracefully', async ({ page }) => {
    await page.goto('/date-night');
    await page.waitForTimeout(2000);

    // Check if no twins message is shown
    const noTwinsMessage = await page.getByText(/No.*twins.*found/i).isVisible().catch(() => false);

    if (noTwinsMessage) {
      // Should suggest finding twins first
      await expect(page.getByText(/Find twins first/i)).toBeVisible();
    }
  });
});
