import bcrypt
from flask import Flask, render_template, request, session as flask_session, flash, redirect, url_for
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, select, Session


app = Flask("app")
app.secret_key = "secret_key"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field()
    password: str = Field()
    email: str = Field()

engine = create_engine('sqlite:///./database.db', echo=True)
SQLModel.metadata.create_all(engine)

class RegisterModel(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: str

class LoginModel(BaseModel):
    username: str
    password: str    

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        try:
            login_model = LoginModel(
                username=request.form["Username"],
                password=request.form["Password"]
            )
        except:
            flash("Type error", "warning")
            return redirect(url_for("login")) 

        with Session(engine) as db_session:
            statement = select(User).where(User.username == login_model.username)  
            user = db_session.exec(statement).first()
        if user:
            password_byte = login_model.password.encode("utf-8")
            if bcrypt.checkpw(password_byte, user.password):
                flash("Welcome, you are logged in", "success")
                flask_session["user_id"] = user.id 
                return redirect(url_for("contact"))  
            else:
                flash("Password is incorrect", "danger")
                return redirect(url_for("login"))
        else:
            flash("Username is incorrect", "danger")
            return redirect(url_for("login"))    
              
    else:    
        return render_template("login.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/contact")
def contact():
    if flask_session.get('user_id'):
        return render_template("contact.html")
    else:
        flash("You must login first")
        return redirect(url_for("index"))


@app.route("/register",methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            register_data = RegisterModel(
            username=request.form["Username"],
            password=request.form["Password"],
            confirm_password=request.form["Confirm_Password"],
            email=request.form["Email"]
            )
        except:    
            flash("Type Error")   
            return redirect(url_for("register"))    
        
        with Session(engine) as db_session:
            statement = select(User).where(User.username== register_data.username)
            result = db_session.exec(statement).first()
        
        if not result:
            if register_data.password == register_data.confirm_password:
                with Session(engine) as db_session:
                    user = User(
                        username=register_data.username,
                        password=bcrypt.hashpw(register_data.password.encode('utf-8'),bcrypt.gensalt()),
                        email=register_data.email
                    )
                    db_session.add(user)
                    db_session.commit()
                flash("Registered done successfuly")  
                return redirect(url_for("login"))   
            else:
                flash("Different passwords!")
                return redirect(url_for("register"))      

        else:
            flash("Usrename already exist, try another username")  
            return redirect(url_for("register"))

    else:
        return render_template("register.html")    


@app.route("/logout")
def logout():
    if flask_session.get('user_id'):
        flask_session.pop("user_id")
        return redirect(url_for("index"))
    else:
        return render_template("index.html")