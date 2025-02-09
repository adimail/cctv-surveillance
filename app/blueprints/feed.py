import os
from flask import Blueprint, render_template, url_for, current_app, jsonify

feed = Blueprint("feed", __name__)

@feed.route("/")
def live_feed():
    try:
        static_folder = current_app.static_folder
        if static_folder is None:
            return jsonify({"error": "Static folder is not configured."}), 500

        videos_folder = os.path.join(static_folder, "videos")
        if not os.path.exists(videos_folder):
            return jsonify({"error": "Videos folder not found."}), 404

        video_files = [
            f for f in os.listdir(videos_folder)
            if f.lower().endswith(('.mp4', '.webm', '.ogg'))
        ]

        if not video_files:
            return jsonify({"error": "No video files found."}), 404

        video_urls = [url_for('static', filename=f"videos/{video}") for video in video_files]

        return render_template("feed.html", video_urls=video_urls)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
