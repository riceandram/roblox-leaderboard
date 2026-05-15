import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from flask import Flask, jsonify
from roblox import fetch_top_games

REFRESH_SECONDS = 2 * 60
HISTORY_MAX = 12


def create_app(fetcher=fetch_top_games):
    app = Flask(__name__, static_folder="public", static_url_path="")

    cache = {"games": [], "lastUpdated": None}
    cache_lock = threading.Lock()
    prev_counts = {}
    prev_ranks = {}
    history = defaultdict(list)

    def refresh():
        nonlocal prev_counts, prev_ranks
        fresh = fetcher()
        with_meta = []
        for i, g in enumerate(fresh):
            uid = g["universeId"]
            rank = i + 1
            prev = prev_counts.get(uid)

            if prev is None:
                trend = "same"
            elif g["playerCount"] > prev:
                trend = "up"
            elif g["playerCount"] < prev:
                trend = "down"
            else:
                trend = "same"

            prev_rank = prev_ranks.get(uid)
            rank_change = (prev_rank - rank) if prev_rank is not None else 0

            hist = history[uid]
            hist.append(g["playerCount"])
            if len(hist) > HISTORY_MAX:
                hist.pop(0)

            with_meta.append({**g, "trend": trend, "rankChange": rank_change, "history": list(hist)})

        prev_counts = {g["universeId"]: g["playerCount"] for g in fresh}
        prev_ranks = {g["universeId"]: i + 1 for i, g in enumerate(fresh)}

        with cache_lock:
            cache["games"] = with_meta
            cache["lastUpdated"] = datetime.now(timezone.utc).isoformat()

    app.config["REFRESH"] = refresh

    @app.route("/api/games")
    def api_games():
        with cache_lock:
            return jsonify(dict(cache))

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


def _start_scheduler(app):
    def loop():
        while True:
            time.sleep(REFRESH_SECONDS)
            with app.app_context():
                try:
                    app.config["REFRESH"]()
                except Exception as e:
                    print(f"Refresh error: {e}")
    t = threading.Thread(target=loop, daemon=True)
    t.start()


if __name__ == "__main__":
    app = create_app()
    app.config["REFRESH"]()
    _start_scheduler(app)
    app.run(host="0.0.0.0", port=3000, debug=False)
