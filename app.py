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


@app.route("/", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
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

        message = "❌ Nieprawidłowy login lub hasło."

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>FilipHub - Logowanie</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding-top: 80px;
        }

        .box {
            background: #222;
            padding: 30px;
            margin: auto;
            width: 300px;
            border-radius: 15px;
        }

        input {
            width: 90%;
            padding: 12px;
            margin: 8px;
            border-radius: 8px;
            border: none;
            box-sizing: border-box;
        }

        button {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🔥 FilipHub</h1>
    <h2>Logowanie</h2>

    <form method="POST">

        <input
            type="text"
            name="username"
            placeholder="Login"
            required
        >

        <input
            type="password"
            name="password"
            placeholder="Hasło"
            required
        >

        <button type="submit">
            Zaloguj
        </button>

    </form>

    <p>{{ message }}</p>

    <p>
        Nie masz konta?
        <a href="/register">Zarejestruj się</a>
    </p>

</div>

</body>
</html>
""", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if len(username) < 3:
            message = "❌ Login musi mieć minimum 3 znaki."

        elif len(password) < 6:
            message = "❌ Hasło musi mieć minimum 6 znaków."

        else:
            conn = sqlite3.connect(DB)
            c = conn.cursor()

            try:
                hashed_password = generate_password_hash(password)

                c.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )

                conn.commit()
                conn.close()

                return redirect("/")

            except sqlite3.IntegrityError:
                conn.close()
                message = "❌ Taki użytkownik już istnieje."

    return render_template_string("""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>FilipHub - Rejestracja</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding-top: 80px;
        }

        .box {
            background: #222;
            padding: 30px;
            margin: auto;
            width: 300px;
            border-radius: 15px;
        }

        input {
            width: 90%;
            padding: 12px;
            margin: 8px;
            border-radius: 8px;
            border: none;
            box-sizing: border-box;
        }

        button {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🔥 FilipHub</h1>
    <h2>Rejestracja</h2>

    <form method="POST">

        <input
            type="text"
            name="username"
            placeholder="Login"
            required
        >

        <input
            type="password"
            name="password"
            placeholder="Hasło"
            required
        >

        <button type="submit">
            Zarejestruj
        </button>

    </form>

    <p>{{ message }}</p>

    <p>
        Masz już konto?
        <a href="/">Zaloguj się</a>
    </p>

</div>

</body>
</html>
""", message=message)


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
    <title>FilipHub - Panel</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
        }

        nav {
            background: #222;
            padding: 18px;
            text-align: center;
        }

        nav a {
            color: white;
            text-decoration: none;
            margin: 0 12px;
        }

        .container {
            max-width: 700px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }

        .welcome {
            background: #222;
            padding: 30px;
            border-radius: 15px;
        }

        .future {
            margin-top: 25px;
            padding: 25px;
            background: #1c1c1c;
            border-radius: 15px;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<nav>
    <a href="/panel">🏠 Start</a>
    <a href="/profile">👤 Profil</a>
    <a href="/change-password">🔐 Zmień hasło</a>
    <a href="/logout">🚪 Wyloguj</a>
</nav>

<div class="container">

    <div class="welcome">

        <h1>🔥 Witaj, {{ username }}!</h1>

        <p>
            Jesteś zalogowany.
        </p>

    </div>

    <div class="future">

        <h2>🚀 Coś nowego już wkrótce!</h2>

        <p>
            W przyszłości pojawią się tutaj nowe funkcje,
            ulepszenia profilu i więcej możliwości.
        </p>

    </div>

</div>

</body>
</html>
""", username=username)


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
    <title>Profil - FilipHub</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding-top: 50px;
        }

        .box {
            background: #222;
            padding: 30px;
            margin: auto;
            max-width: 400px;
            border-radius: 15px;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>👤 Profil</h1>

    <p>
        Zalogowany jako:
    </p>

    <h2>{{ username }}</h2>

    <br>

    <a href="/panel">🏠 Wróć do panelu</a>

</div>

</body>
</html>
""", username=username)


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
            message = "❌ Obecne hasło jest nieprawidłowe."

        elif len(new_password) < 6:
            message = "❌ Nowe hasło musi mieć minimum 6 znaków."

        elif new_password != confirm_password:
            message = "❌ Nowe hasła nie są takie same."

        elif check_password_hash(user[2], new_password):
            message = "❌ Nowe hasło musi być inne od obecnego."

        else:
            hashed_password = generate_password_hash(new_password)

            c.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_password, username)
            )

            conn.commit()
            conn.close()

            message = "✅ Hasło zostało zmienione!"

            return render_template_string("""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Hasło zmienione</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding-top: 80px;
        }

        .box {
            background: #222;
            padding: 30px;
            margin: auto;
            max-width: 400px;
            border-radius: 15px;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🔐 Hasło zmienione!</h1>

    <p>Twoje hasło zostało pomyślnie zmienione.</p>

    <br>

    <a href="/panel">🏠 Wróć do panelu</a>

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
    <title>FilipHub - Zmiana hasła</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding-top: 60px;
        }

        .box {
            background: #222;
            padding: 30px;
            margin: auto;
            width: 320px;
            border-radius: 15px;
        }

        input {
            width: 90%;
            padding: 12px;
            margin: 8px;
            border-radius: 8px;
            border: none;
            box-sizing: border-box;
        }

        button {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }

        a {
            color: #4da6ff;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🔐 Zmień hasło</h1>

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

    <p>{{ message }}</p>

    <br>

    <a href="/panel">🏠 Wróć do panelu</a>

</div>

</body>
</html>
""", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
