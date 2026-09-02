import { chromium } from "../frontend/node_modules/@playwright/test/index.mjs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const root = process.cwd();
const input = path.resolve(root, "deliverables/iteration/real_clinic_iteration_brief.html");
const output = path.resolve(
  root,
  "deliverables/iteration/Nightingale_Real_Clinic_Iteration_Brief.pdf",
);

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1240, height: 1754 } });
  await page.goto(pathToFileURL(input).href, { waitUntil: "load" });
  await page.emulateMedia({ media: "print" });
  await page.pdf({
    path: output,
    format: "A4",
    printBackground: true,
    preferCSSPageSize: true,
  });
  const pages = await page.locator(".page").count();
  console.log(JSON.stringify({ input, output, pages }));
} finally {
  await browser.close();
}
