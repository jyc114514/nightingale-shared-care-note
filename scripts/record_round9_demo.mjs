import { chromium } from "../frontend/node_modules/@playwright/test/index.mjs";
import fs from "node:fs";
import path from "node:path";

const BASE_URL = process.env.DEMO_BASE_URL ?? "http://127.0.0.1:5173";
const API_URL = process.env.DEMO_API_URL ?? "http://127.0.0.1:8000";
const PASSWORD = process.env.DEMO_RECORDING_PASSWORD;
const OUTPUT_DIR = path.resolve("deliverables/iteration");
const VIDEO_STAGING_DIR = path.resolve("artifacts/iteration-video-round9");
const OUTPUT_PATH = path.join(
  OUTPUT_DIR,
  "Nightingale_Real_Clinic_Iteration_Demo.webm",
);

if (!PASSWORD) {
  throw new Error("DEMO_RECORDING_PASSWORD is required for local synthetic recording");
}

async function login(context, email) {
  const response = await context.request.post(`${API_URL}/auth/login`, {
    data: { email, password: PASSWORD },
  });
  if (response.status() !== 200) {
    throw new Error(`local synthetic login failed for ${email}`);
  }
}

async function ensureVisible(locator, label) {
  if (!(await locator.isVisible().catch(() => false))) {
    throw new Error(`REHEARSAL FAIL: ${label} is not visible`);
  }
}

async function moveAndClick(page, locator, label, postClickDelay = 900) {
  await ensureVisible(locator, label);
  await locator.scrollIntoViewIfNeeded();
  await page.waitForTimeout(250);
  const box = await locator.boundingBox();
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, {
      steps: 10,
    });
    await page.waitForTimeout(350);
  }
  await locator.click();
  await page.waitForTimeout(postClickDelay);
}

async function injectCursor(page) {
  await page.evaluate(() => {
    if (document.getElementById("demo-cursor")) return;
    const cursor = document.createElement("div");
    cursor.id = "demo-cursor";
    cursor.innerHTML =
      '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 3L19 12L12 13L9 20L5 3Z" fill="white" stroke="black" stroke-width="1.5" stroke-linejoin="round"/></svg>';
    cursor.style.cssText =
      "position:fixed;z-index:999999;pointer-events:none;width:24px;height:24px;transition:left .1s,top .1s;filter:drop-shadow(1px 1px 2px rgba(0,0,0,.3));left:0;top:0";
    document.body.appendChild(cursor);
    document.addEventListener("mousemove", (event) => {
      cursor.style.left = `${event.clientX}px`;
      cursor.style.top = `${event.clientY}px`;
    });
  });
}

async function injectSubtitleBar(page) {
  await page.evaluate(() => {
    if (document.getElementById("demo-subtitle")) return;
    const bar = document.createElement("div");
    bar.id = "demo-subtitle";
    bar.style.cssText =
      "position:fixed;bottom:0;left:0;right:0;z-index:999998;text-align:center;padding:11px 20px;background:rgba(15,23,42,.84);color:white;font-family:Segoe UI,sans-serif;font-size:16px;font-weight:600;letter-spacing:.2px;transition:opacity .25s;pointer-events:none;opacity:0";
    document.body.appendChild(bar);
  });
}

async function showSubtitle(page, text) {
  await page.evaluate((value) => {
    const bar = document.getElementById("demo-subtitle");
    if (!bar) return;
    bar.textContent = value;
    bar.style.opacity = value ? "1" : "0";
  }, text);
  if (text) await page.waitForTimeout(1000);
}

async function panGlance(page) {
  const cards = await page.getByTestId("glance-item").all();
  for (const card of cards.slice(0, 6)) {
    await card.scrollIntoViewIfNeeded();
    const box = await card.boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + 75, { steps: 8 });
      await page.waitForTimeout(500);
    }
  }
}

async function openAndCloseSource(page) {
  const sourceButton = page
    .getByTestId("glance-item")
    .nth(1)
    .getByRole("button", { name: "Open source" });
  await moveAndClick(page, sourceButton, "Glance source");
  await ensureVisible(
    page.getByRole("region", { name: "Original source", exact: true }),
    "Original source panel",
  );
  await page.waitForTimeout(2200);
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Close source" }),
    "Close source",
  );
}

