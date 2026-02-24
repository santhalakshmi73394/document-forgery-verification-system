from flask import Flask, render_template, redirect, session, send_from_directory
from routes.verify_routes import verify_bp
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
UPLOAD_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))

app = Flask(
    __name__,
    template_folder=FRONTEND_FOLDER,
    static_folder=FRONTEND_FOLDER
)

# 🔐 Secret key for session
app.secret_key = "supersecretkey"

app.register_blueprint(verify_bp)


# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/admin")
def admin_dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("admin.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# Serve uploaded files properly
@app.route("/uploads/<path:filename>")
def uploaded_files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)