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
  await expect(page.getByText("Glance View")).toBeVisible();
  const doctorCard = page
    .getByTestId("glance-item")
    .filter({ hasText: "Doctor consult" })
    .first();
  await expect(doctorCard).toBeVisible();
  await expect(doctorCard).toContainText("Information");
  await expect(doctorCard).toContainText(/Needs review|Reviewed/);
  await expect(doctorCard).toContainText("No risk flag");
  await expect(doctorCard.getByTestId("glance-action")).toContainText(
    "Review suggestion",
  );
  await doctorCard.getByTestId("ranking-details").click();
  await expect(doctorCard).toContainText(
    "Priority helps organise the view. It is not a medical risk score.",
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
  const source = page.getByRole("region", {
    name: "Original source",
    exact: true,
  });
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
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "source-open.png"),
    fullPage: false,
  });

  const highlightId = new URL(page.url()).searchParams.get("highlight");
  expect(highlightId).toBeTruthy();
  await page.reload();
  await expect(
    page.getByRole("region", { name: "Original source", exact: true }),
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
    page.getByRole("region", { name: "Original source", exact: true }),
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
      ).toContainText("Reviewed");
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
  browser,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  const entry = await staffEntry(page);
  const staffCard = page.getByTestId("timeline-entry-" + entry.id);
  await expect(staffCard).toBeVisible();
  await staffCard.getByRole("button", { name: "History" }).click();
  const history = staffCard.getByRole("region", { name: "History" });
  await expect(history).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "history-open.png"),
    fullPage: false,
  });

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
    staffCard.getByText("Version " + (entry.currentVersion + 1), {
      exact: true,
    }),
  ).toBeVisible();

  const compare = history.getByRole("button", { name: "Compare" }).first();
  if (await compare.count()) {
    await compare.click();
    await expect(history).toContainText("Changes from version");
  }
  const revert = history
    .getByRole("button", { name: "Revert" })
    .nth(Math.max(0, entry.currentVersion - 1));
  await expect(revert).toBeVisible();
  await revert.click();
  await expect(
    staffCard.getByText(entry.content, { exact: true }),
  ).toBeVisible();
  await expect(history).toContainText("Version " + (entry.currentVersion + 2));
  await expect(history).toContainText("Version 1");
  await page.screenshot({
    path: screenshotPath(
      testInfo.project.name,
      "history-open-after-revert.png",
    ),
    fullPage: false,
  });

  const staffSourceCard = page
    .getByTestId("glance-item")
    .filter({ hasText: "Pending renal panel" })
    .first();
  if (await staffSourceCard.count()) {
    await staffSourceCard.getByRole("button", { name: "Open source" }).click();
    await expect(page.getByTestId("immutable-timeline-source")).toBeVisible();
    await page.waitForTimeout(800);
    await page.screenshot({
      path: screenshotPath(testInfo.project.name, "source-v1-current-v3.png"),
      fullPage: false,
    });
    await page.getByRole("button", { name: "Close source" }).click();
  }

  await staffCard.getByRole("button", { name: "Comments" }).click();
  await expect(page.getByTestId("comments-drawer")).toBeVisible();
  const comments = page.getByRole("region", { name: "Comments" });
  await expect(comments).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "comments-open.png"),
    fullPage: false,
  });
  const secondContext = await browser.newContext({
    baseURL: "http://127.0.0.1:5173",
  });
  const secondPage = await secondContext.newPage();
  await login(secondPage, "clinician.a@clinic-a.test");
  const secondEntry = await staffEntry(secondPage);
  await secondPage
    .getByTestId("timeline-entry-" + secondEntry.id)
    .getByRole("button", { name: "Comments" })
    .click();
  await expect(
    secondPage.getByRole("region", { name: "Comments" }),
  ).toBeVisible();
  await expect(secondPage.getByTestId("realtime-status")).toContainText(
    "Up to date",
  );
  const rootBody = "Root thread " + testInfo.project.name + " " + Date.now();
  await comments.getByLabel("Comment body").fill("@");
  const mentionOption = comments.getByRole("option").first();
  await expect(mentionOption).toBeVisible();
  const mentionText =
    (await mentionOption.textContent())?.split(" · ")[0] ?? "@clinician";
  await mentionOption.click();
  await comments.getByLabel("Comment body").fill(`${mentionText} ${rootBody}`);
  await comments.getByRole("button", { name: "Add comment" }).click();
  const root = comments
    .locator('[data-testid^="comment-"]')
    .filter({ hasText: rootBody })
    .first();
  await expect(root).toBeVisible();
  await expect(root).toContainText("Mentioned teammates");

  await root.getByRole("button", { name: "Assign task" }).click();
  const taskTitle =
    "Follow up assigned " + testInfo.project.name + " " + Date.now();
  const taskDrawer = page.getByTestId("task-drawer");
  await expect(taskDrawer).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "task-open.png"),
    fullPage: false,
  });
  const taskPanel = page.getByTestId("task-panel");
  await expect(taskPanel.getByLabel("Task title")).toBeFocused();
  await expect(taskPanel).toBeVisible();
  await taskPanel.getByLabel("Task title").fill(taskTitle);
  await taskPanel
    .locator("form")
    .getByLabel("Assign to", { exact: true })
    .selectOption({ index: 1 });
  await taskPanel.getByRole("button", { name: "Create task" }).click();
  await expect(
    taskPanel.getByTestId(/task-/).filter({ hasText: taskTitle }),
  ).toBeVisible();
  await expect(
    page.getByTestId("glance-item").filter({ hasText: taskTitle }),
  ).toBeVisible();
  await expect(
    secondPage.getByRole("region", { name: "Comments" }),
  ).toContainText(rootBody);
  const secondTaskCard = secondPage
    .getByTestId("glance-item")
    .filter({ hasText: taskTitle })
    .first();
  await expect(secondTaskCard).toBeVisible();
  await secondPage.getByRole("button", { name: "Close" }).click();
  await secondTaskCard.getByRole("button", { name: "Open task" }).click();
  await expect(secondPage.getByTestId("task-panel")).toContainText(taskTitle);
  await taskPanel.getByLabel(`Status: ${taskTitle}`).selectOption("done");
  await expect(
    taskPanel.getByTestId(/task-/).filter({ hasText: taskTitle }),
  ).toContainText("Done");
  await page.getByRole("button", { name: "Close tasks" }).click();

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
  await secondContext.close();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-b.png"),
    fullPage: true,
  });
});

