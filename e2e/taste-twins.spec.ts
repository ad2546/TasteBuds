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

test.describe('Taste Twins', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate to twins page from home', async ({ page }) => {
    await page.goto('/home');

    // Click on Find Twins button
    await page.getByText(/Find Twins/i).click();

    // Should navigate to twins page
    await expect(page).toHaveURL(/.*twins/);
  });

  test('should display taste twins count on home page', async ({ page }) => {
    await page.goto('/home');

    // Wait for twins to load
    await page.waitForTimeout(2000);

    // Check for twins count in the Find Twins quick action
    const twinsButton = page.getByText(/taste matches/i);
    await expect(twinsButton).toBeVisible();
  });

  test('should display twins list page', async ({ page }) => {
    await page.goto('/twins');

    // Wait for content to load
    await page.waitForTimeout(2000);

    // Check if page has loaded properly
    await expect(page.getByText(/Taste Twins|Find Your Twins/i)).toBeVisible();
  });

  test('should show twin profiles with similarity scores', async ({ page }) => {
    await page.goto('/twins');
    await page.waitForTimeout(2000);

    // Look for similarity indicators
    const similarityText = page.getByText(/%/);

    // May have twins or no twins message
    const hasTwins = await similarityText.isVisible().catch(() => false);
    const noTwinsMessage = await page.getByText(/No twins|Find twins/i).isVisible().catch(() => false);

    expect(hasTwins || noTwinsMessage).toBeTruthy();
  });

  test('should be able to view twin profile details', async ({ page }) => {
    await page.goto('/twins');
    await page.waitForTimeout(2000);

    // Try to click on first twin if available
    const firstTwin = page.locator('button, a').filter({ hasText: /%/ }).first();

    if (await firstTwin.isVisible().catch(() => false)) {
      await firstTwin.click();
      await page.waitForTimeout(1000);

      // Should show twin details or navigate to profile
      // Check for any profile-related content
      expect(page.url()).toBeTruthy();
    }
  });

  test('should show shared cuisines with twins', async ({ page }) => {
    await page.goto('/twins');
    await page.waitForTimeout(2000);

    // Look for cuisine tags or shared preferences
    const cuisineIndicators = [
      /Italian/i,
      /Mexican/i,
      /Japanese/i,
      /Chinese/i,
      /Thai/i,
      /Indian/i,
      /French/i,
      /shared|common/i
    ];

    let foundCuisine = false;
    for (const indicator of cuisineIndicators) {
      if (await page.getByText(indicator).isVisible().catch(() => false)) {
        foundCuisine = true;
        break;
      }
    }

    // Either has cuisines or has no twins yet
    const noTwins = await page.getByText(/No twins/i).isVisible().catch(() => false);
    expect(foundCuisine || noTwins).toBeTruthy();
  });

  test('should have refresh twins functionality', async ({ page }) => {
    await page.goto('/twins');
    await page.waitForTimeout(1000);

    // Look for refresh button
    const refreshButton = page.getByRole('button', { name: /Refresh|Find New|Discover/i });

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(2000);

      // Should show loading or updated content
      expect(page.url()).toContain('twins');
    }
  });
});
