#!/usr/bin/env python3
"""
CloudSync Core - main.py
Cross-platform (Windows + Linux)
CLI launcher + temporary localhost web setup
Uses rclone for trusted, efficient syncing
"""

import os
import json
import time
import threading
import subprocess
import webbrowser
from flask import Flask, request, render_template_string
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================= CONFIG PATHS =================

def get_config_dir():
    if os.name == "nt":
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "CloudSyncLite")
    else:
        base = os.path.join(os.path.expanduser("~"), ".config")
        path = os.path.join(base, "cloudsync-lite")
    os.makedirs(path, exist_ok=True)
    return path

CONFIG_DIR = get_config_dir()
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "local_folder": "",
    "remote_name": "gdrive",
    "remote_subpath": "",
    "mode": "timer",
    "interval_minutes": 30
}

# ================= WEB UI =================

app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<title>CloudSync Setup</title>
<style>
body{background:#020617;color:#e2e8f0;font-family:sans-serif}
.box{max-width:500px;margin:40px auto;background:#0f172a;padding:20px;border-radius:12px}
input,select{width:100%;padding:8px;margin-top:8px;background:#020617;color:#fff;border:1px solid #1f2937;border-radius:6px}
button{margin-top:16px;width:100%;padding:10px;background:#38bdf8;border:none;border-radius:999px;font-weight:bold}
</style>
</head>
<body>
<div class="box">
<h2>CloudSync Setup</h2>
<form method="post">
<label>Folder to sync</label>
<input name="local_folder" value="{{local_folder}}" required>

<label>Rclone remote name</label>
<input name="remote_name" value="{{remote_name}}" required>

<label>Remote subfolder (optional)</label>
<input name="remote_subpath" value="{{remote_subpath}}">

<label>Mode</label>
<select name="mode">
  <option value="timer" {% if mode=='timer' %}selected{% endif %}>Timer</option>
  <option value="realtime" {% if mode=='realtime' %}selected{% endif %}>Realtime</option>
</select>

<label>Interval (minutes)</label>
<input type="number" name="interval_minutes" value="{{interval_minutes}}">

<button type="submit">Save</button>
{% if saved %}<p>Saved. You can close this tab.</p>{% endif %}
</form>
</div>
</body>
</html>
"""


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


@app.route("/", methods=["GET", "POST"])
def setup_page():
    cfg = load_config()
    saved = False
    if request.method == "POST":
        cfg["local_folder"] = request.form["local_folder"]
        cfg["remote_name"] = request.form["remote_name"]
        cfg["remote_subpath"] = request.form["remote_subpath"]
        cfg["mode"] = request.form["mode"]
        cfg["interval_minutes"] = int(request.form.get("interval_minutes", 30))
        save_config(cfg)
        saved = True
    return render_template_string(HTML_UI, saved=saved, **cfg)


def start_web_ui():
    threading.Timer(1, lambda: webbrowser.open("http://127.0.0.1:8765")).start()
    app.run(port=8765, debug=False)

# ================= SYNC ENGINE =================


def build_remote(cfg):
    base = os.path.basename(os.path.abspath(cfg["local_folder"]))
    sub = cfg["remote_subpath"] or base
    return f"{cfg['remote_name']}:{sub}"


def run_sync(cfg):
    if not cfg["local_folder"]:
        print("No folder configured.")
        return

    remote = build_remote(cfg)
    print(f"Syncing -> {remote}")

    subprocess.run([
        "rclone", "sync",
        cfg["local_folder"],
        remote,
        "--fast-list",
        "--transfers", "2",
        "--checkers", "2"
    ])


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, cfg):
        self.cfg = cfg
        self.timer = None

    def on_any_event(self, event):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(3, lambda: run_sync(self.cfg))
        self.timer.start()


def realtime_loop(cfg):
    obs = Observer()
    obs.schedule(ChangeHandler(cfg), cfg["local_folder"], recursive=True)
    obs.start()
    print("Realtime sync active...")
    while True:
        time.sleep(1)


def timer_loop(cfg):
    print(f"Sync every {cfg['interval_minutes']} minutes")
    while True:
        run_sync(cfg)
        time.sleep(cfg["interval_minutes"] * 60)

# ================= CLI MENU =================


def menu():
    while True:
        os.system('cls' if os.name=='nt' else 'clear')
        cfg = load_config()
        print("=============================")
        print("      CloudSync Lite")
        print("=============================")
        print("1. Open Web Setup")
        print("2. Start Sync Engine")
        print("3. Sync Now")
        print("4. Exit")
        choice = input("Select: ")

        if choice == '1':
            start_web_ui()
        elif choice == '2':
            if cfg['mode'] == 'realtime':
                realtime_loop(cfg)
            else:
                timer_loop(cfg)
        elif choice == '3':
            run_sync(cfg)
        elif choice == '4':
            break


if __name__ == '__main__':
    menu()