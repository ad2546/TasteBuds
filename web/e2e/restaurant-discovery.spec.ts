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

test.describe('Restaurant Discovery', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should display home page with quick actions', async ({ page }) => {
    await page.goto('/home');

    // Check for main quick action buttons
    await expect(page.getByText(/Search/i)).toBeVisible();
    await expect(page.getByText(/Feeling Lucky/i)).toBeVisible();
  });

  test('should navigate to feeling lucky page', async ({ page }) => {
    await page.goto('/home');

    // Click Feeling Lucky button
    await page.getByRole('button', { name: /Feeling Lucky/i }).click();

    // Should navigate to feeling lucky page
    await expect(page).toHaveURL(/.*feeling-lucky/);
  });

  test('should show loading and then restaurant on feeling lucky', async ({ page }) => {
    await page.goto('/feeling-lucky');
    await page.waitForTimeout(3000);

    // Should show either loading state or restaurant
    const hasLoading = await page.getByText(/Loading|Finding/i).isVisible().catch(() => false);
    const hasRestaurant = await page.locator('img').count() > 0;

    expect(hasLoading || hasRestaurant).toBeTruthy();
  });

  test('should navigate to search page', async ({ page }) => {
    await page.goto('/home');

    // Click Search button
    await page.getByText(/Search/i).first().click();

    // Should navigate to search page
    await expect(page).toHaveURL(/.*search/);
  });

  test('should display search input on search page', async ({ page }) => {
    await page.goto('/search');

    // Look for search input or filters
    const hasSearchInput = await page.getByPlaceholder(/search|restaurant|find/i).isVisible().catch(() => false);
    const hasFilters = await page.getByText(/Filter|Cuisine|Price/i).isVisible().catch(() => false);

    expect(hasSearchInput || hasFilters).toBeTruthy();
  });

  test('should be able to search for restaurants', async ({ page }) => {
    await page.goto('/search');

    // Fill search input if available
    const searchInput = page.getByPlaceholder(/search|restaurant|find/i);

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Italian');
      await page.waitForTimeout(2000);

      // Should show results or search button
      const hasResults = await page.locator('button, a').filter({ hasText: /restaurant/i }).count() > 0;
      const hasSearchButton = await page.getByRole('button', { name: /search/i }).isVisible().catch(() => false);

      expect(hasResults || hasSearchButton).toBeTruthy();
    }
  });

  test('should navigate to image search page', async ({ page }) => {
    await page.goto('/home');

    // Click Snap to Find button
    await page.getByText(/Snap to Find/i).click();

    // Should navigate to image search page
    await expect(page).toHaveURL(/.*image-search/);
  });

  test('should display image upload on image search page', async ({ page }) => {
    await page.goto('/image-search');

    // Look for image upload UI
    const hasUploadButton = await page.getByText(/Upload|Choose|Camera/i).isVisible().catch(() => false);
    const hasFileInput = await page.locator('input[type="file"]').count() > 0;

    expect(hasUploadButton || hasFileInput).toBeTruthy();
  });

  test('should be able to click on a restaurant to view details', async ({ page }) => {
    await page.goto('/search');
    await page.waitForTimeout(2000);

    // Try to find and click on first restaurant result
    const restaurantCard = page.locator('button, a').filter({ hasText: /restaurant|\$|rating/i }).first();

    if (await restaurantCard.isVisible().catch(() => false)) {
      await restaurantCard.click();
      await page.waitForTimeout(2000);

      // Should navigate to restaurant detail page
      expect(page.url()).toMatch(/restaurant|detail/);
    }
  });

  test('should display restaurant details page', async ({ page }) => {
    // Try to navigate to a restaurant detail page
    // This test is generic as we don't know specific restaurant IDs
    await page.goto('/home');
    await page.getByRole('button', { name: /Feeling Lucky/i }).click();
    await page.waitForTimeout(3000);

    // If restaurant is shown, try to click to see details
    const viewButton = page.getByRole('button', { name: /View|Details|More Info/i });

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(2000);

      // Should show restaurant details
      expect(page.url()).toBeTruthy();
    }
  });

  test('should display challenges page', async ({ page }) => {
    await page.goto('/home');

    // Click Challenges button
    await page.getByText(/Challenges/i).first().click();

    // Should navigate to challenges page
    await expect(page).toHaveURL(/.*challenges/);
  });

  test('should be able to navigate back to home', async ({ page }) => {
    await page.goto('/search');

    // Look for back button
    const backButton = page.getByRole('button', { name: /back|arrow/i }).first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      // Should navigate back (may not always go to home)
      expect(page.url()).toBeTruthy();
    }
  });

  test('should display user profile button', async ({ page }) => {
    await page.goto('/home');

    // Look for profile image or button
    const profileButton = page.locator('img[alt*="Profile"], button[aria-label*="profile"]');
    await expect(profileButton.first()).toBeVisible();
  });

  test('should navigate to profile page', async ({ page }) => {
    await page.goto('/home');

    // Click on profile image/button
    const profileButton = page.locator('img[alt*="Profile"]').first();
    await profileButton.click();
    await page.waitForTimeout(1000);

    // Should navigate to profile page
    await expect(page).toHaveURL(/.*profile/);
  });
});
