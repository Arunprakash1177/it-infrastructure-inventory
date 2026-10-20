"""IT Infrastructure Inventory - a small Flask + SQLite learning project."""

import ipaddress
import os
import sqlite3

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

app = Flask(__name__)

# Flask needs a secret key to show one-time "flash" messages.
# This value is fine for learning, but never use a hard-coded key in real production.
app.secret_key = "learning-project-secret-key"

# The database is a single file that lives next to app.py.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
DATABASE = os.path.join(DATA_DIR, "inventory.db")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    """Open a connection to the database (once per request) and reuse it."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us read columns by name
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Close the database connection when the request is finished."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the 'servers' table if it does not exist yet."""
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS servers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname   TEXT NOT NULL UNIQUE,
            ip_address TEXT NOT NULL,
            os         TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


def get_server_or_404(server_id):
    """Fetch one server by id, or show a 'Not Found' page."""
    server = get_db().execute(
        "SELECT * FROM servers WHERE id = ?", (server_id,)
    ).fetchone()
    if server is None:
        abort(404)
    return server


def validate(hostname, ip_address, os_name):
    """Check the form values. Returns a list of error messages (empty = OK)."""
    errors = []
    if not hostname:
        errors.append("Hostname is required.")
    if not ip_address:
        errors.append("IP address is required.")
    else:
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            errors.append("IP address is not valid (example: 192.168.1.10).")
    if not os_name:
        errors.append("Operating system is required.")
    return errors


# ---------------------------------------------------------------------------
# Pages (routes)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Show the list of all servers."""
    servers = get_db().execute(
        "SELECT * FROM servers ORDER BY hostname"
    ).fetchall()
    return render_template("index.html", servers=servers)
#test

@app.route("/add", methods=["GET", "POST"])
def add_server():
    """GET: show the empty form.  POST: save the new server."""
    if request.method == "POST":
        hostname = request.form.get("hostname", "").strip()
        ip_address = request.form.get("ip_address", "").strip()
        os_name = request.form.get("os", "").strip()

        errors = validate(hostname, ip_address, os_name)
        if not errors:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO servers (hostname, ip_address, os) VALUES (?, ?, ?)",
                    (hostname, ip_address, os_name),
                )
                db.commit()
                flash(f"Server '{hostname}' was added.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                errors.append(f"A server named '{hostname}' already exists.")

        for message in errors:
            flash(message, "error")
        # Show the form again with what the user typed
        return render_template(
            "add.html", hostname=hostname, ip_address=ip_address, os_name=os_name
        )

    return render_template("add.html", hostname="", ip_address="", os_name="")
# test comment

@app.route("/server/<int:server_id>")
def server_detail(server_id):
    """Show the details of one server."""
    server = get_server_or_404(server_id)
    return render_template("detail.html", server=server)


@app.route("/server/<int:server_id>/edit", methods=["GET", "POST"])
def edit_server(server_id):
    """GET: show the form filled in.  POST: save the changes."""
    server = get_server_or_404(server_id)

    if request.method == "POST":
        hostname = request.form.get("hostname", "").strip()
        ip_address = request.form.get("ip_address", "").strip()
        os_name = request.form.get("os", "").strip()

        errors = validate(hostname, ip_address, os_name)
        if not errors:
            try:
                db = get_db()
                db.execute(
                    "UPDATE servers SET hostname = ?, ip_address = ?, os = ? WHERE id = ?",
                    (hostname, ip_address, os_name, server_id),
                )
                db.commit()
                flash(f"Server '{hostname}' was updated.", "success")
                return redirect(url_for("server_detail", server_id=server_id))
            except sqlite3.IntegrityError:
                errors.append(f"A server named '{hostname}' already exists.")

        for message in errors:
            flash(message, "error")
        return render_template(
            "edit.html",
            server=server,
            hostname=hostname,
            ip_address=ip_address,
            os_name=os_name,
        )

    return render_template(
        "edit.html",
        server=server,
        hostname=server["hostname"],
        ip_address=server["ip_address"],
        os_name=server["os"],
    )


@app.route("/server/<int:server_id>/delete", methods=["POST"])
def delete_server(server_id):
    """Delete a server. Only accepts POST so a link click cannot delete by accident."""
    server = get_server_or_404(server_id)
    db = get_db()
    db.execute("DELETE FROM servers WHERE id = ?", (server_id,))
    db.commit()
    flash(f"Server '{server['hostname']}' was deleted.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Start-up
# ---------------------------------------------------------------------------

# Make sure the table exists every time the application starts.
init_db()

if __name__ == "__main__":
    # 127.0.0.1 = only this computer can open the site. Port 5000 = the "door number".
    app.run(host="0.0.0.0", port=5000, debug=False)
