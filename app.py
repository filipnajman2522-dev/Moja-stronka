from flask import Flask, request, redirect, session, render_template_string
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Sekret pobierany ze zmiennej środowiskowej
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


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


LOGIN_HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FilipHub - Logowanie</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #080808;
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.box {
    width: 340px;
    padding: 30px;
    background: #121212;
    border-radius: 20px;
    box-shadow: 0 0 35px #00ff8840;
    text-align: center;
}

h1 {
    color: #00ff88;
}

input, button {
    width: 100%;
    padding: 13px;
    margin: 7px 0;
    border-radius: 9px;
}

input {
    background: #080808;
    border: 1px solid #333;
    color: white;
}

button {
    background: #00ff88;
    border: 0;
    font-weight: bold;
    cursor: pointer;
}

a {
    color: #00ff88;
}

.msg {
    margin: 15px 0;
}
</style>
</head>

<body>
<div class="box">

<h1>🔐 {{ title }}</h1>

<div class="msg">{{ msg }}</div>

<form method="POST">

<input
    name="username"
    placeholder="Nazwa użytkownika"
    required
>

<input
    name="password"
    type="password"
    placeholder="Hasło"
    required
>

<button>{{ button }}</button>

</form>

<p>
{% if register %}
Masz konto?
<a href="/">Zaloguj się</a>
{% else %}
Nie masz konta?
<a href="/register">Zarejestruj się</a>
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
        LOGIN_HTML,
        title="Logowanie",
        button="ZALOGUJ SIĘ",
        register=False,
        msg=msg
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
                        (
                            username,
                            generate_password_hash(password)
                        )
                    )

                return redirect("/")

            except sqlite3.IntegrityError:

                msg = "❌ Taki użytkownik już istnieje"

    return render_template_string(
        LOGIN_HTML,
        title="Rejestracja",
        button="UTWÓRZ KONTO",
        register=True,
        msg=msg
    )


@app.route("/panel")
def panel():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    return f"""
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>FilipHub - Panel</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #080808;
    color: white;
    font-family: Arial, sans-serif;
}}

.nav {{
    height: 70px;
    background: #111;
    border-bottom: 1px solid #222;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 25px;
}}

.logo {{
    color: #00ff88;
    font-size: 24px;
    font-weight: bold;
}}

.logout {{
    color: white;
    text-decoration: none;
    background: #222;
    padding: 10px 15px;
    border-radius: 10px;
}}

.container {{
    max-width: 900px;
    margin: 50px auto;
    padding: 20px;
}}

.welcome {{
    background: #121212;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 0 30px #00ff8820;
}}

.welcome h1 {{
    color: #00ff88;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 20px;
}}

.card {{
    background: #121212;
    border: 1px solid #222;
    border-radius: 15px;
    padding: 20px;
}}

.card h2 {{
    color: #00ff88;
}}

.status {{
    color: #00ff88;
    font-weight: bold;
}}

</style>

</head>

<body>

<div class="nav">

<div class="logo">
🔥 FilipHub
</div>

<a class="logout" href="/logout">
Wyloguj
</a>

</div>


<div class="container">

<div class="welcome">

<h1>
Witaj, {username}! 👋
</h1>

<p>
Właśnie znajdujesz się w swoim panelu użytkownika.
</p>

<p>
Status:
<span class="status">● ZALOGOWANY</span>
</p>

</div>


<div class="cards">

<div class="card">

<h2>👤 Konto</h2>

<p>
Użytkownik: <b>{username}</b>
</p>

</div>


<div class="card">

<h2>🔐 Bezpieczeństwo</h2>

<p>
Hasło jest przechowywane jako hash.
</p>

</div>


<div class="card">

<h2>🌐 Serwer</h2>

<p>
FilipHub działa online.
</p>

</div>

</div>

</div>

</body>
</html>
"""


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
