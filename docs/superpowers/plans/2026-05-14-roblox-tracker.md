# Roblox Player Count Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local website with a live Roblox game leaderboard sorted by player count, with trend indicators and 5-minute auto-refresh.

**Architecture:** A Node.js/Express backend proxies Roblox's public API (avoiding browser CORS), caches results every 5 minutes, and tracks previous counts for trend arrows. A vanilla JS frontend polls the local server and renders the leaderboard with a live countdown timer.

**Tech Stack:** Node.js 18+, Express 4, Jest + Supertest (tests), Vanilla HTML/CSS/JS (frontend)

---

### Task 1: Project Setup

**Files:**
- Create: `package.json`
- Create: `.gitignore`

- [ ] **Step 1: Initialize npm**

```bash
cd /Users/jyclaude/claude-workspace/projects/jayden-test
npm init -y
```

- [ ] **Step 2: Install dependencies**

```bash
npm install express
npm install --save-dev jest supertest
```

- [ ] **Step 3: Update package.json scripts and jest config**

Edit `package.json` — replace the `"scripts"` block and add `"jest"` config:

```json
{
  "scripts": {
    "start": "node server.js",
    "test": "jest"
  },
  "jest": {
    "testEnvironment": "node"
  }
}
```

- [ ] **Step 4: Create .gitignore**

Create `.gitignore`:

```
node_modules/
.cache/
```

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json .gitignore
git commit -m "chore: project setup with express and jest"
```

---

### Task 2: Roblox API Fetcher Module

**Files:**
- Create: `roblox.js`
- Create: `tests/roblox.test.js`

- [ ] **Step 1: Write the failing test**

Create `tests/roblox.test.js`:

```js
const { buildGamesData } = require('../roblox');

