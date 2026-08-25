import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import path from "node:path";

import { chromium } from "../frontend/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.mjs";

const root = process.cwd();
const input = path.resolve(root, "deliverables/technical_brief.html");
const output = path.resolve(root, "deliverables/Nightingale_Technical_Brief.pdf");

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
  const title = await page.title();
  const pages = await page.locator(".page").count();
  console.log(JSON.stringify({ input, output, title, html_pages: pages }));
} finally {
  await browser.close();
}
