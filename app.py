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
        ("cjutegirl", "password123"),
        ("boiboi", "password456")
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


# Visa alla diskussionstrådar
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topics.*, users.username
        FROM topics
        JOIN users ON topics.user_id = users.id
        ORDER BY topics.created_at DESC
    """)

    topics = cursor.fetchall()
    conn.close()

    return render_template("index.html", topics=topics)


# Skapa en ny diskussionstråd
@app.route("/create_topic", methods=["GET", "POST"])
def create_topic():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO topics (title, user_id) VALUES (?, ?)",
            (title, session["user_id"])
        )

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("create_topic.html")

if __name__ == "__main__":
    app.run(debug=True)
