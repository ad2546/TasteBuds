import { Page } from '@playwright/test';

/**
 * Login helper for E2E tests
 */
export async function login(page: Page, email = 'test@tastesync.com', password = 'TestPassword123!') {
  await page.goto('/login');
  await page.getByPlaceholder(/email/i).fill(email);
  await page.getByPlaceholder(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in/i }).click();

  try {
    await page.waitForURL(/.*home/, { timeout: 5000 });
  } catch (error) {
    console.log('Login may have failed or redirected elsewhere');
  }
}

/**
 * Create a test user for E2E tests
 */
export async function createTestUser(page: Page) {
  const timestamp = Date.now();
  const testEmail = `test${timestamp}@tastesync.com`;
  const testPassword = 'TestPassword123!';
  const testName = `Test User ${timestamp}`;

  await page.goto('/register');
  await page.getByPlaceholder(/name/i).fill(testName);
  await page.getByPlaceholder(/email/i).fill(testEmail);
  await page.getByPlaceholder(/password/i).first().fill(testPassword);
  await page.getByRole('button', { name: /sign up|register/i }).click();

  await page.waitForTimeout(2000);

  return { email: testEmail, password: testPassword, name: testName };
}

/**
 * Wait for API call to complete
 */
export async function waitForApiResponse(page: Page, urlPattern: string | RegExp, timeout = 10000) {
  try {
    await page.waitForResponse(
      (response) => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        }
        return urlPattern.test(url);
      },
      { timeout }
    );
  } catch (error) {
    console.log(`API response for ${urlPattern} not received within timeout`);
  }
}

/**
 * Check if element is visible with timeout
 */
export async function isVisible(page: Page, selector: string, timeout = 3000): Promise<boolean> {
  try {
    await page.locator(selector).waitFor({ state: 'visible', timeout });
    return true;
  } catch {
    return false;
  }
}

/**
 * Logout helper
 */
export async function logout(page: Page) {
  const logoutButton = page.getByRole('button', { name: /logout|sign out/i });
  if (await logoutButton.isVisible().catch(() => false)) {
    await logoutButton.click();
    await page.waitForTimeout(1000);
  }
}
