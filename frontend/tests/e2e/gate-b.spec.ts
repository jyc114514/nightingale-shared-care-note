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

type JsonObject = Record<string, unknown>;
type BackendResponse = { status: number; body: unknown };

async function backendRequest(
  page: Page,
  requestPath: string,
  options: { method?: string; body?: JsonObject } = {},
): Promise<BackendResponse> {
  return page.evaluate(
    async ({ requestPath: pathName, method, body }) => {
      const response = await fetch("http://127.0.0.1:8000" + pathName, {
        method,
        credentials: "include",
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
      return { status: response.status, body: await response.json() };
    },
    {
      requestPath,
      method: options.method ?? "GET",
      body: options.body,
    },
  );
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

async function staffEntry(page: Page) {
  const patientId = await page.locator("#patient-select").inputValue();
  const response = await backendRequest(
    page,
    "/patients/" + patientId + "/timeline",
  );
  expect(response.status).toBe(200);
  const rows = response.body as JsonObject[];
  const row = rows.find((candidate) => candidate.entry_type === "staff_note");
  expect(row).toBeDefined();
  return {
    patientId,
    id: String(row?.id),
    currentVersion: Number(row?.current_version),
    content: String(row?.content),
  };
}

function screenshotPath(projectName: string, filename: string) {
  mkdirSync(screenshotRoot, { recursive: true });
  return path.join(screenshotRoot, projectName + "-" + filename);
}

test.describe.configure({ mode: "serial" });

test("Scenario A - clinician traces an AI item to an exact immutable source", async ({
  page,
}, testInfo) => {
  await login(page, "clinician.a@clinic-a.test");
  await expect(page.getByText("Top Card · Glance View")).toBeVisible();
  const doctorCard = page
    .getByTestId("glance-item")
    .filter({ hasText: "Doctor consult" })
    .first();
  await expect(doctorCard).toBeVisible();
  await expect(doctorCard).toContainText("Information");
  await expect(doctorCard).toContainText(/Suggested|Accepted/);
  await expect(doctorCard).toContainText("No explicit risk tag");
  await expect(doctorCard.getByTestId("glance-action")).toContainText(
    "Review suggestion",
  );
  await doctorCard.getByTestId("ranking-details").click();
  await expect(doctorCard).toContainText(
    "Ranking priority, not a medical risk score.",
  );

  if (testInfo.project.name === "desktop-1440") {
    await doctorCard.getByRole("button", { name: "Pin" }).click();
    await expect(
      doctorCard.getByRole("button", { name: "Unpin" }),
    ).toBeVisible();
    await doctorCard.getByRole("button", { name: "Unpin" }).click();
    await expect(doctorCard.getByRole("button", { name: "Pin" })).toBeVisible();
  }

  await doctorCard.getByRole("button", { name: "Open source" }).click();
  const source = page.getByRole("region", { name: "Immutable source" });
  await expect(source).toBeVisible();
  await expect(source).toHaveAttribute("data-source-version", "1");
  const quote = await source.getByTestId("source-quote").textContent();
  expect(quote).toBe("Documented symptom after dose change");
  const timelineSource = page.getByTestId("immutable-timeline-source");
  await expect(timelineSource).toBeVisible();
  await expect(timelineSource.getByTestId("source-quote")).toHaveText(
    quote ?? "",
  );
  const sourceEntryId = await timelineSource.getAttribute(
    "data-source-entry-id",
  );
  expect(sourceEntryId).toBeTruthy();
  await expect(
    page.getByTestId("timeline-entry-" + sourceEntryId),
  ).toBeVisible();

  await page.waitForTimeout(3000);
  await expect(timelineSource.getByTestId("source-quote")).toHaveText(
    quote ?? "",
  );

  const highlightId = new URL(page.url()).searchParams.get("highlight");
  expect(highlightId).toBeTruthy();
  await page.reload();
  await expect(
    page.getByRole("region", { name: "Immutable source" }),
  ).toBeVisible();
  await expect(
    page.getByTestId("immutable-timeline-source").getByTestId("source-quote"),
  ).toHaveText(quote ?? "");

  const secondCard = page
    .getByTestId("glance-item")
    .filter({ hasText: "Patient session" })
    .first();
  await secondCard.getByRole("button", { name: "Open source" }).click();
  const secondTimelineSource = page.getByTestId("immutable-timeline-source");
  await expect(secondTimelineSource).toBeVisible();
  await expect(secondTimelineSource).not.toHaveAttribute(
    "data-source-entry-id",
    sourceEntryId ?? "",
  );
  const secondQuote = await secondTimelineSource
    .getByTestId("source-quote")
    .textContent();
  expect(secondQuote).toBeTruthy();
  expect(secondQuote).not.toBe(quote);

  const secondHighlightId = new URL(page.url()).searchParams.get("highlight");
  expect(secondHighlightId).toBeTruthy();
  await page.reload();
  await expect(
    page.getByTestId("immutable-timeline-source").getByTestId("source-quote"),
  ).toHaveText(secondQuote ?? "");

  const patientId = await page.locator("#patient-select").inputValue();
  await page.getByRole("button", { name: "Close source" }).click();
  await expect(
    page.getByRole("region", { name: "Immutable source" }),
  ).toHaveCount(0);
  await expect(page.getByTestId("immutable-timeline-source")).toHaveCount(0);
  const closedUrl = new URL(page.url());
  expect(closedUrl.searchParams.get("patient")).toBe(patientId);
  expect(closedUrl.searchParams.has("highlight")).toBe(false);

  if (testInfo.project.name === "desktop-1440") {
    const acceptButton = page
      .getByTestId("glance-item")
      .filter({ hasText: "Doctor consult" })
      .getByRole("button", { name: "Accept" });
    if (await acceptButton.count()) {
      await acceptButton.click();
      await expect(
        page
          .getByTestId("glance-item")
          .filter({ hasText: "Doctor consult" })
          .first(),
      ).toContainText("Accepted");
    }
    const nurseCard = page
      .getByTestId("glance-item")
      .filter({ hasText: "Nurse consult" })
      .first();
    const rejectButton = nurseCard.getByRole("button", { name: "Reject" });
    if (await rejectButton.count()) {
      await rejectButton.click();
      await expect(
        page.getByTestId("glance-item").filter({ hasText: "Nurse consult" }),
      ).toHaveCount(0);
    }
    const sourceAfterReview = await backendRequest(
      page,
      "/highlights/" + highlightId + "/source",
    );
    expect(sourceAfterReview.status).toBe(200);
    const sourceBody = sourceAfterReview.body as JsonObject;
    expect(String(sourceBody.version_content)).toContain(String(quote));
  }

  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-a.png"),
    fullPage: true,
  });
});

test("Scenario B - staff creates revisions, diff, revert, and a comment thread", async ({
  page,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  const entry = await staffEntry(page);
  const staffCard = page.getByTestId("timeline-entry-" + entry.id);
  await expect(staffCard).toBeVisible();
  await staffCard.getByRole("button", { name: "History" }).click();
  const history = staffCard.getByRole("region", { name: "Revision history" });
  await expect(history).toBeVisible();

  const revisedContent =
    "Staff revision " + testInfo.project.name + " " + Date.now();
  await staffCard.getByRole("button", { name: "Edit" }).click();
  await staffCard
    .getByRole("textbox", { name: /Edit Staff note/ })
    .fill(revisedContent);
  await staffCard.getByRole("button", { name: "Save revision" }).click();
  await expect(
    staffCard.getByText(revisedContent, { exact: true }),
  ).toBeVisible();
  await expect(
    staffCard.getByText("v" + (entry.currentVersion + 1), { exact: true }),
  ).toBeVisible();

  const compare = history.getByRole("button", { name: "Compare" }).first();
  if (await compare.count()) {
    await compare.click();
    await expect(history).toContainText("Diff v");
  }
  const revert = history
    .getByRole("button", { name: "Revert" })
    .nth(Math.max(0, entry.currentVersion - 1));
  await expect(revert).toBeVisible();
  await revert.click();
  await expect(
    staffCard.getByText(entry.content, { exact: true }),
  ).toBeVisible();
  await expect(history).toContainText("v" + (entry.currentVersion + 2));
  await expect(history).toContainText("v1");

  await staffCard.getByRole("button", { name: "Comments" }).click();
  const comments = page.getByRole("region", { name: "Comments" });
  await expect(comments).toBeVisible();
  const rootBody = "Root thread " + testInfo.project.name + " " + Date.now();
  await comments.getByLabel("Comment body").fill(rootBody);
  await comments.getByRole("button", { name: "Add comment" }).click();
  const root = comments
    .locator('[data-testid^="comment-"]')
    .filter({ hasText: rootBody })
    .first();
  await expect(root).toBeVisible();

  const replyBody = "Nested reply " + testInfo.project.name + " " + Date.now();
  await root.getByRole("button", { name: "Reply" }).click();
  await comments.getByLabel("Comment body").fill(replyBody);
  await comments.getByRole("button", { name: "Add comment" }).click();
  await expect(
    root
      .locator('[data-testid^="replies-"]')
      .getByText(replyBody, { exact: true }),
  ).toBeVisible();

  await root.getByRole("button", { name: "Resolve" }).first().click();
  await expect(root).toContainText("Resolved");
  await root.getByRole("button", { name: "Unresolve" }).first().click();
  await expect(root).toContainText("Open");
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-b.png"),
    fullPage: true,
  });
});

