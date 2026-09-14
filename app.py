from flask import Flask, request, redirect, session, render_template_string, url_for
import sqlite3
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "filiphub-dev-secret"
)


DB = "users.db"

UPLOAD_FOLDER = "static/uploads"

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# =========================================================
# DATABASE
# =========================================================

def get_db():
    return sqlite3.connect(DB)


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def init_db():

    conn = get_db()

    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            avatar TEXT DEFAULT ''

        )
    """)

    try:

        c.execute(
            "ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT ''"
        )

    except sqlite3.OperationalError:

        pass

    conn.commit()

    conn.close()


init_db()


# =========================================================
# CSS
# =========================================================

CSS = """
<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Arial,sans-serif;
    background:#020617;
    color:#fff;
}

a{
    text-decoration:none;
    color:inherit;
}


/* SIDEBAR */

.sidebar{
    position:fixed;
    left:0;
    top:0;
    width:240px;
    height:100vh;
    background:#0f172a;
    border-right:1px solid #1e293b;
    padding:25px 15px;
    z-index:10;
}

.logo{
    font-size:25px;
    font-weight:700;
    padding:10px;
    margin-bottom:35px;
}

.menu-title{
    color:#64748b;
    font-size:12px;
    text-transform:uppercase;
    padding:0 12px;
    margin-bottom:10px;
}

.menu a{
    display:block;
    padding:13px 15px;
    margin-bottom:7px;
    border-radius:10px;
    color:#cbd5e1;
}

.menu a:hover{
    background:#1e293b;
    color:#fff;
}

.logout{
    position:absolute;
    bottom:25px;
    left:15px;
    right:15px;
}

.logout a{
    display:block;
    padding:13px;
    border-radius:10px;
    color:#f87171;
}

.logout a:hover{
    background:#1e293b;
}


/* MAIN */

.main{
    margin-left:240px;
    padding:35px;
    min-height:100vh;
}

.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:30px;
}

.topbar h1{
    margin:0;
}

.user{
    display:flex;
    align-items:center;
    gap:10px;
    background:#0f172a;
    border:1px solid #1e293b;
    padding:8px 14px;
    border-radius:12px;
}

.avatar-small{
    width:40px;
    height:40px;
    border-radius:50%;
    object-fit:cover;
    background:#1e293b;
}


/* HERO */

.hero{
    padding:35px;
    border-radius:20px;
    background:linear-gradient(
        135deg,
        #1e1b4b,
        #312e81
    );
    border:1px solid #4338ca;
    margin-bottom:25px;
}

.hero h2{
    font-size:30px;
    margin:0 0 10px;
}

.hero p,
.muted{
    color:#94a3b8;
}


/* GRID */

.grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:20px;
}

.card,
.quick,
.form-box,
.profile-card{
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:18px;
}

.card{
    padding:25px;
    transition:.2s;
}

.card:hover{
    border-color:#475569;
    transform:translateY(-3px);
}

.card-icon{
    font-size:28px;
    margin-bottom:15px;
}

.card h3{
    margin:0 0 8px;
}

.card p{
    color:#94a3b8;
    line-height:1.5;
}


/* QUICK */

.quick{
    margin-top:25px;
    padding:25px;
}

.quick a,
.btn{
    display:inline-block;
    padding:12px 18px;
    margin:5px;
    background:#1e293b;
    border-radius:10px;
}

.quick a:hover,
.btn:hover{
    background:#334155;
}


/* FORMS */

.form-box{
    max-width:500px;
    padding:30px;
}

input[type=text],
input[type=password],
input[type=file]{
    width:100%;
    padding:14px;
    margin:8px 0 18px;
    border-radius:12px;
    border:1px solid #334155;
    background:#020617;
    color:#fff;
}

input[type=file]{
    padding:12px;
}

button{
    width:100%;
    padding:14px;
    border:0;
    border-radius:12px;
    background:linear-gradient(
        135deg,
        #6366f1,
        #8b5cf6
    );
    color:#fff;
    font-weight:700;
    cursor:pointer;
}

button:hover{
    opacity:.9;
}

.message{
    color:#f87171;
    margin-bottom:15px;
}


/* PROFILE */

.profile-card{
    max-width:500px;
    padding:35px;
    text-align:center;
}

.avatar-big{
    width:140px;
    height:140px;
    border-radius:50%;
    object-fit:cover;
    background:#1e293b;
    border:4px solid #312e81;
    margin-bottom:20px;
}

.placeholder{
    width:140px;
    height:140px;
    border-radius:50%;
    background:linear-gradient(
        135deg,
        #6366f1,
        #8b5cf6
    );
    display:inline-flex;
    align-items:center;
    justify-content:center;
    font-size:60px;
    margin-bottom:20px;
}

.profile-name{
    font-size:30px;
    font-weight:700;
    margin-bottom:8px;
}


/* =========================================================
   GAMES
   ========================================================= */

.games-title{
    margin-bottom:25px;
}

