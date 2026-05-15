const REFRESH_MS = 5 * 60 * 1000;
let nextRefresh = Date.now() + REFRESH_MS;

function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatCount(n) {
  return n.toLocaleString();
}

function trendHtml(trend) {
  if (trend === 'up') return '<span class="trend trend-up" title="Increased since last refresh">&#8593;</span>';
  if (trend === 'down') return '<span class="trend trend-down" title="Decreased since last refresh">&#8595;</span>';
  return '<span class="trend trend-same">&mdash;</span>';
}

function rankClass(rank) {
  if (rank === 1) return 'rank rank-1';
  if (rank === 2) return 'rank rank-2';
  if (rank === 3) return 'rank rank-3';
  return 'rank';
}

// ── Tab switching ─────────────────────────────────────────────────────────────

function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = document.getElementById(btn.dataset.tab + '-panel');
      if (panel) panel.classList.add('active');
    });
  });
}

// ── Stats computation (pure — no DOM) ────────────────────────────────────────

function computeStats(games) {
  const totalPlayers = games.reduce((sum, g) => sum + g.playerCount, 0);
  const avgPlayers = Math.round(totalPlayers / games.length);
  const rising = games.filter(g => g.trend === 'up').length;
  const falling = games.filter(g => g.trend === 'down').length;

  const creatorCounts = {};
  for (const g of games) {
    creatorCounts[g.creatorName] = (creatorCounts[g.creatorName] || 0) + 1;
  }
  const topEntry = Object.entries(creatorCounts).sort((a, b) => b[1] - a[1])[0];
  const topCreator = topEntry ? { name: topEntry[0], count: topEntry[1] } : null;

  return { totalPlayers, avgPlayers, gamesCount: games.length, rising, falling, topCreator };
}

// ── Stats rendering ───────────────────────────────────────────────────────────

function renderStats(data) {
  if (!data.games || data.games.length === 0) return;
  const games = data.games;
  const s = computeStats(games);

  // Stat cards
  document.getElementById('stat-cards').innerHTML = `
    <div class="stat-card" style="--card-color:#e50000">
      <div class="stat-icon">🔥</div>
      <div class="stat-value">${formatCount(s.totalPlayers)}</div>
      <div class="stat-label">Total Online</div>
    </div>
    <div class="stat-card" style="--card-color:#00d4aa">
      <div class="stat-icon">📊</div>
      <div class="stat-value">${formatCount(s.avgPlayers)}</div>
      <div class="stat-label">Avg Per Game</div>
    </div>
    <div class="stat-card" style="--card-color:#7c6fff">
      <div class="stat-icon">🎮</div>
      <div class="stat-value">${s.gamesCount}</div>
      <div class="stat-label">Games Tracked</div>
    </div>
    <div class="stat-card" style="--card-color:#00c853">
      <div class="stat-icon">📈</div>
      <div class="stat-value">${s.rising}</div>
      <div class="stat-label">Rising</div>
    </div>
    <div class="stat-card" style="--card-color:#e53935">
      <div class="stat-icon">📉</div>
      <div class="stat-value">${s.falling}</div>
      <div class="stat-label">Falling</div>
    </div>
  `;

  // Podium — order: 2nd left, 1st centre, 3rd right
  const top3 = games.slice(0, 3);
  const podiumOrder = [top3[1], top3[0], top3[2]];
  const podiumRanks = [2, 1, 3];
  document.getElementById('podium').innerHTML = podiumOrder.map((g, i) => {
    if (!g) return '';
    const rank = podiumRanks[i];
    const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉';
    const thumb = g.thumbnailUrl
      ? `<img src="${esc(g.thumbnailUrl)}" alt="${esc(g.name)}" />`
      : '<div class="podium-img-placeholder"></div>';
    return `<div class="podium-item rank-${rank}">
      ${thumb}
      <div class="podium-name">${esc(g.name)}</div>
      <div class="podium-count">${formatCount(g.playerCount)}</div>
      <div class="podium-base">${medal}</div>
    </div>`;
  }).join('');

  // Bar chart
  const maxCount = games[0].playerCount || 1;
  document.getElementById('bar-chart').innerHTML = games.map((g, i) => {
    const pct = Math.max(1, Math.round((g.playerCount / maxCount) * 100));
    const cls = i < 3 ? ` top-${i + 1}` : '';
    return `<div class="bar-row${cls}">
      <div class="bar-label">${esc(g.name)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="bar-value">${formatCount(g.playerCount)}</div>
    </div>`;
  }).join('');

  // Highlight cards
  const king = games[0];
  const kingThumb = king.thumbnailUrl
    ? `<img src="${esc(king.thumbnailUrl)}" alt="${esc(king.name)}" />`
    : '<span class="hl-icon">👑</span>';

  document.getElementById('highlight-cards').innerHTML = `
    <div class="highlight-card">
      ${kingThumb}
      <div>
        <div class="hl-label">👑 King of the Server</div>
        <div class="hl-title">${esc(king.name)}</div>
        <div class="hl-sub">${formatCount(king.playerCount)} players</div>
      </div>
    </div>
    <div class="highlight-card">
      <span class="hl-icon">🏗️</span>
      <div>
        <div class="hl-label">🏗️ Top Creator</div>
        <div class="hl-title">${s.topCreator ? esc(s.topCreator.name) : '—'}</div>
        <div class="hl-sub">${s.topCreator ? `${s.topCreator.count} game${s.topCreator.count > 1 ? 's' : ''} in top ${s.gamesCount}` : ''}</div>
      </div>
    </div>
  `;
}

// ── Leaderboard rendering ─────────────────────────────────────────────────────

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
      ? `<img src="${esc(g.thumbnailUrl)}" alt="${esc(g.name)}" loading="lazy" />`
      : '';
    return `<tr>
      <td><span class="${rankClass(rank)}">#${rank}</span></td>
      <td class="thumb-cell">${thumb}</td>
      <td>
        <div class="game-name">${esc(g.name)}</div>
        <div class="creator-name">${esc(g.creatorName)}</div>
      </td>
      <td class="player-count">${formatCount(g.playerCount)}</td>
      <td>${trendHtml(g.trend)}</td>
    </tr>`;
  }).join('');
}

// ── Countdown ─────────────────────────────────────────────────────────────────

function updateCountdown() {
  const remaining = Math.max(0, nextRefresh - Date.now());
  const m = Math.floor(remaining / 60000);
  const s = Math.floor((remaining % 60000) / 1000);
  document.getElementById('countdown').textContent =
    `Next update in ${m}:${String(s).padStart(2, '0')}`;
}

// ── Data loading ──────────────────────────────────────────────────────────────

async function loadData() {
  const tbody = document.getElementById('leaderboard-body');
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const res = await fetch('/api/games', { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    renderLeaderboard(data);
    renderStats(data);
    nextRefresh = Date.now() + REFRESH_MS;
  } catch (e) {
    clearTimeout(timeout);
    console.error('Failed to load data:', e);
    tbody.innerHTML = '<tr><td colspan="5" class="loading error">Failed to load data. Retrying in 5 minutes...</td></tr>';
  }
}

// ── Boot ──────────────────────────────────────────────────────────────────────

initTabs();
loadData();
setInterval(loadData, REFRESH_MS);
setInterval(updateCountdown, 1000);
updateCountdown();
