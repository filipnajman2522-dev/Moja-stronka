from flask import Flask, request, redirect, session, render_template_string
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-change-me"
)

DB = "users.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["username"] = username
            return redirect("/panel")

        message = "Nieprawidłowy login lub hasło."

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FilipHub — Logowanie</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background:
        radial-gradient(circle at top, #1e293b 0%, #0f172a 40%, #020617 100%);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-box {
    width: 380px;
    max-width: 92%;
    padding: 35px;
    background: rgba(15, 23, 42, 0.88);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    box-shadow: 0 25px 80px rgba(0,0,0,.45);
    backdrop-filter: blur(15px);
}

.logo {
    text-align: center;
    margin-bottom: 30px;
}

.logo h1 {
    margin: 0;
    font-size: 34px;
}

.logo p {
    color: #94a3b8;
}

input {
    width: 100%;
    padding: 14px;
    margin-bottom: 14px;
    border-radius: 12px;
    border: 1px solid #334155;
    background: #0f172a;
    color: white;
    outline: none;
}

input:focus {
    border-color: #6366f1;
}

button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: .2s;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(99,102,241,.3);
}

.message {
    color: #f87171;
    text-align: center;
    margin-top: 15px;
}

.register {
    text-align: center;
    margin-top: 22px;
    color: #94a3b8;
}

a {
    color: #818cf8;
    text-decoration: none;
}

</style>
</head>

<body>

<div class="login-box">

    <div class="logo">
        <h1>🔥 FilipHub</h1>
        <p>Witaj ponownie</p>
    </div>

    <form method="POST">

        <input
            type="text"
            name="username"
            placeholder="Nazwa użytkownika"
            required
        >

        <input
            type="password"
            name="password"
            placeholder="Hasło"
            required
        >

        <button type="submit">
            Zaloguj się
        </button>

    </form>

    {% if message %}
        <div class="message">{{ message }}</div>
    {% endif %}

    <div class="register">
        Nie masz konta?
        <a href="/register">Utwórz konto</a>
    </div>

</div>

</body>
</html>
""", message=message)


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3:
            message = "Nazwa użytkownika musi mieć minimum 3 znaki."

        elif len(password) < 6:
            message = "Hasło musi mieć minimum 6 znaków."

        else:

            conn = sqlite3.connect(DB)
            c = conn.cursor()

            try:

                hashed_password = generate_password_hash(password)

                c.execute(
                    """
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                    """,
                    (username, hashed_password)
                )

                conn.commit()
                conn.close()

                return redirect("/")

            except sqlite3.IntegrityError:

                conn.close()

                message = "Taki użytkownik już istnieje."

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FilipHub — Rejestracja</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background:
        radial-gradient(circle at top, #1e293b, #020617);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.box {
    width: 380px;
    max-width: 92%;
    padding: 35px;
    background: rgba(15,23,42,.9);
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,.08);
}

h1 {
    text-align: center;
}

input {
    width: 100%;
    padding: 14px;
    margin-bottom: 14px;
    border-radius: 12px;
    border: 1px solid #334155;
    background: #0f172a;
    color: white;
}

button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: white;
    font-weight: bold;
    cursor: pointer;
}

.message {
    color: #f87171;
    text-align: center;
    margin: 15px 0;
}

.bottom {
    text-align: center;
    margin-top: 20px;
    color: #94a3b8;
}

a {
    color: #818cf8;
}

</style>

</head>

<body>

<div class="box">

<h1>🔥 FilipHub</h1>

<p style="text-align:center;color:#94a3b8;">
    Utwórz swoje konto
</p>

<form method="POST">

<input
    type="text"
    name="username"
    placeholder="Nazwa użytkownika"
    required
>

<input
    type="password"
    name="password"
    placeholder="Hasło"
    required
>

<button type="submit">
    Utwórz konto
</button>

</form>

{% if message %}
<p class="message">{{ message }}</p>
{% endif %}

<div class="bottom">
    Masz już konto?
    <a href="/">Zaloguj się</a>
</div>

</div>

</body>
</html>
""", message=message)


# =========================
# PANEL
# =========================

@app.route("/panel")
def panel():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FilipHub — Dashboard</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #020617;
    color: white;
}

.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 240px;
    height: 100vh;
    background: #0f172a;
    border-right: 1px solid #1e293b;
    padding: 25px 15px;
}

.logo {
    font-size: 25px;
    font-weight: bold;
    padding: 10px;
    margin-bottom: 35px;
}

