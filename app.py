from flask import Flask, render_template, request, redirect, url_for, flash, abort
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

try:
    client.admin.command("ping")
    print("Connected to MongoDB!")
except Exception as e:
    print("MongoDB connection error:", e)

def oid(s):
    try: return ObjectId(s)
    except: abort(404)

@app.route("/", methods=["GET", "POST"])
@app.route("/forum")
def forum_home():
    """Main page:
       - GET: display all posts
       - POST: handle new post submission"""
    posts = list(db.posts.find().sort("created_at", -1))
    return render_template("forum_home.html", posts=posts, section="forum")

@app.route("/profile")
def profile():
    return render_template("profile.html", section="forum")

@app.route("/official")
def official_home():
    return render_template("official_home.html", section="official")

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
