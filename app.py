from flask import Flask, request, redirect, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zmien-to-na-dlugi-losowy-sekret"

def db():
    return sqlite3.connect("users.db")

with db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Login</title>
<style>
body {
    background:#080808;
    color:white;
    font-family:Arial;
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:100vh;
}
.box {
    width:320px;
    padding:30px;
    background:#121212;
    border-radius:20px;
    box-shadow:0 0 35px #00ff8840;
    text-align:center;
}
h1 { color:#00ff88; }
input,button {
    width:100%;
    padding:13px;
    margin:7px 0;
    border-radius:9px;
    box-sizing:border-box;
}
input {
    background:#080808;
    border:1px solid #333;
    color:white;
}
button {
    background:#00ff88;
    border:0;
    font-weight:bold;
}
a { color:#00ff88; }
.msg { margin:15px 0; }
</style>
</head>
<body>
<div class="box">
<h1>🔐 {{ title }}</h1>
<div class="msg">{{ msg }}</div>

<form method="POST">
<input name="username" placeholder="Nazwa użytkownika" required>
<input name="password" type="password" placeholder="Hasło" required>
<button>{{ button }}</button>
</form>

<p>
{% if register %}
Masz konto? <a href="/">Zaloguj się</a>
{% else %}
Nie masz konta? <a href="/register">Zarejestruj się</a>
{% endif %}
</p>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with db() as con:
            user = con.execute(
                "SELECT password FROM users WHERE username=?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user[0], password):
            session["username"] = username
            return redirect("/panel")

        msg = "❌ Błędny login lub hasło"

    return render_template_string(
        HTML, title="Logowanie", button="ZALOGUJ SIĘ",
        register=False, msg=msg
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if len(password) < 6:
            msg = "❌ Hasło musi mieć minimum 6 znaków"
        else:
            try:
                with db() as con:
                    con.execute(
                        "INSERT INTO users(username,password) VALUES(?,?)",
                        (username, generate_password_hash(password))
                    )
                return redirect("/")
            except sqlite3.IntegrityError:
                msg = "❌ Taki użytkownik już istnieje"

    return render_template_string(
        HTML, title="Rejestracja", button="UTWÓRZ KONTO",
        register=True, msg=msg
    )

@app.route("/panel")
def panel():
    if "username" not in session:
        return redirect("/")

    return f"""
    <body style="background:#080808;color:white;text-align:center;
                 font-family:Arial;padding-top:100px">
        <h1 style="color:#00ff88">🔥 Witaj, {session["username"]}!</h1>
        <p>Jesteś zalogowany.</p>
        <a href="/logout" style="color:#00ff88">Wyloguj</a>
    </body>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(host="0.0.0.0", port=8080)
