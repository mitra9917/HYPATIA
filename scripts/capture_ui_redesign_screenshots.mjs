#!/usr/bin/env node
/**
 * Capture HYPATIA UI redesign screenshots (desktop 1440 + mobile home).
 * Usage: node scripts/capture_ui_redesign_screenshots.mjs <session_id>
 */
import { mkdirSync } from "fs";
import { chromium } from "playwright";

const sessionId = process.argv[2];
if (!sessionId) {
  console.error("Usage: node scripts/capture_ui_redesign_screenshots.mjs <session_id>");
  process.exit(1);
}

const outDir = "/opt/cursor/artifacts/screenshots";
mkdirSync(outDir, { recursive: true });

const base = "http://127.0.0.1:3000";

const pages = [
  { name: "01-home", path: "/" },
  { name: "02-lab", path: `/lab?session=${sessionId}` },
  { name: "03-session", path: `/session/${sessionId}` },
  { name: "04-sessions", path: "/sessions" },
  { name: "05-library", path: "/library" },
  { name: "06-notebook", path: "/notebook" },
  { name: "07-settings", path: "/settings" },
  { name: "08-about", path: "/about" },
];

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
});
const page = await context.newPage();

await page.addInitScript((sid) => {
  localStorage.setItem("hypatia-active-session", sid);
  localStorage.setItem("hypatia-recent-sessions", JSON.stringify([sid]));
}, sessionId);

for (const { name, path } of pages) {
  await page.goto(`${base}${path}`, { waitUntil: "networkidle", timeout: 120_000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${outDir}/${name}-desktop-1440.png`, fullPage: true });
  console.log("wrote", `${name}-desktop-1440.png`);
}

await context.close();

const mobile = await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  deviceScaleFactor: 2,
});
const mpage = await mobile.newPage();
await mpage.addInitScript((sid) => {
  localStorage.setItem("hypatia-active-session", sid);
  localStorage.setItem("hypatia-recent-sessions", JSON.stringify([sid]));
}, sessionId);
await mpage.goto(`${base}/session/${sessionId}`, { waitUntil: "networkidle", timeout: 120_000 });
await mpage.waitForTimeout(800);
await mpage.screenshot({ path: `${outDir}/09-session-mobile-390.png`, fullPage: true });
console.log("wrote 09-session-mobile-390.png");

await browser.close();
console.log("done", outDir);
