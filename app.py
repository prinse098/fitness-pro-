from flask import Flask, request, redirect, session, render_template
import sqlite3
import matplotlib.pyplot as plt

import os
import openai
from werkzeug.security import generate_password_hash, check_password_hash

from openai import OpenAI

app = Flask(__name__)
app.secret_key = "mysecret123"

client = openai.api_key = os.getenv("OPENAI_API_KEY")
def render_page(content):
    return f"""
    <html>
    <head>
    <style>
    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        padding:40px;
    }}
    a {{
        color:#00ffcc;
        text-decoration:none;
    }}
    </style>
    </head>
    <body>
    {content}
    </body>
    </html>
    """
def init_db():
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        name TEXT,
        weight INTEGER,
        calories INTEGER,
        running INTEGER,
        goal TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS daily (
        username TEXT,
        calories INTEGER,
        protein INTEGER,
        running REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        username TEXT UNIQUE,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS plans (
        username TEXT,
        age INTEGER,
        height REAL,
        weight INTEGER,
        goal TEXT,
        work TEXT,
        fat INTEGER,
        fat_goal TEXT,
        budget INTEGER
    )""")

    conn.commit()
    conn.close()
# Home page
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b') no-repeat center center/cover;
        color:white;
    }}

    .overlay {{
        background: rgba(0,0,0,0.75);
        min-height:100vh;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
    }}

    h1 {{
        font-size:50px;
        margin-bottom:5px;
        letter-spacing:2px;
    }}

    h3 {{
        margin-bottom:25px;
        color:#ddd;
    }}

    .buttons {{
        display:flex;
        flex-direction:column;
        gap:12px;
    }}

    button {{
        width:260px;
        padding:12px;
        border:none;
        border-radius:12px;
        font-size:16px;
        cursor:pointer;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        transition:0.3s;
        box-shadow:0 4px 15px rgba(0,0,0,0.4);
    }}

    button:hover {{
        transform: scale(1.08);
        box-shadow:0 6px 20px rgba(0,0,0,0.6);
    }}

    .logout {{
        background:red;
    }}

    </style>
    </head>

    <body>

    <div class="overlay">

        <h1>🏋️ Fitness Tracker</h1>
        <h3>Welcome, {username} 👋</h3>

        <div class="buttons">

            <a href="/plan"><button>🔥 Fill Form</button></a>
            <a href="/dashboard"><button>📊 Dashboard</button></a>
            <a href="/chart"><button>📈 Chart</button></a>
            <a href="/daily_input"><button>📅 Daily Entry</button></a>
            <a href="/weekplan"><button>📅 7 Day Plan</button></a>
            <a href="/coach"><button>🤖 AI Coach</button></a>
            <a href="/daily"><button>📅 Daily Plan</button></a>
            <a href="/myplan"><button>📋 My Plan</button></a>
            <a href="/budget_plan"><button>🛒 Budget Plan</button></a>
            <a href="/progress_ai"><button>🤖 AI Progress</button></a>
            <a href="/auto_adjust"><button>🤖 Auto Adjust AI</button></a>
            <a href="/coach_chat"><button>💬 AI Chat Coach</button></a>
            <a href="/weekly_graph"><button>📈 Weekly Graph</button></a>
            <a href="/goal_predict"><button>🎯 Goal Prediction</button></a>
            <a href="/simulate"><button>🧠 Simulator</button></a>

            <a href="/history"><button>📊 History</button></a>
            <a href="/logout"><button class="logout">🚪 Logout</button></a>

        </div>

    </div>

    </body>
    </html>
    """

# Submit data
@app.route("/submit", methods=["POST"])
def submit():
    if "user" not in session:
        return render_page("<h2>🔐 Please login first</h2>")

    username = session["user"]

    name = request.form["name"]
    weight = request.form["weight"]
    calories = int(request.form["calories"])
    running = int(request.form["running"])
    goal = request.form["goal"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
              (username, name, weight, calories, running, goal))

    conn.commit()
    conn.close()

    # 🔥 direct home pe bhej de
    return redirect("/")
# History page
@app.route("/history")
def history():
    if "user" not in session:
        return render_page("<h2>🔐 Please login first</h2>")

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    data = c.fetchall()

    conn.close()

    if not data:
        return render_page("""
            <h1>📊 Your History</h1>
            <p>No data found 😅</p>
            <a href="/"><button>🏠 Home</button></a>
        """)

    result = "<h1>📊 Your History</h1>"

    for row in data:
        result += f"""
        <div style="
            background: rgba(255,255,255,0.1);
            margin:15px auto;
            padding:15px;
            border-radius:12px;
            width:300px;
            box-shadow:0 4px 15px rgba(0,0,0,0.4);
        ">
            <p><b>Name:</b> {row[1]}</p>
            <p><b>Weight:</b> {row[2]} kg</p>
            <p><b>Calories:</b> {row[3]}</p>
            <p><b>Running:</b> {row[4]} km</p>
            <p><b>Goal:</b> {row[5]}</p>
        </div>
        """

    result += '<br><a href="/"><button>🏠 Home</button></a>'

    return render_page(result)
@app.route("/chart")
def chart():
    if "user" not in session:
        return render_page("<h2>🔐 Please login first</h2>")

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT weight, fat FROM plans WHERE username=?", (username,))
    data = c.fetchall()
    conn.close()

    if not data:
        return render_page("""
            <h1>📊 Progress Chart</h1>
            <p>No data available 😅</p>
            <a href="/"><button>🏠 Home</button></a>
        """)

    weight = [row[0] for row in data]
    fat = [row[1] for row in data]

    # 🔥 graph styling
    plt.figure(figsize=(8,5))
    plt.plot(weight, marker='o', linewidth=2, label="Weight")
    plt.plot(fat, marker='o', linewidth=2, label="Fat %")

    plt.legend()
    plt.title("Progress Chart 📊")
    plt.grid(True)

    plt.savefig("static/chart.png", bbox_inches='tight')
    plt.close()

    return render_page("""
        <h1>📊 Progress Chart</h1>

        <div style="
            background: rgba(255,255,255,0.1);
            padding:20px;
            border-radius:15px;
            box-shadow:0 5px 20px rgba(0,0,0,0.5);
            display:inline-block;
        ">
            <img src="/static/chart.png" style="width:100%;max-width:500px;border-radius:10px;">
        </div>

        <br><br>
        <a href="/"><button>🏠 Home</button></a>
    """)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return render_page("<h2>🔐 Please login first</h2>")

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
        SELECT weight, goal, work
        FROM plans
        WHERE username=?
        ORDER BY rowid DESC LIMIT 1
    """, (username,))
    plan = c.fetchone()

    c.execute("""
        SELECT calories, protein, running
        FROM daily
        WHERE username=?
        ORDER BY rowid DESC LIMIT 1
    """, (username,))
    daily = c.fetchone()

    conn.close()

    if not plan:
        return render_page("""
            <h2>😅 Create plan first</h2>
            <a href="/plan"><button>Go</button></a>
        """)

    if not daily:
        return render_page("""
            <h2>😅 Add today's data first</h2>
            <a href="/daily_input"><button>Go</button></a>
        """)

    weight, goal, work = plan
    calories_taken, protein_taken, running_done = daily

    base = weight * (40 if work == "physical" else 30)

    if goal == "loss":
        target_cal = base - 400
        target_run = 5
    else:
        target_cal = base + 400
        target_run = 2

    target_protein = weight * 1.6

    cal_diff = target_cal - calories_taken
    protein_diff = target_protein - protein_taken
    run_diff = target_run - running_done

    if goal == "loss":
        advice = f"""
        🔥 Fat Loss Mode<br>
        Calories remaining: {cal_diff}<br>
        Protein needed: {round(protein_diff,1)}g<br>
        Run more: {round(run_diff,1)} km
        """
    else:
        advice = f"""
        💪 Muscle Gain Mode<br>
        Extra calories needed: {cal_diff}<br>
        Protein needed: {round(protein_diff,1)}g<br>
        Light running: {round(run_diff,1)} km
        """

    return render_page(f"""
        <h1>🤖 Smart Dashboard</h1>

        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:20px;">

            <div style="background:rgba(255,255,255,0.1);padding:20px;border-radius:15px;width:250px;">
                <h3>📊 Today's Stats</h3>
                <p>🔥 Calories: {calories_taken}</p>
                <p>💪 Protein: {protein_taken} g</p>
                <p>🏃 Running: {running_done} km</p>
            </div>

            <div style="background:rgba(255,255,255,0.1);padding:20px;border-radius:15px;width:250px;">
                <h3>🎯 Target</h3>
                <p>Calories: {target_cal}</p>
                <p>Protein: {round(target_protein,1)} g</p>
                <p>Running: {target_run} km</p>
            </div>

        </div>

        <br>

        <div style="
            background:rgba(255,255,255,0.1);
            padding:20px;
            border-radius:15px;
            width:300px;
            margin:auto;
        ">
            <h3>⚡ AI Suggestion</h3>
            <p>{advice}</p>
        </div>

        <br><br>

        <a href="/daily_input"><button>➕ Update Today</button></a>
        <br><br>
        <a href="/"><button>🏠 Home</button></a>
    """)
@app.route("/login")
def login():

    if "user" in session:
        return redirect("/")

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.85)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }

    .overlay {
        background: rgba(0,0,0,0.65);
        padding:45px;
        border-radius:18px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        animation: fade 0.8s ease;
    }

    @keyframes fade {
        from {opacity:0; transform:translateY(20px);}
        to {opacity:1; transform:translateY(0);}
    }

    h2 {
        margin-bottom:25px;
        font-size:32px;
        letter-spacing:1px;
    }

    input {
        width:260px;
        padding:12px;
        margin:10px 0;
        border:none;
        border-radius:10px;
        outline:none;
        font-size:14px;
    }

    button {
        width:280px;
        padding:12px;
        margin-top:12px;
        border:none;
        border-radius:12px;
        font-size:16px;
        cursor:pointer;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        transition:0.3s;
        box-shadow:0 5px 20px rgba(0,0,0,0.5);
    }

    button:hover {
        transform: scale(1.05);
    }

    a {
        display:block;
        margin-top:18px;
        color:#ccc;
        text-decoration:none;
        font-size:14px;
    }

    a:hover {
        color:white;
    }

    </style>
    </head>

    <body>

    <div class="overlay">
        <h2>🔐 Login</h2>

        <form action="/login_check" method="post">
            <input type="text" name="username" placeholder="Enter Username" required><br>
            <input type="password" name="password" placeholder="Enter Password" required><br>
            <button>Login</button>
        </form>

        <a href="/signup">Create Account</a>
    </div>

    </body>
    </html>
    """
@app.route("/signup")
def signup():
    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.85)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }

    .overlay {
        background: rgba(0,0,0,0.65);
        padding:45px;
        border-radius:18px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        animation: fade 0.8s ease;
    }

    @keyframes fade {
        from {opacity:0; transform:translateY(20px);}
        to {opacity:1; transform:translateY(0);}
    }

    h2 {
        margin-bottom:25px;
        font-size:32px;
    }

    input {
        width:260px;
        padding:12px;
        margin:10px 0;
        border:none;
        border-radius:10px;
        outline:none;
        font-size:14px;
    }

    button {
        width:280px;
        padding:12px;
        margin-top:12px;
        border:none;
        border-radius:12px;
        font-size:16px;
        cursor:pointer;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        transition:0.3s;
        box-shadow:0 5px 20px rgba(0,0,0,0.5);
    }

    button:hover {
        transform: scale(1.05);
    }

    a {
        display:block;
        margin-top:18px;
        color:#ccc;
        text-decoration:none;
    }

    a:hover {
        color:white;
    }

    </style>
    </head>

    <body>

    <div class="overlay">
        <h2>📝 Sign Up</h2>

        <form action="/signup_check" method="post">
            <input type="text" name="username" placeholder="Enter Username" required><br>
            <input type="password" name="password" placeholder="Enter Password" required><br>
            <button>Create Account</button>
        </form>

        <a href="/login">Already have account? Login</a>
    </div>

    </body>
    </html>
    """
@app.route("/signup_check", methods=["POST"])
def signup_check():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO accounts VALUES (?, ?)", (username, password))
        conn.commit()
    except:
        conn.close()
        return "<h2>⚠️ Username already exists</h2><a href='/signup'>Try Again</a>"

    conn.close()

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }

    .overlay {
        background: rgba(0,0,0,0.65);
        padding:50px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        animation: fadeIn 0.8s ease;
    }

    .tick {
        font-size:60px;
        margin-bottom:10px;
        animation: pop 0.5s ease;
    }

    h2 {
        font-size:30px;
        margin-bottom:10px;
        color:#00ffcc;
    }

    p {
        color:#ccc;
        font-size:16px;
    }

    @keyframes fadeIn {
        from {opacity:0; transform:translateY(20px);}
        to {opacity:1; transform:translateY(0);}
    }

    @keyframes pop {
        0% {transform: scale(0);}
        100% {transform: scale(1);}
    }

    </style>

    <script>
        setTimeout(function(){
            window.location.href = "/login";
        }, 2000);
    </script>

    </head>

    <body>

    <div class="overlay">
        <div class="tick">✅</div>
        <h2>Account Created Successfully</h2>
        <p>Redirecting to login...</p>
    </div>

    </body>
    </html>
    """
@app.route("/login_check", methods=["POST"])
def login_check():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    conn.close()

    if user:
        session["user"] = username   # ✅ login success
        return redirect("/")         # home page
    else:
        return """
        <html>
        <head>
        <style>

        body {
            margin:0;
            font-family:sans-serif;
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
            url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
            color:white;
        }

        .box {
            background: rgba(0,0,0,0.7);
            padding:40px;
            border-radius:15px;
            text-align:center;
        }

        a {
            color:#00ffcc;
            text-decoration:none;
        }

        </style>
        </head>

        <body>
            <div class="box">
                <h2>❌ Invalid Username or Password</h2>
                <a href="/login">Try Again</a>
            </div>
        </body>
        </html>
        """
@app.route("/result", methods=["POST"])
def result():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    age = request.form.get("age")
    height = request.form.get("height")
    weight = request.form.get("weight")
    goal = request.form.get("goal")
    work = request.form.get("work")
    fat = request.form.get("fat")
    fat_goal = request.form.get("fat_goal")
    budget = request.form.get("budget")

    if not age or not height or not weight or not fat or not budget:
        return "<h2>⚠️ Fill all fields properly</h2><a href='/plan'>Go Back</a>"

    try:
        age = int(age)
        height = float(height)
        weight = int(weight)
        fat = int(fat)
        budget = int(budget)
    except:
        return "<h2>⚠️ Invalid input</h2><a href='/plan'>Go Back</a>"

    # BMI
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    # Calories
    calories = weight * (30 if work == "office" else 40)
    calories = calories - 300 if goal == "loss" else calories + 300

    # Protein
    protein = weight * 1.5

    # Messages
    bmi_msg = "Underweight ⚠️" if bmi < 18.5 else "Normal ✅" if bmi < 25 else "Overweight ⚠️"
    goal_msg = "Fat loss + cardio 🏃" if goal == "loss" else "Muscle gain + gym 💪"
    fat_msg = "Reduce oily + cardio 🔥" if fat_goal == "loss" else "Healthy fats + training 💪"

    if budget < 100:
        diet = "Roti 🍞, dal 🥣, rice 🍚, peanuts 🥜, milk 🥛"
    elif budget < 200:
        diet = "Eggs 🥚, banana 🍌, milk 🥛, rice 🍚"
    else:
        diet = "Chicken 🍗, paneer 🧀, eggs 🥚, fruits 🍎"

    # SAVE
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()
    c.execute("INSERT INTO plans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (username, age, height, weight, goal, work, fat, fat_goal, budget))
    conn.commit()
    conn.close()

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        min-height:100vh;
        color:white;
    }}

    .box {{
        background: rgba(0,0,0,0.75);
        padding:40px;
        border-radius:20px;
        width:400px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        animation: fadeIn 0.7s ease;
    }}

    .card {{
        background: rgba(255,255,255,0.05);
        padding:15px;
        border-radius:10px;
        margin:10px 0;
    }}

    button {{
        margin-top:20px;
        padding:12px;
        width:100%;
        border:none;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        font-size:16px;
        cursor:pointer;
    }}

    button:hover {{
        transform: scale(1.05);
    }}

    @keyframes fadeIn {{
        from {{opacity:0; transform:translateY(20px);}}
        to {{opacity:1; transform:translateY(0);}}
    }}

    </style>
    </head>

    <body>

    <div class="box">

        <h1>🔥 Your Smart Plan</h1>

        <div class="card">
            <p><b>BMI:</b> {round(bmi,2)} ({bmi_msg})</p>
            <p><b>Calories:</b> {calories}</p>
            <p><b>Protein:</b> {protein} g</p>
        </div>

        <div class="card">
            <p><b>🎯 Goal:</b> {goal_msg}</p>
            <p><b>🔥 Fat Plan:</b> {fat_msg}</p>
        </div>

        <div class="card">
            <p><b>💰 Budget:</b> ₹{budget}</p>
            <p><b>🍽️ Diet:</b> {diet}</p>
        </div>

        <a href="/"><button>🏠 Go Home</button></a>

    </div>

    </body>
    </html>
    """
@app.route("/plan")
def plan():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        min-height:100vh;
        color:white;
    }

    .box {
        background: rgba(0,0,0,0.75);
        padding:40px;
        border-radius:20px;
        width:400px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        animation: fadeIn 0.7s ease;
    }

    h2 {
        margin-bottom:20px;
    }

    input, select {
        width:90%;
        padding:12px;
        margin:10px 0;
        border:none;
        border-radius:8px;
        outline:none;
    }

    button {
        width:100%;
        padding:12px;
        margin-top:15px;
        border:none;
        border-radius:10px;
        font-size:16px;
        cursor:pointer;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        transition:0.3s;
    }

    button:hover {
        transform: scale(1.05);
    }

    @keyframes fadeIn {
        from {opacity:0; transform:translateY(20px);}
        to {opacity:1; transform:translateY(0);}
    }

    </style>
    </head>

    <body>

    <div class="box">

        <h2>💪 Fill Your Details</h2>

        <form action="/result" method="post">

        <input type="number" name="age" placeholder="Age" required>

        <input type="number" name="height" step="0.1" placeholder="Height (cm)" required>

        <input type="number" name="weight" placeholder="Weight (kg)" required>

        <select name="goal" required>
            <option value="">🎯 Select Goal</option>
            <option value="gain">Weight Gain</option>
            <option value="loss">Weight Loss</option>
        </select>

        <select name="work" required>
            <option value="">💼 Work Type</option>
            <option value="office">Office Job</option>
            <option value="physical">Physical Job</option>
        </select>

        <input type="number" name="fat" placeholder="Body Fat %" required>

        <select name="fat_goal" required>
            <option value="">🔥 Fat Goal</option>
            <option value="loss">Reduce Fat</option>
            <option value="gain">Increase Fat</option>
        </select>

        <input type="number" name="budget" placeholder="Budget ₹/day" required>

        <button>🚀 Generate Plan</button>

        </form>

    </div>

    </body>
    </html>
    """
@app.route("/myplan")
def myplan():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT * FROM plans WHERE username=?", (username,))
    data = c.fetchall()

    conn.close()

    if not data:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>No plans found 😅</h2>
        <a href='/plan' style="color:cyan;">Create Plan</a>
        </body>
        </html>
        """

    result = """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
    }

    h1 {
        text-align:center;
        padding-top:20px;
    }

    .container {
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
        padding:20px;
    }

    .card {
        background: rgba(0,0,0,0.75);
        padding:20px;
        margin:10px;
        border-radius:15px;
        width:250px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
        transition:0.3s;
    }

    .card:hover {
        transform: scale(1.05);
    }

    p {
        margin:5px 0;
    }

    .home-btn {
        display:block;
        width:200px;
        margin:30px auto;
        padding:12px;
        text-align:center;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }

    </style>
    </head>

    <body>

    <h1>📋 My All Plans</h1>

    <div class="container">
    """

    for row in data:
        result += f"""
        <div class="card">
            <p><b>Age:</b> {row[1]}</p>
            <p><b>Height:</b> {row[2]} cm</p>
            <p><b>Weight:</b> {row[3]} kg</p>
            <p><b>Goal:</b> {row[4]}</p>
            <p><b>Work:</b> {row[5]}</p>
            <p><b>Fat %:</b> {row[6]}</p>
            <p><b>Fat Goal:</b> {row[7]}</p>
            <p><b>Budget:</b> ₹{row[8]}</p>
        </div>
        """

    result += """
    </div>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """

    return result
@app.route("/daily")
def daily():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT weight, goal, work FROM plans WHERE username=? ORDER BY rowid DESC LIMIT 1", (username,))
    data = c.fetchone()
    conn.close()

    if not data:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>No plan found 😅</h2>
        <a href='/plan' style="color:cyan;">Create Plan</a>
        </body>
        </html>
        """

    weight, goal, work = data

    base = weight * (30 if work == "office" else 40)

    if goal == "loss":
        calories = base - 400
        advice = "🔥 Fat loss focus: high protein + cardio (30 min walk/jog)"
    else:
        calories = base + 400
        advice = "💪 Muscle gain focus: high protein + strength training"

    protein = round(weight * 1.6, 1)

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }}

    .box {{
        background: rgba(0,0,0,0.75);
        padding:40px;
        border-radius:20px;
        width:400px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        animation: fadeIn 0.7s ease;
    }}

    .card {{
        background: rgba(255,255,255,0.05);
        padding:15px;
        border-radius:10px;
        margin:10px 0;
    }}

    h1 {{
        margin-bottom:20px;
    }}

    button {{
        margin-top:20px;
        padding:12px;
        width:100%;
        border:none;
        border-radius:10px;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        font-size:16px;
        cursor:pointer;
    }}

    button:hover {{
        transform: scale(1.05);
    }}

    @keyframes fadeIn {{
        from {{opacity:0; transform:translateY(20px);}}
        to {{opacity:1; transform:translateY(0);}}
    }}

    </style>
    </head>

    <body>

    <div class="box">

        <h1>📅 Daily Plan</h1>

        <div class="card">
            <h3>🔥 Calories Target</h3>
            <p>{calories}</p>
        </div>

        <div class="card">
            <h3>💪 Protein Target</h3>
            <p>{protein} g</p>
        </div>

        <div class="card">
            <h3>⚡ Advice</h3>
            <p>{advice}</p>
        </div>

        <a href="/"><button>🏠 Go Home</button></a>

    </div>

    </body>
    </html>
    """
@app.route("/coach")
def coach():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
    SELECT weight, goal, work, fat 
    FROM plans 
    WHERE username=? 
    ORDER BY rowid DESC LIMIT 1
    """, (username,))
    plan = c.fetchone()

    c.execute("""
    SELECT calories, protein, running 
    FROM daily 
    WHERE username=? 
    ORDER BY rowid DESC LIMIT 1
    """, (username,))
    daily = c.fetchone()

    conn.close()

    if not plan:
        return "<h2>⚠️ Pehle plan banao</h2>"

    if not daily:
        return "<h2>⚠️ Pehle daily data fill karo</h2>"

    weight, goal, work, fat = plan
    taken_cal, taken_protein, running = daily

    target_cal = weight * (30 if work == "office" else 40)
    target_cal = target_cal - 400 if goal == "loss" else target_cal + 400
    target_protein = weight * 1.6

    # 🔥 LOGIC SAME
    if goal == "loss":
        cal_msg = "❌ Jyada calories → fat badhega" if taken_cal > target_cal else "✅ Perfect deficit"
    else:
        cal_msg = "❌ Kam calories → gain nahi hoga" if taken_cal < target_cal else "✅ Perfect surplus"

    protein_msg = "⚠️ Protein kam hai" if taken_protein < target_protein else "💪 Protein perfect"

    if goal == "loss":
        activity_tip = "🔥 Running badhao (2-3 km)" if running < 2 else "✅ Good cardio"
        diet = "🥗 Low calorie diet"
        workout = "🏃 Cardio + light workout"
        fat_tip = "🚫 Sugar & fried avoid karo"
    else:
        activity_tip = "🏋️ Gym focus karo"
        diet = "🍚 High calorie diet"
        workout = "🏋️ Heavy training"
        fat_tip = "💪 Clean bulk karo"

    if goal == "loss":
        final_msg = "🔥 Fat loss mode ON" if taken_cal <= target_cal else "❌ Control toot gaya"
    else:
        final_msg = "💪 Muscle gain ON" if taken_cal >= target_cal else "❌ Growth ruk gayi"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
    }}

    h1 {{
        text-align:center;
        padding:20px;
    }}

    .container {{
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        margin:10px;
        border-radius:15px;
        width:260px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
        transition:0.3s;
    }}

    .card:hover {{
        transform: scale(1.05);
    }}

    .big {{
        width:540px;
        text-align:center;
        background: linear-gradient(45deg, #ff512f, #dd2476);
    }}

    .home-btn {{
        display:block;
        width:200px;
        margin:30px auto;
        padding:12px;
        text-align:center;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🤖 AI Fitness Coach</h1>

    <div class="container">

        <div class="card">
            <h3>🔥 Calories</h3>
            <p>{taken_cal} / {target_cal}</p>
            <p>{cal_msg}</p>
        </div>

        <div class="card">
            <h3>💪 Protein</h3>
            <p>{taken_protein} / {round(target_protein)}</p>
            <p>{protein_msg}</p>
        </div>

        <div class="card">
            <h3>🏃 Activity</h3>
            <p>{running} km</p>
            <p>{activity_tip}</p>
        </div>

        <div class="card big">
            <h2>{final_msg}</h2>
        </div>

        <div class="card">
            <h3>🍽️ Diet</h3>
            <p>{diet}</p>
        </div>

        <div class="card">
            <h3>🏋️ Workout</h3>
            <p>{workout}</p>
        </div>

        <div class="card">
            <h3>⚡ Fat Tips</h3>
            <p>{fat_tip}</p>
        </div>

    </div>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """
@app.route("/weekplan")
def weekplan():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT weight, goal, work FROM plans WHERE username=? ORDER BY rowid DESC LIMIT 1", (username,))
    data = c.fetchone()
    conn.close()

    if not data:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>No plan found 😅</h2>
        <a href='/plan' style="color:cyan;">Create Plan</a>
        </body>
        </html>
        """

    weight, goal, work = data

    focus = "🔥 Fat Loss Plan" if goal == "loss" else "💪 Muscle Gain Plan"

    plan = {
        "Monday": "Chest + 20 min cardio",
        "Tuesday": "Back + Abs workout",
        "Wednesday": "Leg day + walking",
        "Thursday": "Shoulder + light cardio",
        "Friday": "Arms + Abs",
        "Saturday": "Full body workout",
        "Sunday": "Rest + stretching 🧘"
    }

    result = f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
    }}

    h1 {{
        text-align:center;
        padding:20px;
    }}

    .container {{
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        margin:10px;
        border-radius:15px;
        width:220px;
        text-align:center;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
        transition:0.3s;
    }}

    .card:hover {{
        transform: scale(1.05);
    }}

    .day {{
        font-size:18px;
        font-weight:bold;
        margin-bottom:10px;
        color:#00ffcc;
    }}

    .home-btn {{
        display:block;
        width:200px;
        margin:30px auto;
        padding:12px;
        text-align:center;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>📅 7 Day Plan<br><small>{focus}</small></h1>

    <div class="container">
    """

    for day, task in plan.items():
        result += f"""
        <div class="card">
            <div class="day">{day}</div>
            <p>{task}</p>
        </div>
        """

    result += """
    </div>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """

    return result
@app.route("/budget_plan")
def budget_plan():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT budget, goal FROM plans WHERE username=? ORDER BY rowid DESC LIMIT 1", (username,))
    data = c.fetchone()
    conn.close()

    if not data:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>No plan found 😅</h2>
        <a href='/plan' style="color:cyan;">Create Plan</a>
        </body>
        </html>
        """

    budget, goal = data

    # 🔥 FOOD LOGIC
    if budget < 100:
        food = ["🥚 Eggs", "🍚 Rice + Dal", "🥛 Milk", "🥜 Peanuts"]
    elif budget < 200:
        food = ["🥚 Eggs", "🍌 Banana", "🥛 Milk", "🍚 Rice + Dal"]
    else:
        food = ["🍗 Chicken", "🧀 Paneer", "🥚 Eggs", "🍎 Fruits", "🥛 Milk"]

    tip = "🔥 Avoid sugar & fried food" if goal == "loss" else "💪 Eat surplus clean calories"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
    }}

    h1 {{
        text-align:center;
        padding:20px;
    }}

    .container {{
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        margin:10px;
        border-radius:15px;
        width:200px;
        text-align:center;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
        transition:0.3s;
        font-size:18px;
    }}

    .card:hover {{
        transform: scale(1.08);
    }}

    .tip {{
        text-align:center;
        margin-top:20px;
        font-size:20px;
        color:#00ffcc;
    }}

    .home-btn {{
        display:block;
        width:200px;
        margin:30px auto;
        padding:12px;
        text-align:center;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🛒 Budget Diet Plan (₹{budget})</h1>

    <div class="container">
    """

    for item in food:
        result += f"""
        <div class="card">
            {item}
        </div>
        """

    result += f"""
    </div>

    <div class="tip">{tip}</div>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """

    return result
@app.route("/progress_ai")
def progress_ai():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT weight FROM plans WHERE username=? ORDER BY rowid DESC", (username,))
    data = c.fetchall()

    conn.close()

    if len(data) < 2:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>Need at least 2 entries 📊</h2>
        <a href='/plan' style="color:cyan;">Add More Data</a>
        </body>
        </html>
        """

    last_weight = data[-1][0]
    prev_weight = data[-2][0]

    diff = round(last_weight - prev_weight, 2)

    # 🔥 AI LOGIC
    if diff < 0:
        msg = "🔥 Great! Weight decreasing (fat loss progress)"
        advice = "Continue calorie deficit + cardio 🏃"
        color = "#00ff99"
    elif diff > 0:
        msg = "💪 Weight increasing (muscle/fat gain)"
        advice = "Check diet + focus on strength training 🏋️"
        color = "#ffaa00"
    else:
        msg = "⚖️ No change in weight"
        advice = "Adjust calories slightly (+/-200)"
        color = "#00c6ff"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        text-align:center;
    }}

    h1 {{
        padding:20px;
    }}

    .container {{
        display:flex;
        justify-content:center;
        gap:20px;
        flex-wrap:wrap;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
        width:220px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
    }}

    .result {{
        margin-top:20px;
        padding:25px;
        border-radius:15px;
        background: {color};
        color:black;
        width:60%;
        margin-left:auto;
        margin-right:auto;
        font-weight:bold;
    }}

    .home-btn {{
        display:inline-block;
        margin-top:30px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🤖 AI Progress Analysis</h1>

    <div class="container">

        <div class="card">
            <h3>📉 Previous</h3>
            <p>{prev_weight} kg</p>
        </div>

        <div class="card">
            <h3>📈 Current</h3>
            <p>{last_weight} kg</p>
        </div>

        <div class="card">
            <h3>⚖️ Change</h3>
            <p>{diff} kg</p>
        </div>

    </div>

    <div class="result">
        {msg}<br><br>
        👉 {advice}
    </div>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """
@app.route("/auto_adjust")
def auto_adjust():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
        SELECT weight, fat, goal, budget
        FROM plans
        WHERE username=?
        ORDER BY rowid DESC
        LIMIT 2
    """, (username,))

    data = c.fetchall()
    conn.close()

    if len(data) < 2:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>⚠️ Need at least 2 entries</h2>
        <a href='/plan' style="color:cyan;">Add Data</a>
        </body>
        </html>
        """

    prev = data[-2]
    curr = data[-1]

    prev_weight, prev_fat, _, _ = prev
    curr_weight, curr_fat, goal, budget = curr

    weight_change = round(curr_weight - prev_weight, 2)
    fat_change = round(curr_fat - prev_fat, 2)

    advice = []
    calories_adjust = 0

    # 🔥 LOGIC
    if goal == "loss":
        if weight_change >= 0:
            advice.append("🔥 Fat loss slow → reduce calories")
            calories_adjust -= 200
        else:
            advice.append("✅ Good fat loss progress")
    else:
        if weight_change <= 0:
            advice.append("💪 Muscle gain slow → increase calories")
            calories_adjust += 200
        else:
            advice.append("✅ Good muscle gain progress")

    if fat_change > 0:
        advice.append("⚠️ Fat increasing → add cardio + clean diet")
        calories_adjust -= 100
    else:
        advice.append("✅ Fat under control")

    # 🔥 FINAL RESULT STYLE
    if calories_adjust > 0:
        cal_msg = f"⬆️ Increase calories by +{calories_adjust}"
        color = "#00ff99"
    elif calories_adjust < 0:
        cal_msg = f"⬇️ Reduce calories by {calories_adjust}"
        color = "#ff4d4d"
    else:
        cal_msg = "⚖️ Calories stable"
        color = "#00c6ff"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        text-align:center;
    }}

    h1 {{
        padding:20px;
    }}

    .container {{
        display:flex;
        justify-content:center;
        gap:20px;
        flex-wrap:wrap;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
        width:220px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
    }}

    .analysis {{
        margin-top:20px;
        text-align:left;
        display:inline-block;
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
    }}

    .result {{
        margin-top:20px;
        padding:25px;
        border-radius:15px;
        background: {color};
        color:black;
        font-size:20px;
        font-weight:bold;
        width:60%;
        margin-left:auto;
        margin-right:auto;
    }}

    .home-btn {{
        display:inline-block;
        margin-top:30px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🤖 Auto Adjust AI</h1>

    <div class="container">

        <div class="card">
            <h3>⚖️ Weight Change</h3>
            <p>{weight_change} kg</p>
        </div>

        <div class="card">
            <h3>📉 Fat Change</h3>
            <p>{fat_change} %</p>
        </div>

    </div>

    <div class="analysis">
        <h3>📌 AI Analysis</h3>
        <ul>
            {''.join([f"<li>{a}</li>" for a in advice])}
        </ul>
    </div>

    <div class="result">
        {cal_msg}
    </div>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """
@app.route("/coach_chat")
def coach_chat():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        display:flex;
        flex-direction:column;
        height:100vh;
    }

    .header {
        text-align:center;
        padding:15px;
        background: rgba(0,0,0,0.8);
        font-size:20px;
        font-weight:bold;
    }

    .chat-box {
        flex:1;
        padding:20px;
        overflow-y:auto;
    }

    .msg-user {
        text-align:right;
        margin:10px;
    }

    .msg-bot {
        text-align:left;
        margin:10px;
    }

    .bubble-user {
        display:inline-block;
        background:#0072ff;
        padding:10px 15px;
        border-radius:15px;
        max-width:60%;
    }

    .bubble-bot {
        display:inline-block;
        background:#444;
        padding:10px 15px;
        border-radius:15px;
        max-width:60%;
    }

    .input-box {
        display:flex;
        padding:10px;
        background: rgba(0,0,0,0.9);
    }

    input {
        flex:1;
        padding:10px;
        border:none;
        border-radius:10px;
        outline:none;
    }

    button {
        margin-left:10px;
        padding:10px 20px;
        border:none;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        cursor:pointer;
    }

    </style>
    </head>

    <body>

    <div class="header">💬 AI Fitness Coach</div>

    <div class="chat-box" id="chat">
        <div class="msg-bot">
            <div class="bubble-bot">👋 Ask me anything about fitness!</div>
        </div>
    </div>

    <form class="input-box" action="/chat_reply" method="post">
        <input type="text" name="msg" placeholder="Type your message..." required>
        <button>Send</button>
    </form>

    </body>
    </html>
    """
@app.route("/chat_reply", methods=["POST"])
def chat_reply():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    user_msg = request.form["msg"]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly AI coach. Talk like a real human. Answer in Hindi or English based on user language. Help with fitness, business, life, anything."
                },
                {
                    "role": "user",
                    "content": user_msg
                }
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"⚠️ Error: {e}"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        display:flex;
        flex-direction:column;
        height:100vh;
    }}

    .header {{
        text-align:center;
        padding:15px;
        background: rgba(0,0,0,0.8);
        font-size:20px;
        font-weight:bold;
    }}

    .chat-box {{
        flex:1;
        padding:20px;
        overflow-y:auto;
    }}

    .msg-user {{
        text-align:right;
        margin:10px;
    }}

    .msg-bot {{
        text-align:left;
        margin:10px;
    }}

    .bubble-user {{
        display:inline-block;
        background:#0072ff;
        padding:10px 15px;
        border-radius:15px;
        max-width:60%;
    }}

    .bubble-bot {{
        display:inline-block;
        background:#444;
        padding:10px 15px;
        border-radius:15px;
        max-width:60%;
    }}

    .input-box {{
        display:flex;
        padding:10px;
        background: rgba(0,0,0,0.9);
    }}

    input {{
        flex:1;
        padding:10px;
        border:none;
        border-radius:10px;
        outline:none;
    }}

    button {{
        margin-left:10px;
        padding:10px 20px;
        border:none;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        cursor:pointer;
    }}

    </style>
    </head>

    <body>

    <div class="header">💬 AI Fitness Coach</div>

    <div class="chat-box">

        <div class="msg-user">
            <div class="bubble-user">{user_msg}</div>
        </div>

        <div class="msg-bot">
            <div class="bubble-bot">{reply}</div>
        </div>

    </div>

    <form class="input-box" action="/chat_reply" method="post">
        <input type="text" name="msg" placeholder="Type again..." required>
        <button>Send</button>
    </form>

    </body>
    </html>
    """
@app.route("/ai_coach_v2")
def ai_coach_v2():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT weight, goal, work, fat, budget FROM plans WHERE username=? ORDER BY rowid DESC LIMIT 1", (username,))
    data = c.fetchone()
    conn.close()

    if not data:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>No plan found 😅</h2>
        <a href='/plan' style="color:cyan;">Create Plan</a>
        </body>
        </html>
        """

    weight, goal, work, fat, budget = data

    # 🔥 AI LOGIC
    calories = weight * (40 if work == "physical" else 30)

    if goal == "loss":
        calories -= 400
        diet = "🥗 High protein + low carb diet"
        mode = "🔥 Fat Loss Mode"
    else:
        calories += 400
        diet = "🍚 High calorie clean bulking diet"
        mode = "💪 Muscle Gain Mode"

    fat_tip = "⚠️ Fat control needed" if fat > 18 else "✅ Fat under control"
    budget_tip = "💰 Budget diet focus" if budget < 150 else "💪 Balanced diet possible"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        text-align:center;
    }}

    h1 {{
        padding:20px;
    }}

    .mode {{
        font-size:22px;
        margin-bottom:10px;
        color:#00ffcc;
    }}

    .container {{
        display:flex;
        justify-content:center;
        flex-wrap:wrap;
        gap:20px;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
        width:220px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
    }}

    .highlight {{
        margin:20px auto;
        padding:20px;
        width:60%;
        background:#00c6ff;
        color:black;
        border-radius:15px;
        font-weight:bold;
        font-size:20px;
    }}

    .home-btn {{
        display:inline-block;
        margin-top:30px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🤖 AI Coach V2</h1>

    <div class="mode">{mode}</div>

    <div class="container">

        <div class="card">
            <h3>⚖️ Weight</h3>
            <p>{weight} kg</p>
        </div>

        <div class="card">
            <h3>🔥 Calories</h3>
            <p>{calories}</p>
        </div>

        <div class="card">
            <h3>💪 Body Fat</h3>
            <p>{fat}%</p>
        </div>

        <div class="card">
            <h3>💰 Budget</h3>
            <p>₹{budget}</p>
        </div>

    </div>

    <div class="highlight">
        {diet}
    </div>

    <p>{fat_tip}</p>
    <p>{budget_tip}</p>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """
@app.route("/ai_personal_plan")
def ai_personal_plan():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("SELECT age, height, weight, goal, work, fat, budget FROM plans WHERE username=? ORDER BY rowid DESC LIMIT 1", (username,))
    data = c.fetchone()
    conn.close()

    if not data:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>No data 😅</h2>
        <a href='/plan' style="color:cyan;">Create Plan</a>
        </body>
        </html>
        """

    age, height, weight, goal, work, fat, budget = data

    bmi = round(weight / ((height/100) ** 2), 2)

    # 🔥 AI LOGIC
    if goal == "loss":
        plan = "🏃 Daily 30 min cardio + low carb diet"
        mode = "🔥 Fat Loss Plan"
    else:
        plan = "🏋️ Heavy workout + high protein diet"
        mode = "💪 Muscle Gain Plan"

    if fat > 20:
        fat_plan = "⚠️ High fat → strict diet + cardio needed"
        fat_color = "#ff4d4d"
    else:
        fat_plan = "✅ Fat level is good"
        fat_color = "#00ff99"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        text-align:center;
    }}

    h1 {{
        padding:20px;
    }}

    .mode {{
        font-size:22px;
        margin-bottom:15px;
        color:#00ffcc;
    }}

    .container {{
        display:flex;
        justify-content:center;
        flex-wrap:wrap;
        gap:20px;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
        width:200px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
    }}

    .highlight {{
        margin:20px auto;
        padding:20px;
        width:60%;
        background:#00c6ff;
        color:black;
        border-radius:15px;
        font-weight:bold;
        font-size:20px;
    }}

    .fat-box {{
        margin:20px auto;
        padding:15px;
        width:50%;
        border-radius:12px;
        background:{fat_color};
        color:black;
        font-weight:bold;
    }}

    .home-btn {{
        display:inline-block;
        margin-top:30px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🤖 Personal AI Plan</h1>

    <div class="mode">{mode}</div>

    <div class="container">

        <div class="card">
            <h3>🎂 Age</h3>
            <p>{age}</p>
        </div>

        <div class="card">
            <h3>📏 Height</h3>
            <p>{height} cm</p>
        </div>

        <div class="card">
            <h3>⚖️ Weight</h3>
            <p>{weight} kg</p>
        </div>

        <div class="card">
            <h3>📊 BMI</h3>
            <p>{bmi}</p>
        </div>

    </div>

    <div class="highlight">
        {plan}
    </div>

    <div class="fat-box">
        {fat_plan}
    </div>

    <p>💰 Budget: ₹{budget}</p>

    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """
@app.route("/weekly_graph")
def weekly_graph():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
        SELECT weight, fat
        FROM plans
        WHERE username=?
        ORDER BY rowid DESC LIMIT 7
    """, (username,))

    data = c.fetchall()
    conn.close()

    if len(data) < 2:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>📊 Not enough data</h2>
        <a href='/plan' style="color:cyan;">Add More Data</a>
        </body>
        </html>
        """

    weight = [row[0] for row in data][::-1]
    fat = [row[1] for row in data][::-1]

    # 🔥 GRAPH
    plt.figure(figsize=(6,4))
    plt.plot(weight, marker='o', label="Weight")
    plt.plot(fat, marker='o', label="Fat %")
    plt.legend()
    plt.title("Weekly Progress 📈")

    plt.savefig("static/weekly.png")
    plt.close()

    # 🔥 ANALYSIS
    weight_change = round(weight[-1] - weight[0], 2)
    fat_change = round(fat[-1] - fat[0], 2)

    if weight_change < 0:
        w_msg = "🔥 Weight decreasing (good for fat loss)"
    elif weight_change > 0:
        w_msg = "💪 Weight increasing"
    else:
        w_msg = "⚖️ No weight change"

    if fat_change < 0:
        f_msg = "🔥 Fat decreasing (great progress)"
    elif fat_change > 0:
        f_msg = "⚠️ Fat increasing"
    else:
        f_msg = "⚖️ No fat change"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        text-align:center;
    }}

    h1 {{
        padding:20px;
    }}

    .container {{
        display:flex;
        justify-content:center;
        gap:20px;
        flex-wrap:wrap;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
        width:220px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
    }}

    img {{
        margin-top:20px;
        border-radius:10px;
        width:70%;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
    }}

    .home-btn {{
        display:inline-block;
        margin-top:30px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>📈 Weekly Progress</h1>

    <div class="container">

        <div class="card">
            <h3>⚖️ Weight Change</h3>
            <p>{weight_change} kg</p>
            <p>{w_msg}</p>
        </div>

        <div class="card">
            <h3>🔥 Fat Change</h3>
            <p>{fat_change} %</p>
            <p>{f_msg}</p>
        </div>

    </div>

    <img src="/static/weekly.png">

    <br>
    <a href="/" class="home-btn">🏠 Go Home</a>

    </body>
    </html>
    """
@app.route("/goal_predict")
def goal_predict():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""
        SELECT weight, goal
        FROM plans
        WHERE username=?
        ORDER BY rowid DESC LIMIT 5
    """, (username,))

    data = c.fetchall()
    conn.close()

    if len(data) < 2:
        return """
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:100px;">
        <h2>📊 Need more data</h2>
        <a href='/plan' style="color:cyan;">Add More Entries</a>
        </body>
        </html>
        """

    weights = [row[0] for row in data][::-1]
    goal = data[-1][1]

    start = weights[0]
    current = weights[-1]

    total_change = round(current - start, 2)

    # 🔥 avg change per entry
    changes = []
    for i in range(1, len(weights)):
        changes.append(weights[i] - weights[i-1])

    avg_change = sum(changes) / len(changes)

    # 🎯 prediction logic
    if goal == "loss":
        target_weight = current - 5   # lose 5kg target
        if avg_change >= 0:
            days = "❌ No fat loss trend"
            msg = "⚠️ Progress wrong direction"
        else:
            days = int(abs((target_weight - current) / avg_change) * 7)
            msg = "🔥 Fat loss on track"
    else:
        target_weight = current + 5   # gain 5kg target
        if avg_change <= 0:
            days = "❌ No muscle gain trend"
            msg = "⚠️ Progress too slow"
        else:
            days = int(abs((target_weight - current) / avg_change) * 7)
            msg = "💪 Muscle gain on track"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        color:white;
        text-align:center;
    }}

    h1 {{
        padding:20px;
    }}

    .container {{
        display:flex;
        justify-content:center;
        gap:20px;
        flex-wrap:wrap;
        padding:20px;
    }}

    .card {{
        background: rgba(0,0,0,0.75);
        padding:20px;
        border-radius:15px;
        width:220px;
        box-shadow:0 8px 25px rgba(0,0,0,0.7);
    }}

    .highlight {{
        margin:20px auto;
        padding:20px;
        width:60%;
        background:#00c6ff;
        color:black;
        border-radius:15px;
        font-weight:bold;
        font-size:20px;
    }}

    .home-btn {{
        display:inline-block;
        margin-top:30px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <h1>🎯 Goal Prediction</h1>

    <div class="container">

        <div class="card">
            <h3>Start Weight</h3>
            <p>{start} kg</p>
        </div>

        <div class="card">
            <h3>Current</h3>
            <p>{current} kg</p>
        </div>

        <div class="card">
            <h3>Total Change</h3>
            <p>{total_change} kg</p>
        </div>

    </div>

    <div class="highlight">
        {msg}
    </div>

    <h3>⏳ Estimated Time: {days} days</h3>

    <a href="/" class="home-btn">🏠 Home</a>

    </body>
    </html>
    """
@app.route("/simulate", methods=["POST", "GET"])
def simulate():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    if request.method == "GET":
        return """
        <html>
        <head>
        <style>

        body {
            margin:0;
            font-family:sans-serif;
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
            url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
            color:white;
        }

        .box {
            background: rgba(0,0,0,0.65);
            padding:40px;
            border-radius:20px;
            text-align:center;
            box-shadow:0 10px 30px rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
        }

        input {
            padding:12px;
            width:220px;
            border:none;
            border-radius:8px;
            margin-top:10px;
        }

        button {
            margin-top:15px;
            padding:12px 25px;
            border:none;
            border-radius:10px;
            background: linear-gradient(45deg, #00c6ff, #0072ff);
            color:white;
            cursor:pointer;
        }

        button:hover {
            transform: scale(1.05);
        }

        </style>
        </head>

        <body>

        <div class="box">
            <h2>🧠 AI Simulator</h2>

            <form method="post">
                <input type="number" name="change" placeholder="Change Weight (kg)" required><br>
                <button>Check Result</button>
            </form>
        </div>

        </body>
        </html>
        """

    # POST
    try:
        change = int(request.form["change"])
    except:
        return "<h2>⚠️ Invalid input</h2>"

    if change < 0:
        result = "🔥 Fat loss: body lean ho jayegi + stamina increase"
        color = "#00ffcc"
    else:
        result = "💪 Muscle gain: strength + weight increase"
        color = "#00c6ff"

    return f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }}

    .box {{
        background: rgba(0,0,0,0.65);
        padding:40px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
    }}

    .result {{
        margin-top:15px;
        padding:15px;
        border-radius:10px;
        background:{color};
        color:black;
        font-weight:bold;
    }}

    a {{
        display:inline-block;
        margin-top:20px;
        padding:10px 20px;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        border-radius:10px;
        text-decoration:none;
    }}

    </style>
    </head>

    <body>

    <div class="box">
        <h2>🧠 Simulation Result</h2>

        <div class="result">
            {result}
        </div>

        <a href="/">🏠 Home</a>
    </div>

    </body>
    </html>
    """
@app.route("/logout")
def logout():
    session.pop("user", None)   # 🔥 logout

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }

    .box {
        background: rgba(0,0,0,0.65);
        padding:50px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        animation: fadeIn 0.6s ease;
    }

    h2 {
        font-size:28px;
        margin-bottom:15px;
        color:#00ffcc;
    }

    p {
        color:#ccc;
        font-size:16px;
    }

    .btn {
        display:inline-block;
        margin-top:20px;
        padding:12px 25px;
        border-radius:10px;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        text-decoration:none;
        transition:0.3s;
    }

    .btn:hover {
        transform: scale(1.05);
    }

    @keyframes fadeIn {
        from {opacity:0; transform:translateY(20px);}
        to {opacity:1; transform:translateY(0);}
    }

    </style>
    </head>

    <body>

    <div class="box">
        <h2>🚪 Logged Out</h2>
        <p>You have been logged out successfully</p>

        <a href="/login" class="btn">🔐 Login Again</a>
    </div>

    </body>
    </html>
    """
@app.route("/daily_input")
def daily_input():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }

    .box {
        background: rgba(0,0,0,0.65);
        padding:40px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        width:300px;
    }

    h2 {
        margin-bottom:20px;
        font-size:28px;
    }

    input {
        width:90%;
        padding:12px;
        margin:10px 0;
        border:none;
        border-radius:8px;
        outline:none;
        font-size:14px;
    }

    button {
        width:95%;
        padding:12px;
        margin-top:10px;
        border:none;
        border-radius:10px;
        font-size:16px;
        cursor:pointer;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color:white;
        transition:0.3s;
        box-shadow:0 4px 15px rgba(0,0,0,0.4);
    }

    button:hover {
        transform: scale(1.05);
    }

    .home-btn {
        display:block;
        margin-top:15px;
        padding:10px;
        border-radius:10px;
        background: linear-gradient(45deg, #ff512f, #dd2476);
        color:white;
        text-decoration:none;
    }

    </style>
    </head>

    <body>

    <div class="box">
        <h2>📅 Daily Entry</h2>

        <form action="/save_daily" method="post">

            <input type="number" name="calories" placeholder="Calories Taken" required>

            <input type="number" name="protein" placeholder="Protein (g)" required>

            <input type="number" name="running" step="0.1" placeholder="Running (km)" required>

            <button>💾 Save</button>

        </form>

        <a href="/" class="home-btn">🏠 Home</a>
    </div>

    </body>
    </html>
    """
@app.route("/save_daily", methods=["POST"])
def save_daily():
    if "user" not in session:
        return "<h2>Please login first 🔐</h2>"

    username = session["user"]

    calories = int(request.form["calories"])
    protein = int(request.form["protein"])
    running = float(request.form["running"])

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("INSERT INTO daily VALUES (?, ?, ?, ?)",
              (username, calories, protein, running))

    conn.commit()
    conn.close()

    return """
    <html>
    <head>
    <style>

    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)),
        url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }

    .box {
        background: rgba(0,0,0,0.65);
        padding:50px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 10px 30px rgba(0,0,0,0.7);
        backdrop-filter: blur(8px);
        animation: fadeIn 0.8s ease;
    }

    .tick {
        font-size:60px;
        margin-bottom:10px;
        animation: pop 0.5s ease;
    }

    h2 {
        font-size:30px;
        color:#00ffcc;
    }

    p {
        color:#ccc;
        margin-top:10px;
    }

    @keyframes fadeIn {
        from {opacity:0; transform:translateY(20px);}
        to {opacity:1; transform:translateY(0);}
    }

    @keyframes pop {
        0% {transform: scale(0);}
        100% {transform: scale(1);}
    }

    </style>

    <script>
        setTimeout(function(){
            window.location.href = "/";
        }, 2000);
    </script>

    </head>

    <body>

    <div class="box">
        <div class="tick">✅</div>
        <h2>Data Saved Successfully</h2>
        <p>Redirecting to Home...</p>
    </div>

    </body>
    </html>
    """
@app.route("/start")
def start():
    return """
    <html>
    <head>
        <style>

            body {
                margin:0;
                height:100vh;
                display:flex;
                justify-content:center;
                align-items:center;
                flex-direction:column;
                background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.9)),
                url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438') no-repeat center center/cover;
                color:white;
                font-family:sans-serif;
                overflow:hidden;
            }

            h1 {
                font-size:60px;
                letter-spacing:3px;
                text-shadow:0 0 20px #ff4b2b, 0 0 40px #ff416c;
                animation: zoomIn 1.5s ease;
            }

            p {
                margin-top:10px;
                font-size:18px;
                color:#ccc;
                animation: fadeIn 2s ease;
            }

            .loader {
                margin-top:30px;
                border:4px solid rgba(255,255,255,0.2);
                border-top:4px solid #ff416c;
                border-radius:50%;
                width:40px;
                height:40px;
                animation: spin 1s linear infinite;
            }

            @keyframes zoomIn {
                from {opacity:0; transform:scale(0.5);}
                to {opacity:1; transform:scale(1);}
            }

            @keyframes fadeIn {
                from {opacity:0;}
                to {opacity:1;}
            }

            @keyframes spin {
                0% {transform: rotate(0deg);}
                100% {transform: rotate(360deg);}
            }

        </style>
    </head>

    <body>

        <h1>🔥 FITNESS PRO 🔥</h1>
        <p>Your Smart Fitness Companion</p>

        <div class="loader"></div>

        <script>
            setTimeout(() => {
                window.location.href = "/login";
            }, 2500);
        </script>

    </body>
    </html>
    """
# Run app
if __name__ == "__main__":
    init_db()
    os.makedirs("static", exist_ok=True)

    print("🔥 Fitness App Running...")
    print("👉 Open: http://127.0.0.1:5000/start")

    app.run(debug=True)