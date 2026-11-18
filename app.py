from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_tables, connect_db

app = Flask(__name__)

# Hemlig nyckel för sessioner
app.secret_key = "byt-denna-nyckel-till-en-hemlig-strang"

# Skapa databastabellerna
create_tables()


# Skapa testanvändare
def create_test_users():
    conn = connect_db()
    cursor = conn.cursor()

    test_users = [
        ("farskalle1", "password123"),
        ("farskalle2", "password456")
    ]

    for username, password in test_users:
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )

        if cursor.fetchone() is None:
            hashed_password = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

    conn.commit()
    conn.close()


create_test_users()


# Startsidan
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")


# Inloggning
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("home"))

        flash("Fel användarnamn eller lösenord!")

    return render_template("login.html")


# Logga ut
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