async function rehearse(page, context) {
  await login(context, "clinician.a@clinic-a.test");
  await page.goto(`${BASE_URL}/?lang=en`);
  await page.waitForTimeout(900);
  await ensureVisible(page.getByTestId("glance-item").first(), "Glance card");
  if ((await page.getByTestId("glance-item").count()) !== 6) {
    throw new Error("REHEARSAL FAIL: Glance View did not cap at six items");
  }
  await ensureVisible(
    page.getByRole("button", { name: "Review conflict" }),
    "Review conflict",
  );
  await ensureVisible(
    page.getByTestId(/^prepare-publication-/).first(),
    "Prepare patient update",
  );
  await ensureVisible(
    page.getByRole("button", { name: "Create care-note suggestion" }),
    "Voice suggestion",
  );
  await ensureVisible(
    page.getByRole("button", { name: "Check availability" }),
    "Provider availability",
  );
  await openAndCloseSource(page);
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Review conflict" }),
    "Review conflict",
  );
  await ensureVisible(page.getByTestId("clinical-conflict-panel"), "Clinical conflict panel");
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Close conflict review" }),
    "Close conflict review",
  );
  await moveAndClick(
    page,
    page.getByTestId(/^prepare-publication-/).first(),
    "Prepare patient update",
  );
  await ensureVisible(page.getByTestId("publication-review-panel"), "Publication review panel");
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Close publication review" }),
    "Close publication review",
  );
  await page.request.post(`${API_URL}/auth/logout`);
  await login(context, "sarah.patient@clinic-a.test");
  await page.goto(`${BASE_URL}/?lang=en`);
  await page.waitForTimeout(900);
  await ensureVisible(page.getByText("Patient privacy"), "Patient privacy");
  if ((await page.getByTestId("glance-item").count()) !== 0) {
    throw new Error("REHEARSAL FAIL: Patient Glance View is visible");
  }
  console.log("REHEARSAL PASSED - local synthetic selectors verified");
}

async function record(page, context) {
  await login(context, "clinician.a@clinic-a.test");
  await page.goto(`${BASE_URL}/?lang=en`);
  await page.waitForTimeout(1200);
  await injectCursor(page);
  await injectSubtitleBar(page);

  await showSubtitle(page, "A trust-centered real-clinic iteration");
  await page.getByRole("region", { name: "Glance view" }).scrollIntoViewIfNeeded();
  await showSubtitle(page, "Glance View: six bounded items, ranked for attention");
  await panGlance(page);
  await page.waitForTimeout(1200);

  await showSubtitle(page, "Every highlighted claim stays linked to its source");
  await openAndCloseSource(page);

  await showSubtitle(page, "One contradiction, two immutable sources, one clinician decision");
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Review conflict" }),
    "Review conflict",
  );
  await page.waitForTimeout(2500);
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Close conflict review" }),
    "Close conflict review",
  );

  await showSubtitle(page, "Accept is not Publish: patient release is a separate gate");
  await moveAndClick(
    page,
    page.getByTestId(/^prepare-publication-/).first(),
    "Prepare patient update",
  );
  await page.waitForTimeout(2600);
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Close publication review" }),
    "Close publication review",
  );

  await page.route("**/ai-processing/provider-status", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "provider_temporarily_unavailable" }),
    });
  });
  await showSubtitle(page, "Provider failure stays explicit; existing records remain usable");
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Check availability" }),
    "Check provider availability",
  );
  await page.waitForTimeout(1700);
  await page.unroute("**/ai-processing/provider-status");

  await showSubtitle(page, "Prerecorded synthetic audio becomes a reviewable suggestion");
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Create care-note suggestion" }),
    "Create Voice care-note suggestion",
  );
  await ensureVisible(
    page.getByText("Suggestion status: Ready for review"),
    "Voice suggestion result",
  );
  await page.waitForTimeout(2200);
  const voiceSource = page
    .getByRole("region", { name: "Voice note" })
    .getByRole("button", { name: "View source" });
  await moveAndClick(page, voiceSource, "Voice source");
  await page.waitForTimeout(1700);
  await moveAndClick(
    page,
    page.getByRole("button", { name: "Close source" }),
    "Close Voice source",
  );

  await context.request.post(`${API_URL}/auth/logout`);
  await login(context, "sarah.patient@clinic-a.test");
  await page.goto(`${BASE_URL}/?lang=en`);
  await page.waitForTimeout(1200);
  await injectCursor(page);
  await injectSubtitleBar(page);
  await showSubtitle(page, "Patient view: only patient-facing published care is shown");
  await ensureVisible(page.getByText("Patient privacy"), "Patient privacy projection");
  await page.waitForTimeout(3200);
  await showSubtitle(page, "Narrow safety slices, explicit boundaries, honest scope");
  await page.waitForTimeout(1800);
  await showSubtitle(page, "");
}

async function main() {
  const rehearsal = process.argv.includes("--rehearse");
  if (rehearsal) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    try {
      await rehearse(page, context);
    } finally {
      await context.close();
      await browser.close();
    }
    return;
  }

  fs.rmSync(VIDEO_STAGING_DIR, { recursive: true, force: true });
  fs.mkdirSync(VIDEO_STAGING_DIR, { recursive: true });
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: VIDEO_STAGING_DIR, size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();
  const video = page.video();
  try {
    await record(page, context);
  } finally {
    await context.close();
    await browser.close();
  }
  if (!video) throw new Error("recording did not create a video");
  const source = await video.path();
  fs.copyFileSync(source, OUTPUT_PATH);
  console.log(`VIDEO_CREATED path=${OUTPUT_PATH} bytes=${fs.statSync(OUTPUT_PATH).size}`);
}

main().catch((error) => {
  console.error(`DEMO_RECORDING_FAILED: ${error.message}`);
  process.exitCode = 1;
});