test("Comments drawer survives realtime refresh and updates in place", async ({
  page,
  browser,
}) => {
  await login(page, "staff.a@clinic-a.test");
  const entry = await staffEntry(page);
  const card = page.getByTestId("timeline-entry-" + entry.id);
  const commentsButton = card.getByRole("button", { name: "Comments" });
  await commentsButton.click();
  const drawer = page.getByTestId("comments-drawer");
  await expect(drawer).toBeVisible();
  await expect(page.getByRole("region", { name: "Comments" })).toBeVisible();

  // The seed and preceding serial scenarios leave collaboration events in the stream.
  await page.waitForTimeout(5200);
  await expect(drawer).toBeVisible();
  await expect(page.getByRole("region", { name: "Comments" })).toBeVisible();

  const secondContext = await browser.newContext({
    baseURL: "http://127.0.0.1:5173",
  });
  const secondPage = await secondContext.newPage();
  try {
    await login(secondPage, "clinician.a@clinic-a.test");
    const secondEntry = await staffEntry(secondPage);
    const secondComments = secondPage
      .getByTestId("timeline-entry-" + secondEntry.id)
      .getByRole("button", { name: "Comments" });
    await secondComments.click();
    const secondDrawer = secondPage.getByTestId("comments-drawer");
    await expect(secondDrawer).toBeVisible();
    const body = "Realtime drawer check " + Date.now();
    await secondPage.getByLabel("Comment body").fill(body);
    await secondDrawer.getByRole("button", { name: "Add comment" }).click();
    await expect(secondDrawer).toContainText(body);
    await expect(drawer).toContainText(body);
  } finally {
    await secondContext.close();
  }

  await drawer.getByRole("button", { name: "Close" }).click();
  await expect(drawer).toHaveCount(0);
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
    "Historical summary · not the original record",
  );
  await expect(
    historical.getByRole("button", { name: "View original record" }).first(),
  ).toBeVisible();
  await expect(
    historical.getByTestId(/historical-source-/).first(),
  ).toContainText("v1");
  const staffCard = page.getByTestId("timeline-entry-" + entry.id);
  await expect(staffCard).toContainText(winnerContent);
  await staffCard.getByRole("button", { name: "History" }).click();
  const conflictPanel = page.getByTestId("conflict-panel");
  await expect(conflictPanel).toBeVisible();
  await expect(conflictPanel).toContainText(
    "This record changed while you were editing",
  );
  await expect(conflictPanel).toContainText(winnerContent);
  await expect(conflictPanel).toContainText(staleContent);
  await expect(conflictPanel).toContainText(
    "record is now version " + (entry.currentVersion + 1),
  );
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "scenario-c.png"),
    fullPage: true,
  });
});

