from flask import Flask, request, jsonify
from pytube import YouTube
from pytube.exceptions import PytubeError
from uuid import uuid4
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # CORS var palīdzēt POST testos no browsera / Postman

# Route pārbaude
@app.route("/routes", methods=["GET"])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": sorted(rule.methods),
            "path": str(rule)
        })
    return jsonify(routes)

# Vienkāršs POST tests
@app.route("/test-post", methods=["POST"])
def test_post():
    return jsonify({"success": True, "message": "POST works"})

# Root GET
@app.route("/", methods=["GET"])
def index():
    return "YouTube Audio API is running!"

# Galvenais POST endpoint
@app.route("/download", methods=["POST"])
def download_audio():
    app.logger.info("POST /download received")
    data = request.get_json()

    if not data:
        app.logger.error("No JSON received")
        return jsonify({"error": "Invalid JSON"}), 400

    video_url = data.get("url")
    if not video_url:
        app.logger.error("Missing 'url' in JSON")
        return jsonify({"error": "URL is required"}), 400

    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        filename = f"{uuid4().hex}.mp3"
        audio_stream.download(filename=filename)

        app.logger.info(f"Downloaded: {filename}")
        return jsonify({
            "message": "Audio downloaded successfully",
            "title": yt.title,
            "filename": filename
        }), 200

    except PytubeError as e:
        app.logger.error(f"Pytube error: {e}")
        return jsonify({"error": "Failed to process YouTube URL"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
