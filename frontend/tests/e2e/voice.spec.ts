import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test, type Page } from "@playwright/test";

const e2eRoot = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(e2eRoot, "..", "..");
const passwordPath = path.join(
  frontendRoot,
  "test-results",
  "gate-b",
  "e2e-password.txt",
);

async function login(page: Page, email: string) {
  const password = readFileSync(passwordPath, "utf8").trim();
  await page.goto("/");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("Longitudinal timeline")).toBeVisible();
  await expect(page.locator("#patient-select")).toHaveValue(/.+/);
}

test.describe.configure({ mode: "serial" });

test("Voice fixture clinical flow exposes segments and source navigation", async ({
  page,
}) => {
  await login(page, "clinician.a@clinic-a.test");
  const voice = page.getByTestId("voice-panel");
  await expect(voice).toBeVisible();
  await expect(voice).toContainText("Mock transcript fixture");
  await expect(voice).toContainText("Synthetic nurse follow-up");
  await expect(voice.getByTestId("voice-audio")).toBeVisible();
  await voice.getByRole("button", { name: "Process sample" }).click();
  const result = page.getByTestId("voice-session-result");
  await expect(result).toContainText("Voice session status: completed");
  await expect(result.getByTestId("voice-segment-0")).toContainText(
    "This is a synthetic nurse follow-up",
  );
  const audio = voice.getByTestId("voice-audio");
  await result.getByTestId("voice-segment-1").click();
  await expect
    .poll(() =>
      audio.evaluate((element) => (element as HTMLAudioElement).currentTime),
    )
    .toBeGreaterThanOrEqual(8);
  await result.getByRole("button", { name: "Open generated source" }).click();
  await expect(
    page.getByRole("region", { name: "Immutable source" }),
  ).toBeVisible();
});

test("Voice fixture patient flow exposes only the patient sample", async ({
  page,
}) => {
  await login(page, "sarah.patient@clinic-a.test");
  const voice = page.getByTestId("voice-panel");
  await expect(voice).toBeVisible();
  await expect(voice).toContainText("Mock transcript fixture");
  await expect(voice).toContainText("Synthetic patient follow-up");
  await expect(voice).not.toContainText("Synthetic nurse follow-up");
  await expect(voice.getByTestId("voice-audio")).toBeVisible();
  await expect(voice.getByRole("button", { name: /microphone/i })).toHaveCount(
    0,
  );
  await voice.getByRole("button", { name: "Process sample" }).click();
  await expect(page.getByTestId("voice-session-result")).toContainText(
    "Voice session status: completed",
  );
  await expect(
    page.getByTestId("voice-session-result").getByRole("button", {
      name: "Open generated source",
    }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Documented symptom after dose change"),
  ).toHaveCount(0);
});
