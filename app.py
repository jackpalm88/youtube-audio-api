from flask import Flask, request, jsonify
from pytube import YouTube
import os
from uuid import uuid4

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "YouTube Audio API is running!"

@app.route("/download", methods=["POST"])
def download_audio():
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        filename = f"{uuid4().hex}.mp3"
        audio_stream.download(filename=filename)
        
        return jsonify({
            "message": "Audio downloaded successfully",
            "title": yt.title,
            "filename": filename
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
