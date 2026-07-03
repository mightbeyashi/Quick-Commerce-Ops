const path = require("path");
const puppeteer = require("/Users/mac/node_modules/puppeteer-core");

const root = path.resolve(__dirname, "..");
const reportPath = path.join(root, "report", "index.html");
const outputDir = path.join(root, "learning-pack", "assets", "screenshots");
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function sectionByHeading(page, heading) {
  const handles = await page.$$("h2");
  for (const handle of handles) {
    const text = await page.evaluate(el => el.textContent.trim(), handle);
    if (text === heading) {
      return await handle.evaluateHandle(el => el.closest("section"));
    }
  }
  return null;
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1800, height: 1500, deviceScaleFactor: 3 });
  await page.goto(`file://${reportPath}`, { waitUntil: "networkidle0" });

  await page.screenshot({
    path: path.join(outputDir, "report_top.png"),
    fullPage: false
  });

  const sections = [
    ["executive_snapshot", "Executive Snapshot"],
    ["charts", "Charts"],
    ["category_health", "Category Health"],
    ["replenishment_watchlist", "Replenishment Watchlist"],
    ["interview_explain", "How To Explain This In Interview"]
  ];

  for (const [name, heading] of sections) {
    const section = await sectionByHeading(page, heading);
    if (section) {
      await section.evaluate(el => el.scrollIntoView({ block: "start" }));
      await sleep(350);
      await section.screenshot({
        path: path.join(outputDir, `${name}.png`)
      });
    }
  }

  await browser.close();
  console.log("Captured local report screenshots.");
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
