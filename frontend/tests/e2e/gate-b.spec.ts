import { mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test, type Page } from "@playwright/test";

const e2eRoot = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(e2eRoot, "..", "..");
const screenshotRoot = path.resolve(frontendRoot, "..", "artifacts", "gate-b");
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
}

function screenshotPath(projectName: string, filename: string) {
  mkdirSync(screenshotRoot, { recursive: true });
  return path.join(screenshotRoot, `${projectName}-${filename}`);
}

test("Scenario A · clinician traces Glance to an immutable source", async ({
  page,
}, testInfo) => {
  await login(page, "clinician.a@clinic-a.test");
  await expect(page.getByText("Top Card · Glance View")).toBeVisible();
  await expect(
    page.getByTestId("top-card").getByText("AI-scribed · Doctor consult"),
  ).toBeVisible();
  await expect(
    page.getByText("Clinician review required").first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "Open source" }).first().click();
  await expect(
    page.getByRole("region", { name: "Immutable source" }),
  ).toBeVisible();
  await expect(page.getByText(/Exact span/)).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-a.png"),
    fullPage: true,
  });
});

test("Scenario B · staff edits a note, opens history, and adds a thread", async ({
  page,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  await expect(page.getByText("Top Card · Glance View")).toBeVisible();
  await expect(page.getByRole("button", { name: "Accept" })).toHaveCount(0);

  const staffCard = page
    .locator("article")
    .filter({ hasText: "Staff note" })
    .last();
  await staffCard.getByRole("button", { name: "History" }).click();
  await expect(
    staffCard.getByRole("region", { name: "Revision history" }),
  ).toBeVisible();
  await staffCard.getByRole("button", { name: "Edit" }).click();
  const editor = staffCard.getByRole("textbox", { name: /Edit Staff note/ });
  await editor.fill(
    "Pending renal panel requires coordination; staff follow-up confirmed.",
  );
  await staffCard.getByRole("button", { name: "Save revision" }).click();
  await expect(staffCard.getByText("v2", { exact: true })).toBeVisible();

  await staffCard.getByRole("button", { name: "Comments" }).click();
  const comments = page.getByRole("region", { name: "Comments" });
  await expect(comments).toBeVisible();
  const commentBody = `Staff thread follow-up (${testInfo.project.name})`;
  await comments.getByLabel("Comment body").fill(commentBody);
  await comments.getByRole("button", { name: "Add comment" }).click();
  await expect(comments.getByText(commentBody, { exact: true })).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-b.png"),
    fullPage: true,
  });
});