.game-card{
    max-width:650px;
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:20px;
    padding:25px;
}

.game-card h2{
    margin-top:0;
}

.snake-wrapper{
    display:flex;
    justify-content:center;
    margin-top:20px;
}

#snake{
    width:100%;
    max-width:500px;
    aspect-ratio:1/1;
    background:#020617;
    border:2px solid #334155;
    border-radius:12px;
    display:block;
}

.game-info{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-top:15px;
    gap:15px;
}

.score{
    font-size:20px;
    font-weight:bold;
}

.start-btn{
    width:auto;
    padding:12px 20px;
}

.controls{
    display:grid;
    grid-template-columns:repeat(3,60px);
    justify-content:center;
    gap:8px;
    margin-top:20px;
}

.controls button{
    width:60px;
    height:50px;
    padding:0;
    font-size:20px;
}

.controls .empty{
    visibility:hidden;
}


/* MOBILE */

@media(max-width:850px){

    .sidebar{
        position:relative;
        width:100%;
        height:auto;
        border-right:0;
        border-bottom:1px solid #1e293b;
    }

    .logout{
        position:relative;
        left:auto;
        right:auto;
        bottom:auto;
        margin-top:20px;
    }

    .main{
        margin-left:0;
        padding:20px;
    }

    .grid{
        grid-template-columns:1fr;
    }

    .topbar{
        display:block;
    }

    .user{
        display:inline-flex;
        margin-top:15px;
    }

    .game-card{
        padding:15px;
    }

}

</style>
"""


# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    return """
    <aside class="sidebar">

        <div class="logo">
            🔥 FilipHub
        </div>

        <div class="menu-title">
            Menu
        </div>

        <div class="menu">

            <a href="/panel">
                🏠 Dashboard
            </a>

            <a href="/games">
                🎮 Gry
            </a>

            <a href="/profile">
                👤 Profil
            </a>

            <a href="/edit-profile">
                ✏️ Edytuj profil
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
    """


# =========================================================
# USER DATA
# =========================================================

def user_data(username):

    conn = get_db()

    c = conn.cursor()

    c.execute(
        """
        SELECT username, avatar
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    row = c.fetchone()

    conn.close()

    return row


# =========================================================
# LOGIN
# =========================================================

LOGIN_HTML = """
<!doctype html>

<html lang="pl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>FilipHub</title>

{{ css|safe }}

</head>

<body
style="
min-height:100vh;
display:flex;
align-items:center;
justify-content:center
"
>

<div
class="form-box"
style="width:400px;max-width:92%"
>

<h1 style="text-align:center">
🔥 FilipHub
</h1>

<p
class="muted"
style="text-align:center"
>
Witaj ponownie
</p>

{% if message %}

<div class="message">
{{ message }}
</div>

{% endif %}

<form method="post">

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

<p
class="muted"
style="
text-align:center;
margin-top:20px
"
>

Nie masz konta?

<a
href="/register"
style="color:#818cf8"
>
Utwórz konto
</a>

</p>

</div>

</body>

</html>
"""


# =========================================================
# REGISTER
# =========================================================

