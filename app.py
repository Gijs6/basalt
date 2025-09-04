from flask import Flask, render_template, request, redirect, url_for, session
import os
from datetime import datetime, timezone, timedelta
from functools import wraps
from dotenv import load_dotenv

from db.models import db, Entry

load_dotenv(override=True)

AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")

if not AUTH_PASSWORD:
    raise NameError("Please set an password.")

app = Flask(__name__)

app.secret_key = os.urandom(30)
app.permanent_session_lifetime = timedelta(days=7)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///basalt.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


with app.app_context():
    db.create_all()


def login_excluded(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged_in"):
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


@app.before_request
def require_login():
    allowed_routes = ["login", "static"]
    if request.endpoint not in allowed_routes and not session.get("logged_in"):
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
@login_excluded
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if AUTH_PASSWORD and password == AUTH_PASSWORD:
            session["logged_in"] = True
            session.permanent = True
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    return redirect(url_for("list_entries"))


@app.route("/entries")
def list_entries():
    entries = Entry.query.order_by(Entry.dt_made.desc()).all()
    return render_template("list.html", entries=entries)


@app.route("/entries/<string:entry_id>")
def view_edit_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    return render_template("view_edit.html", entry=entry)


@app.route("/new", methods=["POST"])
def new_entry():
    title = "title"
    content = "content"
    now = datetime.now(timezone.utc)
    entry = Entry(title=title, content=content, dt_made=now, dt_updated=now)

    db.session.add(entry)
    db.session.commit()

    return redirect(url_for("view_edit_entry", entry_id=entry.id))


@app.route("/entries/<string:entry_id>/update", methods=["POST"])
def update_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)

    entry.title = request.form["title"].strip()
    entry.content = request.form["content"].strip()
    entry.dt_updated = datetime.now(timezone.utc)

    db.session.commit()

    return redirect(url_for("view_edit_entry", entry_id=entry.id))


@app.route("/entries/<string:entry_id>/delete", methods=["POST"])
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for("list_entries"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
