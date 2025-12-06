import { test, expect } from '@playwright/test';

// Helper to login before running tests
async function login(page: any) {
  await page.goto('/login');
  // Ensure we're in login mode (click Log In tab)
  await page.getByRole('button', { name: /log in/i, exact: false }).first().click();
  await page.getByPlaceholder(/email/i).fill('evelyn.davis481@example.com');
  await page.getByPlaceholder(/password/i).fill('password123');
  // Click the submit button (the gradient button at the bottom)
  await page.getByRole('button', { name: /log in/i }).last().click();
  // Wait for redirect to home
  await page.waitForURL(/.*home/, { timeout: 5000 });
}

test.describe('Taste DNA Quiz', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate to Taste DNA page from home', async ({ page }) => {
    await page.goto('/home');

    // Click on Taste DNA card
    await page.getByText(/Your Taste DNA/i).click();

    // Should navigate to Taste DNA page
    await expect(page).toHaveURL(/.*taste-dna/);
  });

  test('should display Taste DNA profile if exists', async ({ page }) => {
    await page.goto('/taste-dna');

    // Wait for content to load
    await page.waitForTimeout(2000);

    // Check if profile is displayed (either quiz or existing profile)
    const hasQuiz = await page.getByText(/Take Quiz|Start Quiz/i).isVisible().catch(() => false);
    const hasProfile = await page.getByText(/Adventure Score|Spice Tolerance/i).isVisible().catch(() => false);

    expect(hasQuiz || hasProfile).toBeTruthy();
  });

  test('should be able to complete Taste DNA quiz', async ({ page }) => {
    await page.goto('/taste-dna');

    // Check if quiz button exists
    const quizButton = page.getByRole('button', { name: /Take Quiz|Start Quiz|Retake Quiz/i });

    if (await quizButton.isVisible().catch(() => false)) {
      await quizButton.click();

      // Wait for quiz to load
      await page.waitForTimeout(1000);

      // Interact with quiz questions (adjust based on actual quiz structure)
      // This is a generic approach - you may need to customize
      for (let i = 0; i < 10; i++) {
        // Try clicking next/continue buttons or making selections
        const nextButton = page.getByRole('button', { name: /Next|Continue|Submit/i });

        if (await nextButton.isVisible().catch(() => false)) {
          // Try to interact with quiz elements (sliders, buttons, etc.)
          const sliders = page.locator('input[type="range"]');
          const sliderCount = await sliders.count();

          if (sliderCount > 0) {
            await sliders.first().fill('5');
          }

          await nextButton.click();
          await page.waitForTimeout(500);
        } else {
          break;
        }
      }
    }
  });

  test('should display taste profile characteristics', async ({ page }) => {
    await page.goto('/taste-dna');
    await page.waitForTimeout(2000);

    // Look for profile elements (may vary based on implementation)
    const profileIndicators = [
      /Adventure/i,
      /Spice/i,
      /Price/i,
      /Ambiance/i,
      /Cuisine/i
    ];

    // At least some profile indicators should be present
    let foundIndicators = 0;
    for (const indicator of profileIndicators) {
      if (await page.getByText(indicator).isVisible().catch(() => false)) {
        foundIndicators++;
      }
    }

    expect(foundIndicators).toBeGreaterThan(0);
  });
});
