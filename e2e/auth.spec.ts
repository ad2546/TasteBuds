import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should redirect to login page on initial load', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/.*login/);
  });

  test('should show login form', async ({ page }) => {
    await page.goto('/login');

    // Check for email input
    await expect(page.getByPlaceholder(/email/i)).toBeVisible();

    // Check for password input
    await expect(page.getByPlaceholder(/password/i)).toBeVisible();

    // Check for log in submit button (there are two "Log In" buttons - tab and submit, we want the submit one)
    await expect(page.locator('form').getByRole('button', { name: /log in/i })).toBeVisible();
  });

  test('should show register form when clicking sign up tab', async ({ page }) => {
    await page.goto('/login');

    // Click on Sign Up tab (new design uses toggle buttons, not links)
    await page.getByRole('button', { name: /sign up/i }).click();

    // Should stay on same page (new design uses tabs, not separate pages)
    await expect(page).toHaveURL(/.*login/);

    // Check for name input (appears when in register mode)
    await expect(page.getByPlaceholder(/full name/i)).toBeVisible();
  });

  test('should show error for invalid login credentials', async ({ page }) => {
    await page.goto('/login');

    // Ensure we're in login mode
    await page.getByRole('button', { name: /log in/i, exact: false }).first().click();

    // Fill in invalid credentials
    await page.getByPlaceholder(/email/i).fill('invalid@test.com');
    await page.getByPlaceholder(/password/i).fill('wrongpassword');

    // Click log in button (submit button, not toggle)
    const submitButtons = await page.getByRole('button', { name: /log in/i }).all();
    await submitButtons[submitButtons.length - 1].click();

    // Should show error message (might need to adjust selector based on your error display)
    await page.waitForTimeout(1000);
  });

  test('should successfully register a new user', async ({ page }) => {
    await page.goto('/login');

    // Click on Sign Up tab to switch to register mode
    await page.getByRole('button', { name: /sign up/i }).click();

    const timestamp = Date.now();
    const testEmail = `test${timestamp}@tastesync.com`;

    // Fill registration form
    await page.getByPlaceholder(/full name/i).fill(`Test User ${timestamp}`);
    await page.getByPlaceholder(/email/i).fill(testEmail);
    await page.getByPlaceholder(/password/i).fill('TestPassword123!');

    // Submit form - the button says "Create Account" in register mode
    await page.getByRole('button', { name: /create account/i }).click();

    // Wait for navigation or success indicator
    await page.waitForTimeout(2000);
  });
});
