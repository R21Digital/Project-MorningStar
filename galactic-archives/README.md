# Galactic Archives

This directory contains a simple script for fetching the recent activity log
from the SWGR wiki. The script is designed for Codex environments and runs
entirely offline by default.

## 🛠 Scripts

### Fetch Activity Log (Offline)

```bash
node scripts/fetchActivityLog.js
```

By default, it parses `data/sample-activity.html` and writes the results to
`data/recent-activity.json`.

To re-enable live mode (outside Codex), replace `USE_OFFLINE_MODE = true` with
code that fetches the page using `axios`:

```js
const axios = require("axios");
const { data } = await axios.get("https://swgr.org/wiki/special/activity/");
```

---

### ✅ Summary

- Codex-safe: no web calls
- Fully offline-compatible
- Includes test HTML and output JSON
- Can easily toggle live mode when needed