test("Scenario C - stale write returns 409 and remains visible as an optimistic conflict", async ({
  page,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  const entry = await staffEntry(page);
  const winnerContent = "Current winner " + Date.now();
  const winner = await backendRequest(page, "/entries/" + entry.id, {
    method: "PATCH",
    body: {
      expected_version: entry.currentVersion,
      new_content: winnerContent,
    },
  });
  expect(winner.status).toBe(200);
  const staleContent = "Preserved stale submission " + Date.now();
  const stale = await backendRequest(page, "/entries/" + entry.id, {
    method: "PATCH",
    body: {
      expected_version: entry.currentVersion,
      new_content: staleContent,
    },
  });
  expect(stale.status).toBe(409);
  expect(String(JSON.stringify(stale.body))).toContain("actual_version");

  const contextRefresh = await backendRequest(
    page,
    "/patients/" + entry.patientId + "/context/refresh",
    { method: "POST" },
  );
  expect(contextRefresh.status).toBe(200);

  await page.reload();
  const historical = page.getByTestId("historical-context");
  await expect(historical).toBeVisible();
  await expect(historical).toContainText(
    "Derived summary · not canonical source",
  );
  await expect(
    historical.getByRole("button", { name: "Open canonical source" }).first(),
  ).toBeVisible();
  const staffCard = page.getByTestId("timeline-entry-" + entry.id);
  await expect(staffCard).toContainText(winnerContent);
  await staffCard.getByRole("button", { name: "History" }).click();
  const conflictPanel = page.getByTestId("conflict-panel");
  await expect(conflictPanel).toBeVisible();
  await expect(conflictPanel).toContainText("Optimistic concurrency conflict");
  await expect(conflictPanel).toContainText(winnerContent);
  await expect(conflictPanel).toContainText(staleContent);
  await expect(conflictPanel).toContainText(
    "actual v" + (entry.currentVersion + 1),
  );
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-c.png"),
    fullPage: true,
  });
});

test("Patient privacy - cookie patient sees only patient-facing entries and internal endpoint is denied", async ({
  page,
}) => {
  await login(page, "sarah.patient@clinic-a.test");
  await expect(page.getByText("Internal Glance View is hidden")).toBeVisible();
  await expect(page.getByText("Patient summary")).toBeVisible();
  await expect(page.getByText("Patient instruction")).toBeVisible();
  await expect(page.getByTestId("historical-context")).toBeVisible();
  await expect(
    page.getByText("Documented symptom after dose change"),
  ).toHaveCount(0);
  await expect(
    page.getByText("Internal follow-up: confirm the next appointment window."),
  ).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Comments" })).toHaveCount(0);

  const patientId = await page.locator("#patient-select").inputValue();
  const internalGlance = await backendRequest(
    page,
    "/patients/" + patientId + "/glance",
  );
  expect(internalGlance.status).toBe(403);
  const timeline = await backendRequest(
    page,
    "/patients/" + patientId + "/timeline",
  );
  expect(timeline.status).toBe(200);
  const rows = timeline.body as JsonObject[];
  expect(
    rows.every(
      (row) =>
        row.entry_type === "patient_facing_summary" ||
        row.entry_type === "patient_instruction",
    ),
  ).toBe(true);
});
