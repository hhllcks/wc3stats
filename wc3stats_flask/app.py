import os
import datetime
import json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from flask_assets import Bundle, Environment
from dotenv import load_dotenv
from .replay_handler import load_replay, get_statistics
from .stats_layouter import get_stats_content
from .exceptions import ImproperlyConfigured
app = Flask(__name__)

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)

try:
    app.secret_key = os.environ["SECRET_KEY"]
except KeyError:
    raise ImproperlyConfigured("SECRET KEY not set in .env:")

bundles = {
    'js': Bundle(
        'js/handlers.js',
        'js/upload.js',
        output='gen/all.js'),
    'css': Bundle(
        'css/style.css',
        output='gen/all.css'),
}

assets = Environment(app)

assets.register(bundles)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        replay_files = request.files.getlist("replays")
        session['dates'] = json.loads(request.form['dates'])
        session['playerName'] = request.form['playerName']

        g.replays = []

        for replay_file in replay_files:
            if replay_file.filename in session['dates']:
                timestamp = session['dates'][replay_file.filename]
                replay = load_replay(replay_file, replay_file.filename, timestamp/1000.0)
                g.replays.append(replay)
                (g.stats_raw, g.rep_list) = get_statistics(g.replays, [session['playerName']])

        g.stats_content = get_stats_content(g.stats_raw,g.rep_list)
        return render_template("stats_only.html")
    else:
        return redirect(url_for('home'))

@app.route('/stats')
def stats():
    return render_template("stats.html")