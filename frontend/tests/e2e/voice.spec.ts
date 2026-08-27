import { mkdirSync, readFileSync } from "node:fs";
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
const screenshotRoot = path.resolve(frontendRoot, "..", "artifacts", "gate-b");

function screenshotPath(projectName: string, filename: string) {
  mkdirSync(screenshotRoot, { recursive: true });
  return path.join(screenshotRoot, projectName + "-" + filename);
}

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

test("Voice note clinical flow exposes segments and source navigation", async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  const errorResponses: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("response", (response) => {
    if (response.status() >= 400) {
      errorResponses.push(
        response.status() + " " + new URL(response.url()).pathname,
      );
    }
  });
  const audioResponsePromise = page.waitForResponse((response) => {
    const pathname = new URL(response.url()).pathname;
    return (
      response.request().method() === "GET" &&
      /\/voice\/samples\/[^/]+\/audio$/.test(pathname)
    );
  });
  await login(page, "clinician.a@clinic-a.test");
  const audioResponse = await audioResponsePromise;
  consoleErrors.length = 0;
  errorResponses.length = 0;
  expect(audioResponse.status()).toBe(200);
  expect(audioResponse.headers()["content-type"]).toMatch(/^audio\/wav/);
  expect(new URL(audioResponse.url()).port).toBe("8000");
  const voice = page.getByTestId("voice-panel");
  await expect(voice).toBeVisible();
  await expect(voice).toContainText("Review a pre-recorded care conversation");
  await expect(voice).toContainText("nurse follow-up");
  await expect(voice).not.toContainText("mock-transcript-fixture");
  const audio = voice.getByTestId("voice-audio");
  await expect(audio).toBeVisible();
  await expect(audio).toHaveAttribute("data-audio-state", "ready");
  const audioMetadata = await audio.evaluate((element) => ({
    readyState: (element as HTMLAudioElement).readyState,
    duration: (element as HTMLAudioElement).duration,
    src: (element as HTMLAudioElement).src,
  }));
  expect(audioMetadata.readyState).toBeGreaterThanOrEqual(1);
  expect(audioMetadata.duration).toBeGreaterThan(0);
  expect(audioMetadata.src).toMatch(/^blob:/);
  await voice
    .getByRole("button", { name: "Create care-note suggestion" })
    .click();
  const result = page.getByTestId("voice-session-result");
  await expect(result).toContainText("Suggestion status: Ready for review");
  await expect(result.getByTestId("voice-segment-0")).toContainText(
    "This is a synthetic nurse follow-up",
  );
  await page.screenshot({
    path: screenshotPath(test.info().project.name, "voice-clinical.png"),
    fullPage: false,
  });
  await audio.click();
  await audio.evaluate(async (element) => {
    await (element as HTMLAudioElement).play();
  });
  await expect
    .poll(() =>
      audio.evaluate((element) => (element as HTMLAudioElement).currentTime),
    )
    .toBeGreaterThan(0);
  await audio.evaluate((element) => (element as HTMLAudioElement).pause());
  await result.getByTestId("voice-segment-1").click();
  await expect
    .poll(() =>
      audio.evaluate((element) => (element as HTMLAudioElement).currentTime),
    )
    .toBeGreaterThanOrEqual(8);
  await result.getByRole("button", { name: "View source" }).click();
  await expect(
    page.getByRole("region", { name: "Original source", exact: true }),
  ).toBeVisible();
  await expect(audio).toHaveJSProperty("error", null);
  expect({ consoleErrors, errorResponses }).toEqual({
    consoleErrors: [],
    errorResponses: [],
  });
});

test("Voice note patient flow exposes only the patient sample", async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  const errorResponses: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("response", (response) => {
    if (response.status() >= 400) {
      errorResponses.push(
        response.status() + " " + new URL(response.url()).pathname,
      );
    }
  });
  const audioResponsePromise = page.waitForResponse((response) => {
    const pathname = new URL(response.url()).pathname;
    return (
      response.request().method() === "GET" &&
      /\/voice\/samples\/[^/]+\/audio$/.test(pathname)
    );
  });
  await login(page, "sarah.patient@clinic-a.test");
  const audioResponse = await audioResponsePromise;
  consoleErrors.length = 0;
  errorResponses.length = 0;
  expect(audioResponse.status()).toBe(200);
  expect(audioResponse.headers()["content-type"]).toMatch(/^audio\/wav/);
  expect(new URL(audioResponse.url()).port).toBe("8000");
  const voice = page.getByTestId("voice-panel");
  await expect(voice).toBeVisible();
  await expect(voice).toContainText("Review a pre-recorded care conversation");
  await expect(voice).toContainText("patient follow-up");
  await expect(voice).not.toContainText("nurse follow-up");
  await expect(voice).not.toContainText("mock-transcript-fixture");
  const audio = voice.getByTestId("voice-audio");
  await expect(audio).toBeVisible();
  await expect(audio).toHaveAttribute("data-audio-state", "ready");
  const audioMetadata = await audio.evaluate((element) => ({
    readyState: (element as HTMLAudioElement).readyState,
    duration: (element as HTMLAudioElement).duration,
    src: (element as HTMLAudioElement).src,
  }));
  expect(audioMetadata.readyState).toBeGreaterThanOrEqual(1);
  expect(audioMetadata.duration).toBeGreaterThan(0);
  expect(audioMetadata.src).toMatch(/^blob:/);
  await expect(voice.getByRole("button", { name: /microphone/i })).toHaveCount(
    0,
  );
  await voice
    .getByRole("button", { name: "Create care-note suggestion" })
    .click();
  await expect(page.getByTestId("voice-session-result")).toContainText(
    "Suggestion status: Ready for review",
  );
  await expect(
    page.getByTestId("voice-session-result").getByRole("button", {
      name: "View source",
    }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Documented symptom after dose change"),
  ).toHaveCount(0);
  await page.screenshot({
    path: screenshotPath(test.info().project.name, "voice-patient.png"),
    fullPage: false,
  });
  await audio.click();
  await audio.evaluate(async (element) => {
    await (element as HTMLAudioElement).play();
  });
  await expect
    .poll(() =>
      audio.evaluate((element) => (element as HTMLAudioElement).currentTime),
    )
    .toBeGreaterThan(0);
  await audio.evaluate((element) => (element as HTMLAudioElement).pause());
  await expect(audio).toHaveJSProperty("error", null);
  expect({ consoleErrors, errorResponses }).toEqual({
    consoleErrors: [],
    errorResponses: [],
  });
});
