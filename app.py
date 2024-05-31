from flask import Flask, render_template


app = Flask("Personal_Website")

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")