REGISTER_HTML = """
<!doctype html>

<html lang="pl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>FilipHub</title>

{{ css|safe }}

</head>

<body
style="
min-height:100vh;
display:flex;
align-items:center;
justify-content:center
"
>

<div
class="form-box"
style="width:400px;max-width:92%"
>

<h1 style="text-align:center">
🔥 FilipHub
</h1>

<p
class="muted"
style="text-align:center"
>
Utwórz konto
</p>

{% if message %}

<div class="message">
{{ message }}
</div>

{% endif %}

<form method="post">

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

<p
class="muted"
style="
text-align:center;
margin-top:20px
"
>

Masz już konto?

<a
href="/"
style="color:#818cf8"
>
Zaloguj się
</a>

</p>

</div>

</body>

</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]


        conn = get_db()

        c = conn.cursor()

        c.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = c.fetchone()

        conn.close()


        if user and check_password_hash(
            user[2],
            password
        ):

            session["username"] = username

            return redirect("/panel")


        message = "Nieprawidłowy login lub hasło."


    return render_template_string(
        LOGIN_HTML,
        css=CSS,
        message=message
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]


        if len(username) < 3:

            message = (
                "Nazwa użytkownika musi mieć minimum 3 znaki."
            )

        elif len(password) < 6:

            message = (
                "Hasło musi mieć minimum 6 znaków."
            )

        else:

            conn = get_db()

            c = conn.cursor()

            try:

                c.execute(
                    """
                    INSERT INTO users
                    (
                        username,
                        password,
                        avatar
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        username,
                        generate_password_hash(password),
                        ""
                    )
                )

                conn.commit()

                conn.close()

                return redirect("/")


            except sqlite3.IntegrityError:

                conn.close()

                message = (
                    "Taki użytkownik już istnieje."
                )


    return render_template_string(
        REGISTER_HTML,
        css=CSS,
        message=message
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/panel")
def panel():

    if "username" not in session:

        return redirect("/")


    username = session["username"]

    row = user_data(username)

    avatar = (
        row[1]
        if row and row[1]
        else ""
    )


    return render_template_string(
        """
<!doctype html>

<html lang="pl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>FilipHub - Dashboard</title>

{{ css|safe }}

</head>

<body>

{{ sidebar|safe }}

<main class="main">


<div class="topbar">

<div>

<h1>
Dashboard
</h1>

<p class="muted">
Centrum Twojego konta
</p>

</div>


<div class="user">

{% if avatar %}

<img
class="avatar-small"
src="{{ url_for(
    'static',
    filename='uploads/' + avatar
) }}"
>

{% else %}

<div
class="avatar-small"
style="
display:flex;
align-items:center;
justify-content:center;
font-size:22px
"
>
👤
</div>

{% endif %}

{{ username }}

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
👤
</div>

<h3>
Twój profil
</h3>

<p>
Ustaw własne zdjęcie profilowe
i zmieniaj dane konta.
</p>

</div>


<div class="card">

<div class="card-icon">
🎮
</div>

<h3>
Gry
</h3>

<p>
Zagraj w minigry i pobij swój rekord.
</p>

<a
class="btn"
href="/games"
>
Zagraj
</a>

</div>


</div>


<section class="quick">

<h2>
Szybkie akcje
</h2>

<a href="/profile">
👤 Profil
</a>

<a href="/games">
🎮 Gry
</a>

<a href="/edit-profile">
✏️ Edytuj profil
</a>

<a href="/change-password">
🔐 Zmień hasło
</a>

</section>


</main>

</body>

</html>
        """,
        css=CSS,
        sidebar=sidebar(),
        username=username,
        avatar=avatar
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "username" not in session:

        return redirect("/")


    username = session["username"]

    row = user_data(username)

    avatar = (
        row[1]
        if row and row[1]
        else ""
    )


    return render_template_string(
        """
<!doctype html>

<html lang="pl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>FilipHub - Profil</title>

{{ css|safe }}

</head>

<body>

{{ sidebar|safe }}

<main class="main">

<div class="topbar">

<h1>
Twój profil
</h1>

</div>


<div class="profile-card">


{% if avatar %}

<img
class="avatar-big"
src="{{ url_for(
    'static',
    filename='uploads/' + avatar
) }}"
>

{% else %}

<div class="placeholder">
👤
</div>

{% endif %}


<div class="profile-name">
{{ username }}
</div>

<div class="muted">
Użytkownik FilipHub
</div>


<div style="margin-top:25px">

<a
class="btn"
href="/edit-profile"
>
✏️ Edytuj profil
</a>

<a
class="btn"
href="/games"
>
🎮 Gry
</a>

</div>

</div>

</main>

</body>

</html>
        """,
        css=CSS,
        sidebar=sidebar(),
        username=username,
        avatar=avatar
    )


# =========================================================
# EDIT PROFILE
# =========================================================

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "username" not in session:

        return redirect("/")


    old_username = session["username"]

    row = user_data(old_username)

    current_avatar = (
        row[1]
        if row and row[1]
        else ""
    )

    message = ""


    if request.method == "POST":

        new_username = request.form["username"].strip()

        file = request.files.get("avatar")

        new_avatar = current_avatar


        if len(new_username) < 3:

            message = (
                "Nazwa użytkownika musi mieć minimum 3 znaki."
            )

        elif (
            file
            and file.filename
            and not allowed_file(file.filename)
        ):

            message = (
                "Dozwolone formaty: JPG, JPEG, PNG, WEBP."
            )

        else:

            if file and file.filename:

                extension = secure_filename(
                    file.filename
                ).rsplit(
                    ".",
                    1
                )[1].lower()


                filename = (
                    uuid.uuid4().hex
                    + "."
                    + extension
                )


                filepath = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )


                file.save(filepath)

                new_avatar = filename


            conn = get_db()

            c = conn.cursor()


            try:

                c.execute(
                    """
                    UPDATE users

                    SET username = ?,
                        avatar = ?

                    WHERE username = ?
                    """,
                    (
                        new_username,
                        new_avatar,
                        old_username
                    )
                )

                conn.commit()

                conn.close()


                if (
                    current_avatar
                    and
                    new_avatar != current_avatar
                ):

                    old_file = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        current_avatar
                    )


                    if os.path.exists(old_file):

                        try:

                            os.remove(old_file)

                        except OSError:

                            pass


                session["username"] = new_username

                return redirect("/profile")


            except sqlite3.IntegrityError:

                conn.close()


                if new_avatar != current_avatar:

                    new_file = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        new_avatar
                    )


                    if os.path.exists(new_file):

                        os.remove(new_file)


                message = (
                    "Taka nazwa użytkownika już istnieje."
                )


    return render_template_string(
        """
<!doctype html>

<html lang="pl">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>FilipHub - Edytuj profil</title>

{{ css|safe }}

</head>

<body>

{{ sidebar|safe }}

<m
