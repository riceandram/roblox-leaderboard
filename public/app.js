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
