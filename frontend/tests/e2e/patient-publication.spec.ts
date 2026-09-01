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

function screenshotPath(projectName: string, filename: string) {
  mkdirSync(screenshotRoot, { recursive: true });
  return path.join(screenshotRoot, projectName + "-publication-" + filename);
}

test.describe.configure({ mode: "serial" });

test("Scenario F - patient publication requires dosage match, approval, publish, recall, and correction", async ({
  page,
  browser,
}, testInfo) => {
  await login(page, "staff.a@clinic-a.test");
  const patientId = await page.locator("#patient-select").inputValue();
  const sourceResponse = await backendRequest(
    page,
    "/patients/" + patientId + "/entries",
    {
      method: "POST",
      body: {
        entry_type: "staff_note",
        content: "Continue metformin 500 mg twice daily.",
      },
    },
  );
  expect(sourceResponse.status).toBe(200);
  const source = sourceResponse.body as JsonObject;
  const sourceEntryId = String(source.id);
  await page.reload();
  const sourceCard = page.getByTestId("timeline-entry-" + sourceEntryId);
  await expect(sourceCard).toBeVisible();
  await sourceCard
    .getByRole("button", { name: "Prepare patient update" })
    .click();
  const drawer = page.getByTestId("patient-publication-drawer");
  await expect(drawer).toBeVisible();
  const draft = drawer.getByTestId("publication-draft");
  await expect(draft).toHaveValue("Continue metformin 500 mg twice daily.");
  await draft.fill("Take metformin 1000 mg twice daily.");
  await drawer.getByTestId("publication-save").click();
  await expect(drawer.getByTestId("publication-dosage-status")).toContainText(
    "cannot be approved or published",
  );
  await expect(drawer.getByTestId("publication-mismatch")).toBeVisible();
  await expect(drawer.getByTestId("publication-approve")).toHaveCount(0);
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "dosage-mismatch.png"),
    fullPage: false,
  });
  await drawer
    .getByRole("button", { name: "Close publication review" })
    .click();

  const patientContext = await browser.newContext({
    viewport:
      testInfo.project.name === "mobile-390"
        ? { width: 390, height: 844 }
        : { width: 1440, height: 900 },
  });
  const patientPage = await patientContext.newPage();
  await login(patientPage, "sarah.patient@clinic-a.test");
  await expect(patientPage.getByTestId("patient-published-care")).toBeVisible();
  await expect(
    patientPage.getByText("Take metformin 1000 mg twice daily."),
  ).toHaveCount(0);
  await expect(
    patientPage.getByText("Continue metformin 500 mg twice daily."),
  ).toHaveCount(0);
  await patientContext.close();

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page.getByLabel("Email")).toBeVisible();
  await login(page, "clinician.a@clinic-a.test");
  const clinicianCard = page.getByTestId("timeline-entry-" + sourceEntryId);
  await clinicianCard
    .getByRole("button", { name: "Prepare patient update" })
    .click();
  const clinicianDrawer = page.getByTestId("patient-publication-drawer");
  await expect(clinicianDrawer).toBeVisible();
  await clinicianDrawer
    .getByTestId("publication-draft")
    .fill("Take metformin 500 mg twice daily.");
  await clinicianDrawer.getByTestId("publication-save").click();
  await expect(
    clinicianDrawer.getByTestId("publication-dosage-status"),
  ).toContainText("matches the selected source exactly");
  await clinicianDrawer.getByTestId("publication-approve").click();
  await expect(clinicianDrawer.getByTestId("publication-state")).toContainText(
    "Clinician approved",
  );
  await clinicianDrawer.getByTestId("publication-publish").click();
  await expect(
    clinicianDrawer.getByTestId("publication-publish-confirm"),
  ).toBeVisible();
  await clinicianDrawer.getByTestId("publication-confirm-publish").click();
  await expect(
    clinicianDrawer.getByTestId("publication-success"),
  ).toContainText("Published to the patient portal");
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "published.png"),
    fullPage: false,
  });

  const publishedPatientContext = await browser.newContext({
    viewport:
      testInfo.project.name === "mobile-390"
        ? { width: 390, height: 844 }
        : { width: 1440, height: 900 },
  });
  const publishedPatientPage = await publishedPatientContext.newPage();
  await login(publishedPatientPage, "sarah.patient@clinic-a.test");
  const patientCare = publishedPatientPage.getByTestId(
    "patient-published-care",
  );
  await expect(patientCare).toContainText("Take metformin 500 mg twice daily.");
  await expect(patientCare).toContainText("Published care updates");
  await expect(
    publishedPatientPage.getByText("Take metformin 1000 mg twice daily."),
  ).toHaveCount(0);
  await expect(
    publishedPatientPage.getByText("Continue metformin 500 mg twice daily."),
  ).toHaveCount(0);
  await expect(
    publishedPatientPage.getByTestId("publication-review-panel"),
  ).toHaveCount(0);
  await publishedPatientContext.close();

  await clinicianDrawer.getByTestId("publication-recall").click();
  await expect(clinicianDrawer.getByTestId("publication-state")).toContainText(
    "Recalled from portal",
  );
  const recalledPatientContext = await browser.newContext({
    viewport:
      testInfo.project.name === "mobile-390"
        ? { width: 390, height: 844 }
        : { width: 1440, height: 900 },
  });
  const recalledPatientPage = await recalledPatientContext.newPage();
  await login(recalledPatientPage, "sarah.patient@clinic-a.test");
  const recalledCare = recalledPatientPage.getByTestId(
    "patient-published-care",
  );
  await expect(recalledCare).toContainText(
    "This care update was withdrawn by the clinic.",
  );
  await expect(recalledCare).not.toContainText(
    "Take metformin 500 mg twice daily.",
  );
  await recalledPatientContext.close();

  await clinicianDrawer.getByTestId("publication-correction").click();
  await expect(clinicianDrawer.getByTestId("publication-draft")).toBeVisible();
  await clinicianDrawer
    .getByTestId("publication-draft")
    .fill("Please take metformin 500 mg twice daily.");
  await clinicianDrawer.getByTestId("publication-save").click();
  await clinicianDrawer.getByTestId("publication-approve").click();
  await clinicianDrawer.getByTestId("publication-publish").click();
  await clinicianDrawer.getByTestId("publication-confirm-publish").click();
  await expect(
    clinicianDrawer.getByTestId("publication-success"),
  ).toBeVisible();
  const correctedPatientContext = await browser.newContext({
    viewport:
      testInfo.project.name === "mobile-390"
        ? { width: 390, height: 844 }
        : { width: 1440, height: 900 },
  });
  const correctedPatientPage = await correctedPatientContext.newPage();
  await login(correctedPatientPage, "sarah.patient@clinic-a.test");
  const correctedCare = correctedPatientPage.getByTestId(
    "patient-published-care",
  );
  await expect(correctedCare).toContainText(
    "Please take metformin 500 mg twice daily.",
  );
  await expect(correctedCare).not.toContainText("withdrawn by the clinic");
  await expect(correctedCare).not.toContainText(
    "Take metformin 1000 mg twice daily.",
  );
  await correctedPatientContext.close();
  await page.screenshot({
    path: screenshotPath(testInfo.project.name, "correction-published.png"),
    fullPage: false,
  });

  const raceSource = await backendRequest(
    page,
    "/patients/" + patientId + "/entries",
    {
      method: "POST",
      body: {
        entry_type: "clinician_section",
        content: "The synthetic follow-up plan is ready for review.",
      },
    },
  );
  expect(raceSource.status).toBe(200);
  const raceSourceBody = raceSource.body as JsonObject;
  const raceDraft = await backendRequest(
    page,
    "/entries/" + String(raceSourceBody.id) + "/patient-publications",
    { method: "POST", body: {} },
  );
  expect(raceDraft.status).toBe(200);
  const racePublication = raceDraft.body as JsonObject;
  const raceContext = await browser.newContext({
    viewport:
      testInfo.project.name === "mobile-390"
        ? { width: 390, height: 844 }
        : { width: 1440, height: 900 },
  });
  const racePage = await raceContext.newPage();
  await login(racePage, "clinician.a@clinic-a.test");
  const [winner, stale] = await Promise.all([
    backendRequest(
      page,
      "/patient-publications/" + String(racePublication.id) + "/approve",
      {
        method: "POST",
        body: { expected_workflow_version: 1 },
      },
    ),
    backendRequest(
      racePage,
      "/patient-publications/" + String(racePublication.id) + "/approve",
      {
        method: "POST",
        body: { expected_workflow_version: 1 },
      },
    ),
  ]);
  expect([winner.status, stale.status].sort()).toEqual([200, 409]);
  const staleBody = winner.status === 409 ? winner.body : stale.body;
  expect((staleBody as JsonObject).detail).toMatchObject({
    actual_workflow_version: 2,
  });
  await raceContext.close();
});
