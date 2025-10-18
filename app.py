from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from pymongo import MongoClient
import certifi
from bson import ObjectId
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# load .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client[os.getenv("MONGO_DBNAME")]
posts = db.posts
comments = db.comments
#user collection
users = db.users

try:
    client.admin.command("ping")
    print("Connected to MongoDB!")
except Exception as e:
    print("MongoDB connection error:", e)

def oid(s):
    try: return ObjectId(s)
    except: abort(404)

@app.route("/", methods=["GET", "POST"])
def forum_home():
    all_posts = list(db.posts.find().sort("created_at", -1))
    return render_template("forum_home.html", posts=all_posts, section="forum")


@app.route("/my_posts")
def my_posts():
    if "username" not in session:
        flash("Please log in to view your posts.")
        return redirect(url_for("login"))
    
    username = session["username"]
    user = db.users.find_one({"username": username})
    if not user:
        flash("User not found.")
        return redirect(url_for("login"))
    
    my_posts = list(db.posts.find({"user_id": user["_id"]}).sort("created_at", -1))
    return render_template("my_posts.html", posts=my_posts, section="forum")
#User
##register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("Please fill in both username and password.")
            return redirect(url_for("register"))
        existing_user = users.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose another.")
            return redirect(url_for("register"))
        users.insert_one({"username": username, "password": password})
        flash("Registration successful!")
        session["username"] = username

        return redirect(url_for("profile"))

    return render_template("register.html")
##login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user = users.find_one({"username": username})
        if user and user["password"] == password:
            session["username"] = username
            flash(f"Welcome, {username}!")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))       
        

    return render_template("login.html")
##logout route
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have logged out.")
    return redirect(url_for("login"))
##delete account route
@app.route("/delete_account", methods=["POST"])
def delete_account():
    "should not happen logically"
    if "username" not in session:
        flash("You must be logged in to delete your account.")
        return redirect(url_for("login"))

    username = session["username"]
    result = users.delete_one({"username": username})
    flash("Account deleted successfully.")
    session.pop("username", None)
    return redirect(url_for("login"))

#profile route

@app.route("/profile")
def profile():
    "change to login if not logged in"
    if "username" not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for("login"))
    username = session["username"]
    return render_template("profile.html", section="profile", username=username)


@app.route("/official")
def official_home():
    return render_template("official_home.html", section="official")

@app.route("/forum/publish", methods=["GET", "POST"])
def publish_post():
    """Main page:
       - GET: display all posts
       - POST: handle new post submission"""
    if request.method == "POST":
        if "username" not in session:
            flash("Please log in before posting.")
            return redirect(url_for("login"))
        name = session["username"]
        title = request.form.get("ftitle").strip()
        message = request.form.get("fmessage").strip()

        if not title or not message:
            flash("Please fill in both title and message.")
            return redirect(url_for("forum_home"))
        
        # find current user id
        user = db.users.find_one({"username": name})
        if not user:
            flash("User not found.")
            return redirect(url_for("login"))

        # insert post
        new_post = {
            "title": title,
            "message": message,
            "name": name,
            "user_id": user["_id"],
            "created_at": datetime.now(timezone.utc)
        }
        db.posts.insert_one(new_post)
        flash("Post published successfully!")
        return redirect(url_for("forum_home"))

@app.route("/post/<pid>", methods=["GET", "POST"])
def post_detail(pid):
    """Post detail page:
       - GET: display one post and its comments
       - POST: handle new comment submission"""
    pass


@app.route("/post/<pid>/edit", methods=["GET", "POST"])
def edit_post(pid):
    """Edit post page:
       - GET: display edit form for an existing post
       - POST: save edited content to database"""
    pass


@app.route("/post/<pid>/delete", methods=["POST"])
def delete_post(pid):
    """Delete a post:
       - Triggered by 'Delete' button form submission"""
    pass


if __name__ == "__main__":
    app.run(debug=True)
