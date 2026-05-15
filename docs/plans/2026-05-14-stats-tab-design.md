# Stats Tab Design

**Date:** 2026-05-14

## Overview

Add a second tab to the Roblox leaderboard. Clicking "Stats" switches the view to a rich stats page computed from already-loaded game data — no extra API calls, no refresh.

## Tab System

Two tab buttons above the main content area. Active tab gets a Roblox-red underline accent. Switching is pure JS: toggle `active` class on panels. No page reload, no network call.

Panels:
- `#leaderboard-panel` — existing table (active by default)
- `#stats-panel` — new stats view

## Stats Tab Sections

### 1. Overview Cards (top row)

Five glowing stat cards:
- 🔥 Total Online — sum of all 50 game playerCounts
- 📊 Average — mean playerCount per game
- 🎮 Games Tracked — count (50)
- 📈 Rising — count of games with trend="up"
- 📉 Falling — count of games with trend="down"

### 2. Top 3 Podium

Gold/silver/bronze podium with #2 left, #1 center (taller), #3 right. Each position shows thumbnail, game name, and player count.

### 3. Player Distribution Bar Chart

Horizontal bar for each of the 50 games. Bar width proportional to #1 game's playerCount. Top 3 bars: gold/silver/bronze. Rest: teal. Game name left, count right.

### 4. Highlight Cards (bottom row)

- 👑 King of the Server — #1 game with thumbnail, name, count
- 🏗️ Top Creator — creator name with the most games in the top 50, with game count

## Data Flow

All stats computed client-side in `renderStats(data)` from the same `/api/games` payload. Called alongside `renderLeaderboard(data)` in `loadData()`.

## Files Changed

- `public/index.html` — add tab nav, wrap table in panel, add stats panel structure
- `public/style.css` — tab styles, stat cards, podium, bar chart, highlight cards
- `public/app.js` — tab switching, `renderStats()` function