test("Patient privacy - cookie patient sees only patient-facing entries and internal endpoint is denied", async ({
  page,
}, testInfo) => {
  await login(page, "sarah.patient@clinic-a.test");
  await expect(page.getByText("Your care summary")).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Patient care summary", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Care instruction", exact: true }),
  ).toBeVisible();
  await expect(page.getByTestId("historical-context")).toBeVisible();
  await expect(
    page.getByText("Documented symptom after dose change"),
  ).toHaveCount(0);
  await expect(
    page.getByText("Internal follow-up: confirm the next appointment window."),
  ).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Comments" })).toHaveCount(0);
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "patient-privacy.png"),
    fullPage: false,
  });

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

test("Chinese chrome keeps source data and provenance controls usable", async ({
  page,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  await page.getByRole("button", { name: "简体中文" }).click();
  await expect(page.getByText("共享照护记录")).toBeVisible();
  await expect(page.getByText("纵向时间线")).toBeVisible();
  await expect(page.getByRole("button", { name: "使用指南" })).toBeVisible();

  const sourceButton = page
    .getByTestId("glance-item")
    .first()
    .getByRole("button", { name: "打开来源" });
  await sourceButton.click();
  const source = page.getByRole("region", { name: "原始来源", exact: true });
  await expect(source).toBeVisible();
  await expect(source.getByTestId("source-quote")).toBeVisible();
  await page.waitForTimeout(3000);
  await expect(page.getByTestId("immutable-timeline-source")).toBeVisible();
  await expect(
    page.getByTestId("immutable-timeline-source").getByTestId("source-quote"),
  ).toBeVisible();
  await page.getByRole("button", { name: "关闭来源" }).click();
  await expect(
    page.getByRole("region", { name: "原始来源", exact: true }),
  ).toHaveCount(0);
  await expect(page.getByTestId("immutable-timeline-source")).toHaveCount(0);
  expect(new URL(page.url()).searchParams.has("highlight")).toBe(false);
  const chineseEntry = await staffEntry(page);
  const chineseStaffCard = page.getByTestId(
    "timeline-entry-" + chineseEntry.id,
  );
  await chineseStaffCard
    .getByRole("button", { name: "历史", exact: true })
    .click();
  const chineseHistory = chineseStaffCard.getByRole("region", {
    name: "历史记录",
    exact: true,
  });
  await expect(chineseHistory).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "history-chinese.png"),
    fullPage: false,
  });
  await chineseStaffCard
    .getByRole("button", { name: "隐藏历史", exact: true })
    .click();
});

test("Demo preview uses real internal viewports without recursive controls", async ({
  page,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  await page.getByRole("button", { name: "Guide" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "guide-open.png"),
    fullPage: false,
  });
  await page.getByRole("button", { name: "Close guide" }).click();
  const previewSelect = page.getByTestId("demo-preview-select");
  await previewSelect.selectOption("mobile");
  await expect(page.getByTestId("preview-dimensions")).toContainText("390×844");
  const previewFrame = page.locator(
    'iframe[data-testid="demo-preview-iframe"]',
  );
  await expect(previewFrame).toBeVisible();
  const embedded = page.frameLocator(
    'iframe[data-testid="demo-preview-iframe"]',
  );
  await expect(embedded.getByText("Longitudinal timeline")).toBeVisible();
  await expect(embedded.getByTestId("top-card")).toBeVisible();
  await expect(embedded.getByTestId("glance-item").first()).toBeVisible();
  await expect
    .poll(async () =>
      previewFrame.evaluate((element) => {
        const frame = element as HTMLIFrameElement;
        return frame.contentWindow
          ? [frame.contentWindow.innerWidth, frame.contentWindow.innerHeight]
          : null;
      }),
    )
    .toEqual([390, 844]);
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "preview-mobile.png"),
    fullPage: false,
  });
  expect(await embedded.getByTestId("demo-preview-select").count()).toBe(0);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);

  await previewSelect.selectOption("desktop");
  await expect(page.getByTestId("preview-dimensions")).toContainText(
    "1440×900",
  );
  await expect(embedded.getByText("Longitudinal timeline")).toBeVisible();
  await expect(embedded.getByTestId("top-card")).toBeVisible();
  await expect(embedded.getByTestId("glance-item").first()).toBeVisible();
  await expect
    .poll(async () =>
      previewFrame.evaluate((element) => {
        const frame = element as HTMLIFrameElement;
        return frame.contentWindow
          ? [frame.contentWindow.innerWidth, frame.contentWindow.innerHeight]
          : null;
      }),
    )
    .toEqual([1440, 900]);
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "preview-desktop.png"),
    fullPage: false,
  });

  await page.getByRole("button", { name: "Close preview" }).click();
  await expect(page.getByTestId("demo-preview")).toHaveCount(0);
});