describe('buildGamesData', () => {
  it('merges game list with thumbnails and returns sorted descending by playerCount', () => {
    const games = [
      { universeId: 1, name: 'Game A', playerCount: 5000, creatorName: 'Dev1' },
      { universeId: 2, name: 'Game B', playerCount: 12000, creatorName: 'Dev2' },
    ];
    const thumbs = [
      { targetId: 1, imageUrl: 'https://img/1.png' },
      { targetId: 2, imageUrl: 'https://img/2.png' },
    ];
    const result = buildGamesData(games, thumbs);
    expect(result).toHaveLength(2);
    expect(result[0].playerCount).toBe(12000);
    expect(result[0].thumbnailUrl).toBe('https://img/2.png');
    expect(result[1].playerCount).toBe(5000);
    expect(result[1].thumbnailUrl).toBe('https://img/1.png');
  });

  it('sets thumbnailUrl to null when no matching thumbnail exists', () => {
    const games = [{ universeId: 1, name: 'Game A', playerCount: 100, creatorName: 'Dev1' }];
    const result = buildGamesData(games, []);
    expect(result[0].thumbnailUrl).toBe(null);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx jest tests/roblox.test.js -v
```
Expected: FAIL — "Cannot find module '../roblox'"

- [ ] **Step 3: Implement roblox.js**

Create `roblox.js`:

```js
const GAMES_URL = 'https://games.roblox.com/v1/games/list?SortType=2&MaxRows=50';
const THUMBS_BASE = 'https://thumbnails.roblox.com/v1/games/icons';

function buildGamesData(games, thumbs) {
  const thumbMap = {};
  for (const t of thumbs) {
    thumbMap[t.targetId] = t.imageUrl;
  }
  return games
    .map(g => ({
      universeId: g.universeId,
      name: g.name,
      playerCount: g.playerCount,
      creatorName: g.creatorName,
      thumbnailUrl: thumbMap[g.universeId] ?? null,
    }))
    .sort((a, b) => b.playerCount - a.playerCount);
}

async function fetchTopGames() {
  const gamesRes = await fetch(GAMES_URL);
  if (!gamesRes.ok) throw new Error(`Roblox games API error: ${gamesRes.status}`);
  const gamesJson = await gamesRes.json();
  const games = gamesJson.games ?? [];

  if (games.length === 0) return [];

  const ids = games.map(g => g.universeId).join(',');
  const thumbsRes = await fetch(
    `${THUMBS_BASE}?universeIds=${ids}&size=150x150&format=Png&isCircular=false`
  );
  if (!thumbsRes.ok) throw new Error(`Roblox thumbnails API error: ${thumbsRes.status}`);
  const thumbsJson = await thumbsRes.json();

  return buildGamesData(games, thumbsJson.data ?? []);
}

module.exports = { fetchTopGames, buildGamesData };
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx jest tests/roblox.test.js -v
```
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add roblox.js tests/roblox.test.js
git commit -m "feat: Roblox API fetcher with buildGamesData unit tests"
```

---

### Task 3: Express Server with Cache and /api/games

**Files:**
- Create: `server.js`
- Create: `tests/server.test.js`

- [ ] **Step 1: Write the failing tests**

Create `tests/server.test.js`:

```js
const request = require('supertest');
const { createApp } = require('../server');

describe('GET /api/games', () => {
  it('returns 200 with games array after refresh', async () => {
    const mockGames = [
      { universeId: 1, name: 'Game A', playerCount: 100, creatorName: 'Dev', thumbnailUrl: null }
    ];
    const app = createApp(() => Promise.resolve(mockGames));
    await app.locals.refresh();
    const res = await request(app).get('/api/games');
    expect(res.status).toBe(200);
    expect(res.body.games).toHaveLength(1);
    expect(res.body.games[0].trend).toBe('same');
    expect(res.body.lastUpdated).toBeDefined();
  });

  it('sets trend to up when playerCount increased since last refresh', async () => {
    const rounds = [
      [{ universeId: 1, name: 'G', playerCount: 100, creatorName: 'D', thumbnailUrl: null }],
      [{ universeId: 1, name: 'G', playerCount: 200, creatorName: 'D', thumbnailUrl: null }],
    ];
    let call = 0;
    const app = createApp(() => Promise.resolve(rounds[call++]));
    await app.locals.refresh();
    await app.locals.refresh();
    const res = await request(app).get('/api/games');
    expect(res.body.games[0].trend).toBe('up');
  });

  it('sets trend to down when playerCount decreased since last refresh', async () => {
    const rounds = [
      [{ universeId: 1, name: 'G', playerCount: 500, creatorName: 'D', thumbnailUrl: null }],
      [{ universeId: 1, name: 'G', playerCount: 300, creatorName: 'D', thumbnailUrl: null }],
    ];
    let call = 0;
    const app = createApp(() => Promise.resolve(rounds[call++]));
    await app.locals.refresh();
    await app.locals.refresh();
    const res = await request(app).get('/api/games');
    expect(res.body.games[0].trend).toBe('down');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
npx jest tests/server.test.js -v
```
Expected: FAIL — "Cannot find module '../server'"

- [ ] **Step 3: Implement server.js**

Create `server.js`:

```js
const express = require('express');
const path = require('path');
const { fetchTopGames } = require('./roblox');

const REFRESH_MS = 5 * 60 * 1000;

function createApp(fetcher = fetchTopGames) {
  const app = express();
  app.use(express.static(path.join(__dirname, 'public')));

  let cache = { games: [], lastUpdated: null };
  let prevCounts = {};

  async function refresh() {
    const fresh = await fetcher();
    const withTrend = fresh.map(g => {
      const prev = prevCounts[g.universeId];
      const trend =
        prev == null ? 'same'
        : g.playerCount > prev ? 'up'
        : g.playerCount < prev ? 'down'
        : 'same';
      return { ...g, trend };
    });
    prevCounts = Object.fromEntries(fresh.map(g => [g.universeId, g.playerCount]));
    cache = { games: withTrend, lastUpdated: new Date().toISOString() };
  }

  app.locals.refresh = refresh;

  app.get('/api/games', (_req, res) => {
    res.json(cache);
  });

  return app;
}

if (require.main === module) {
  const app = createApp();
  app.locals.refresh().catch(console.error);
  setInterval(() => app.locals.refresh().catch(console.error), REFRESH_MS);
  app.listen(3000, () => console.log('Running at http://localhost:3000'));
}

module.exports = { createApp };
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx jest tests/server.test.js -v
```
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add server.js tests/server.test.js
git commit -m "feat: Express server with 5-min cache and trend calculation"
```

---

### Task 4: Frontend HTML

**Files:**
- Create: `public/index.html`

- [ ] **Step 1: Create the public directory and index.html**

```bash
mkdir -p /Users/jyclaude/claude-workspace/projects/jayden-test/public
```

Create `public/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Roblox Live Leaderboard</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header>
    <h1>Roblox Live Leaderboard</h1>
    <div class="ticker">
      <span id="last-updated">Loading...</span>
      <span id="countdown"></span>
    </div>
  </header>
  <main>
    <table id="leaderboard">
      <thead>
        <tr>
          <th>#</th>
          <th></th>
          <th>Game</th>
          <th>Players</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="leaderboard-body">
        <tr><td colspan="5" class="loading">Fetching data...</td></tr>
      </tbody>
    </table>
  </main>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add public/index.html
git commit -m "feat: frontend HTML leaderboard structure"
```

---

### Task 5: Frontend CSS

**Files:**
- Create: `public/style.css`

- [ ] **Step 1: Create style.css**

Create `public/style.css`:

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #0f0f13;
  color: #e0e0e0;
  font-family: 'Segoe UI', system-ui, sans-serif;
  min-height: 100vh;
}

header {
  background: #1a1a24;
  border-bottom: 2px solid #e50000;
  padding: 1.2rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.03em;
}

.ticker {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.8rem;
  color: #888;
  gap: 2px;
}

#countdown { color: #e50000; font-weight: 600; }

main { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }

table {
  width: 100%;
  border-collapse: collapse;
  background: #1a1a24;
  border-radius: 10px;
  overflow: hidden;
}

thead th {
  background: #12121a;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #666;
}

tbody tr {
  border-bottom: 1px solid #24242e;
  transition: background 0.15s;
}

tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: #20202c; }

td { padding: 0.7rem 1rem; vertical-align: middle; }

.rank {
  font-size: 1rem;
  font-weight: 700;
  width: 48px;
  text-align: center;
}

.rank-1 { color: #ffd700; }
.rank-2 { color: #c0c0c0; }
.rank-3 { color: #cd7f32; }

.thumb-cell { width: 60px; }

.thumb-cell img {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  object-fit: cover;
  background: #2a2a36;
}

.game-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #fff;
}

.creator-name {
  font-size: 0.75rem;
  color: #666;
  margin-top: 2px;
}

.player-count {
  font-size: 1rem;
  font-weight: 700;
  color: #00d4aa;
  text-align: right;
}

.trend { font-size: 1.2rem; text-align: center; width: 40px; }
.trend-up { color: #00c853; }
.trend-down { color: #e53935; }
.trend-same { color: #444; }

.loading { text-align: center; padding: 3rem; color: #666; }
```

- [ ] **Step 2: Commit**

```bash
git add public/style.css
git commit -m "feat: dark theme CSS for leaderboard"
```

---

### Task 6: Frontend JavaScript

**Files:**
- Create: `public/app.js`

- [ ] **Step 1: Create app.js**

Create `public/app.js`:

```js
const REFRESH_MS = 5 * 60 * 1000;
let nextRefresh = Date.now() + REFRESH_MS;

function formatCount(n) {
  return n.toLocaleString();
}

function trendHtml(trend) {
  if (trend === 'up') return '<span class="trend trend-up" title="Increased">&#8593;</span>';
  if (trend === 'down') return '<span class="trend trend-down" title="Decreased">&#8595;</span>';
  return '<span class="trend trend-same">&mdash;</span>';
}

function rankClass(rank) {
  if (rank === 1) return 'rank rank-1';
  if (rank === 2) return 'rank rank-2';
  if (rank === 3) return 'rank rank-3';
  return 'rank';
}

function renderLeaderboard(data) {
  const tbody = document.getElementById('leaderboard-body');
  const lastUpdated = document.getElementById('last-updated');

  if (data.lastUpdated) {
    const d = new Date(data.lastUpdated);
    lastUpdated.textContent = 'Updated ' + d.toLocaleTimeString();
  }

  if (!data.games || data.games.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="loading">No data available.</td></tr>';
    return;
  }

  tbody.innerHTML = data.games.map((g, i) => {
    const rank = i + 1;
    const thumb = g.thumbnailUrl
      ? `<img src="${g.thumbnailUrl}" alt="${g.name}" loading="lazy" />`
      : '';
    return `<tr>
      <td><span class="${rankClass(rank)}">#${rank}</span></td>
      <td class="thumb-cell">${thumb}</td>
      <td>
        <div class="game-name">${g.name}</div>
        <div class="creator-name">${g.creatorName}</div>
      </td>
      <td class="player-count">${formatCount(g.playerCount)}</td>
      <td>${trendHtml(g.trend)}</td>
    </tr>`;
  }).join('');
}

function updateCountdown() {
  const remaining = Math.max(0, nextRefresh - Date.now());
  const m = Math.floor(remaining / 60000);
  const s = Math.floor((remaining % 60000) / 1000);
  document.getElementById('countdown').textContent =
    `Next update in ${m}:${String(s).padStart(2, '0')}`;
}

async function loadData() {
  try {
    const res = await fetch('/api/games');
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    renderLeaderboard(data);
    nextRefresh = Date.now() + REFRESH_MS;
  } catch (e) {
    console.error('Failed to load data:', e);
  }
}

loadData();
setInterval(loadData, REFRESH_MS);
setInterval(updateCountdown, 1000);
updateCountdown();
```

- [ ] **Step 2: Commit**

```bash
git add public/app.js
git commit -m "feat: frontend JS — render leaderboard, countdown timer, auto-refresh"
```

---

### Task 7: Full Test Run and README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Run all tests**

```bash
cd /Users/jyclaude/claude-workspace/projects/jayden-test
npx jest -v
```
Expected: PASS — 5 tests across roblox.test.js and server.test.js

- [ ] **Step 2: Create README.md**

Create `README.md`:

```markdown
# Roblox Live Leaderboard

Tracks the most popular Roblox games by live player count, updating every 5 minutes.

## Run

```bash
npm install
node server.js
```

Open http://localhost:3000
```

- [ ] **Step 3: Commit README**

```bash
git add README.md
git commit -m "docs: add README with run instructions"
```
