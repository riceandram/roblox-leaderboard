# Roblox Player Count Tracker — Design

**Date:** 2026-05-14  
**Project:** jayden-test

## Overview

A local website that displays a live leaderboard of the most popular Roblox games sorted by current player count, with trend indicators and a 5-minute auto-refresh.

## Architecture

Two-layer local app:

- **Backend** (`server.js`) — Node.js/Express server that proxies Roblox's public API (avoids browser CORS restrictions), caches results, and exposes `GET /api/games`.
- **Frontend** (`public/`) — Static HTML/CSS/JS that calls the local server, renders the leaderboard, and shows a live countdown to the next refresh.

## Data Flow

1. Server starts → immediately fetches top 50 games from Roblox sorted by player count.
2. Batch-fetches thumbnails for all 50 games.
3. Caches results in memory with previous-poll snapshot for trend calculation.
4. Serves data at `GET /api/games`.
5. Re-fetches every 5 minutes, updates cache, calculates new trend arrows.
6. Frontend polls `/api/games` on load and every 5 minutes, re-renders smoothly.

## Roblox API Endpoints

- `GET https://games.roblox.com/v1/games/list?SortType=2&MaxRows=50` — top games by player count
- `GET https://thumbnails.roblox.com/v1/games/icons?universeIds=...&size=150x150&format=Png` — batch thumbnails

## Display (Standard Tier)

Each leaderboard row:

```
[rank badge]  [thumbnail]  [game name]        [player count]  [trend ↑↓]
```

- Rank badge: #1, #2, #3 ... styled gold/silver/bronze for top 3
- Thumbnail: 150×150 icon from Roblox CDN
- Player count: formatted with commas (e.g. 142,301)
- Trend: ↑ green if count increased since last poll, ↓ red if decreased, — gray if same

Top of page: live countdown timer ("Next update in 4:32").

## File Structure

```
jayden-test/
├── server.js          # Express backend, Roblox proxy, 5-min cache
├── package.json
├── public/
│   ├── index.html     # Leaderboard page
│   ├── style.css      # Dark theme, responsive
│   └── app.js         # Fetch /api/games, render, countdown timer
└── docs/plans/
    └── 2026-05-14-roblox-tracker-design.md
```

## Tech Stack

- Node.js + Express (backend)
- Vanilla JS, HTML, CSS (frontend — no framework needed)
- `node-fetch` or built-in `fetch` (Node 18+) for Roblox API calls

## Running Locally

```bash
npm install
node server.js
# Open http://localhost:3000
```