.menu-title {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    padding: 0 12px;
    margin-bottom: 10px;
}

.menu a {
    display: block;
    padding: 13px 15px;
    margin-bottom: 7px;
    border-radius: 10px;
    color: #cbd5e1;
    text-decoration: none;
    transition: .2s;
}

.menu a:hover,
.menu .active {
    background: #1e293b;
    color: white;
    transform: translateX(3px);
}

.logout {
    position: absolute;
    bottom: 25px;
    left: 15px;
    right: 15px;
}

.logout a {
    display: block;
    padding: 13px;
    border-radius: 10px;
    color: #f87171;
    text-decoration: none;
}

.logout a:hover {
    background: #2a1518;
}

.main {
    margin-left: 240px;
    padding: 35px;
    min-height: 100vh;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 35px;
}

.topbar h1 {
    margin: 0;
}

.user {
    background: #0f172a;
    border: 1px solid #1e293b;
    padding: 10px 15px;
    border-radius: 12px;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    background:
        linear-gradient(135deg, #1e1b4b, #312e81);
    border: 1px solid #4338ca;
    margin-bottom: 25px;
}

.hero h2 {
    font-size: 30px;
    margin-top: 0;
}

.hero p {
    color: #c7d2fe;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.card {
    background: #0f172a;
    border: 1px solid #1e293b;
    padding: 25px;
    border-radius: 18px;
    transition: .2s;
}

.card:hover {
    transform: translateY(-4px);
    border-color: #475569;
}

.card-icon {
    font-size: 28px;
    margin-bottom: 15px;
}

.card h3 {
    margin: 0 0 8px;
}

.card p {
    color: #94a3b8;
    line-height: 1.5;
}

.quick {
    margin-top: 25px;
    padding: 25px;
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 18px;
}

.quick h2 {
    margin-top: 0;
}

.quick a {
    display: inline-block;
    padding: 12px 18px;
    margin: 5px;
    background: #1e293b;
    border-radius: 10px;
    color: white;
    text-decoration: none;
    transition: .2s;
}

.quick a:hover {
    background: #334155;
}

@media (max-width: 850px) {

    .sidebar {
        position: relative;
        width: 100%;
        height: auto;
        border-right: none;
        border-bottom: 1px solid #1e293b;
    }

    .logo {
        text-align: center;
    }

    .logout {
        position: relative;
        left: auto;
        right: auto;
        bottom: auto;
        margin-top: 20px;
    }

    .main {
        margin-left: 0;
        padding: 20px;
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .topbar {
        display: block;
    }

    .user {
        display: inline-block;
        margin-top: 15px;
    }
}

</style>

</head>

<body>

<aside class="sidebar">

    <div class="logo">
        🔥 FilipHub
    </div>

    <div class="menu-title">
        Menu
    </div>

    <div class="menu">

        <a href="/panel" class="active">
            🏠 Dashboard
        </a>

        <a href="/profile">
            👤 Profil
        </a>

        <a href="/change-password">
            🔐 Zmień hasło
        </a>

    </div>

    <div class="logout">

        <a href="/logout">
            🚪 Wyloguj się
        </a>

    </div>

</aside>


<main class="main">

    <div class="topbar">

        <div>
            <h1>Dashboard</h1>
            <p style="color:#64748b;">
                Centrum Twojego konta
            </p>
        </div>

        <div class="user">
            👤 {{ username }}
        </div>

    </div>


    <section class="hero">

        <h2>
            Witaj, {{ username }}! 👋
        </h2>

        <p>
            Miło Cię widzieć w FilipHub.
            To jest Twoje centrum użytkownika.
        </p>

    </section>


    <div class="grid">

        <div class="card">

            <div class="card-icon">
                🚀
            </div>

            <h3>
                Nowe funkcje
            </h3>

            <p>
                FilipHub będzie stopniowo otrzymywał
                nowe możliwości.
            </p>

        </div>


        <div class="card">

            <div class="card-icon">
                🔐
            </div>

            <h3>
                Bezpieczeństwo
            </h3>

            <p>
                Twoje hasło jest przechowywane
                w bezpiecznej, zahashowanej formie.
            </p>

        </div>


        <div class="card">

            <div class="card-icon">
                ⚡
            </div>

            <h3>
                Szybki dostęp
            </h3>

            <p>
                Wszystkie najważniejsze opcje
                znajdziesz w menu po lewej.
            </p>

        </div>

    </div>


    <section class="quick">

        <h2>
            Szybkie akcje
        </h2>

        <a href="/profile">
            👤 Otwórz profil
        </a>

        <a href="/change-password">
            🔐 Zmień hasło
        </a>

        <a href="/logout">
            🚪 Wyloguj
        </a>

    </section>

</main>

</body>
</html>
""", username=username)


# =========================
# PROFIL
# =========================

@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FilipHub — Profil</title>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #020617;
    color: white;
}

.container {
    max-width: 700px;
    margin: 70px auto;
    padding: 25px;
}

.box {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 35px;
    text-align: center;
}

.avatar {
    width: 90px;
    height: 90px;
    margin: auto;
    border-radius: 50%;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
}

.username {
    font-size: 28px;
    margin: 20px 0 5px;
}

.info {
    color: #94a3b8;
}

a {
    display: inline-block;
    margin-top: 25px;
    color: white;
    background: #1e293b;
    padding: 12px 20px;
    border-radius: 10px;
    text-decoration: none;
}

</style>

</head>

<body>

<div class="container">

<div class="box">

<div class="avatar">
    👤
</div>

<div class="username">
    {{ username }}
</div>

<div class="info">
    Użytkownik FilipHub
</div>

<a href="/panel">
    ← Wróć do dashboardu
</a>

</div>

</div>

</body>
</html>
""", username=username)


# =========================
# ZMIANA HASŁA
# =========================

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "username" not in session:
        return redirect("/")

    message = ""

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        username = session["username"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = c.fetchone()

        if not user:

            conn.close()
            return redirect("/")

        if not check_password_hash(user[2], current_password):

            message = "Obecne hasło jest nieprawidłowe."

        elif len(new_password) < 6:

            message = "Nowe hasło musi mieć minimum 6 znaków."

        elif new_password != confirm_password:

            message = "Nowe hasła nie są takie same."

        elif check_password_hash(user[2], new_password):

            message = "Nowe hasło musi być inne od obecnego."

        else:

            hashed_password = generate_password_hash(new_password)

            c.execute(
                """
                UPDATE users
                SET password = ?
                WHERE username = ?
                """,
                (hashed_password, username)
            )

            conn.commit()
            conn.close()

            return render_template_string("""
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">

<title>Hasło zmienione</title>

<style>

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background: #020617;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.box {
    background: #0f172a;
    border: 1px solid #1e293b;
    padding: 40px;
    border-radius: 20px;
    text-align: center;
}

.success {
    font-size: 50px;
}

a {
    display: inline-block;
    margin-top: 20px;
    background: #1e293b;
    padding: 12px 20px;
    border-radius: 10px;
    color: white;
    text-decoration: none;
}

</style>

</head>

<body>

<div class="box">

<div class="success">
    ✅
</div>

<h1>Hasło zmienione</h1>

<p style="color:#94a3b8;">
    Twoje hasło zostało pomyślnie zmienione.
</p>

<a href="/panel">
    Wróć do dashboardu
</a>

</div>

</body>

</html>
""")

        conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FilipHub — Zmień hasło</title>

<style>

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background: #020617;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.box {
    width: 400px;
    max-width: 92%;
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 35px;
}

h1 {
    margin-top: 0;
}

input {
    width: 100%;
    padding: 14px;
    margin-bottom: 14px;
    border-radius: 12px;
    border: 1px solid #334155;
    background: #020617;
    color: white;
    box-sizing: border-box;
}

button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: white;
    font-weight: bold;
    cursor: pointer;
}

.message {
    color: #f87171;
    text-align: center;
    margin-top: 15px;
}

.back {
    text-align: center;
    margin-top: 20px;
}

a {
    color: #818cf8;
}

</style>

</head>

<body>

<div class="box">

<h1>🔐 Zmień hasło</h1>

<p style="color:#94a3b8;">
    Zabezpiecz swoje konto nowym hasłem.
</p>

<form method="POST">

<input
    type="password"
    name="current_password"
    placeholder="Obecne hasło"
    required
>

<input
    type="password"
    name="new_password"
    placeholder="Nowe hasło"
    required
>

<input
    type="password"
    name="confirm_password"
    placeholder="Powtórz nowe hasło"
    required
>

<button type="submit">
    Zmień hasło
</button>

</form>

{% if message %}
<div class="message">
    {{ message }}
</div>
{% endif %}

<div class="back">
    <a href="/panel">
        ← Wróć do dashboardu
    </a>
</div>

</div>

</body>

</html>
""", message=message)


# =========================
# WYLOGOWANIE
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# START
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )
