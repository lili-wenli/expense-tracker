from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# 初始化数据库
def init_db():
    conn = sqlite3.connect('expense.db')
    cursor = conn.cursor()

    # 用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    # 记账表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expense (
        user_id INTEGER,
        type TEXT,
        category TEXT,
        amount INTEGER
    )
    ''')

    conn.commit()
    conn.close()

init_db()


# 默认打开 → Register
@app.route("/")
def index():
    return redirect(url_for("register"))


# 注册
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect('expense.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# 登录
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect('expense.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        else:
            return "Login failed"

    return render_template("login.html")


# 主页面
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect('expense.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT rowid, * FROM expense WHERE user_id=?",
        (session["user_id"],)
    )
    rows = cursor.fetchall()

    cursor.execute(
        "SELECT SUM(amount) FROM expense WHERE user_id=? AND type='income'",
        (session["user_id"],)
    )
    income = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT SUM(amount) FROM expense WHERE user_id=? AND type='expense'",
        (session["user_id"],)
    )
    expense = cursor.fetchone()[0] or 0

    balance = income - expense

    conn.close()

    return render_template(
        "home.html",
        rows=rows,
        income=income,
        expense=expense,
        balance=balance
    )


# 添加
@app.route("/add", methods=["POST"])
def add():
    type = request.form["type"]
    category = request.form["category"]
    amount = request.form["amount"]

    conn = sqlite3.connect('expense.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expense (user_id, type, category, amount) VALUES (?, ?, ?, ?)",
        (session["user_id"], type, category, amount)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# 删除
@app.route("/delete/<int:rowid>")
def delete(rowid):
    conn = sqlite3.connect('expense.db')
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM expense WHERE rowid=?",
        (rowid,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# 退出
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)