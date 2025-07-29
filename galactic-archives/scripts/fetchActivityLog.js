const fs = require("fs");
const path = require("path");
const cheerio = require("cheerio");

const USE_OFFLINE_MODE = true; // Set to false for live fetch

const OFFLINE_HTML_PATH = path.join(__dirname, "../data/sample-activity.html");
const OUTPUT_PATH = path.join(__dirname, "../data/recent-activity.json");

async function fetchActivityOffline() {
  const html = fs.readFileSync(OFFLINE_HTML_PATH, "utf8");
  const $ = cheerio.load(html);

  const changes = [];

  $(".mw-changeslist-title").each((i, el) => {
    const link = $(el).find("a").attr("href");
    const title = $(el).text().trim();

    if (title && link) {
      changes.push({
        title,
        link: `https://swgr.org${link}`,
        timestamp: new Date().toISOString()
      });
    }
  });

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(changes, null, 2));
  console.log(`✅ Offline mode: wrote ${changes.length} items to recent-activity.json`);
}

fetchActivityOffline();
