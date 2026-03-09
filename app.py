import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "filesecretkey456"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx", "xlsx", "zip", "mp3", "mp4"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(filepath):
    size = os.path.getsize(filepath)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def get_file_icon(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    icons = {
        "pdf": "📄", "png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️", "gif": "🖼️",
        "txt": "📝", "docx": "📃", "xlsx": "📊", "zip": "🗜️",
        "mp3": "🎵", "mp4": "🎬",
    }
    return icons.get(ext, "📁")


@app.route("/")
def index():
    files = []
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.isfile(filepath):
            files.append({
                "name": filename,
                "size": get_file_size(filepath),
                "icon": get_file_icon(filename),
            })
    return render_template("index.html", files=files)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected!", "error")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected!", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("File type not allowed!", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    flash(f'"{filename}" uploaded successfully!', "success")
    return redirect(url_for("index"))


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/delete/<filename>")
def delete(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'"{filename}" deleted.', "success")
    else:
        flash("File not found!", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
