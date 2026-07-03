const path = require("path");
const puppeteer = require("/Users/mac/node_modules/puppeteer-core");

async function main() {
  const root = path.resolve(__dirname, "..");
  const input = path.join(root, "learning-pack", "QuickCommerceOps-Learning-Interview-Pack.html");
  const output = path.join(root, "learning-pack", "QuickCommerceOps-Learning-Interview-Pack.pdf");

  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"]
  });

  const page = await browser.newPage();
  await page.goto(`file://${input}`, { waitUntil: "networkidle0" });
  await page.pdf({
    path: output,
    format: "A4",
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: "0mm", right: "0mm", bottom: "0mm", left: "0mm" }
  });

  await browser.close();
  console.log(output);
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
