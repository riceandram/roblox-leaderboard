import threading
import time
from datetime import datetime, timezone
from flask import Flask, jsonify
from roblox import fetch_top_games

REFRESH_SECONDS = 5 * 60


def create_app(fetcher=fetch_top_games):
    app = Flask(__name__, static_folder="public", static_url_path="")

    cache = {"games": [], "lastUpdated": None}
    cache_lock = threading.Lock()
    prev_counts = {}

    def refresh():
        nonlocal prev_counts
        fresh = fetcher()
        with_trend = []
        for g in fresh:
            prev = prev_counts.get(g["universeId"])
            if prev is None:
                trend = "same"
            elif g["playerCount"] > prev:
                trend = "up"
            elif g["playerCount"] < prev:
                trend = "down"
            else:
                trend = "same"
            with_trend.append({**g, "trend": trend})
        prev_counts = {g["universeId"]: g["playerCount"] for g in fresh}
        with cache_lock:
            cache["games"] = with_trend
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
