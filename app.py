from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from pymongo import MongoClient
import certifi
from bson import ObjectId
from datetime import datetime, timezone
from dotenv import load_dotenv
from datetime import timedelta
import os

# load .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# app.config['SESSION_PERMANENT'] = False

# connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client[os.getenv("MONGO_DBNAME")]
posts = db.posts
comments = db.comments
#user collection
users = db.users
#job items
jobs = db.jobs

app.config["SESSION_PERMANENT"] = True
app.permanent_session_lifetime = timedelta(days=7)


try:
    client.admin.command("ping")
    print("Connected to MongoDB!")
except Exception as e:
    print("MongoDB connection error:", e)

def oid(s):
    try: return ObjectId(s)
    except: abort(404)

@app.route("/")
def home_redirect():
    return redirect(url_for("official_home"))


@app.route("/forum", methods=["GET", "POST"])
def forum_home():
    all_posts = list(db.posts.find().sort("created_at", -1))
    for p in all_posts:
        p["_id"] = str(p["_id"])
        if "created_at" in p:
            p["created_at"] = p["created_at"].astimezone(timezone.utc)

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
    for p in my_posts:
        p["_id"] = str(p["_id"])
    return render_template("my_posts.html", posts=my_posts, section="forum")


@app.route("/official")
def official_home():
    page = int(request.args.get("page", 1))
    per_page = 20
    skip = (page - 1) * per_page

    jobs_cursor = db.jobs.find().skip(skip).limit(per_page)
    jobs = list(jobs_cursor)
    total_jobs = db.jobs.count_documents({})
    has_next = total_jobs > page * per_page

    # Get user's saved jobs
    user_jobs = []
    if "user_id" in session:
        user = db.users.find_one({"_id": ObjectId(session["user_id"])})
        if user and "my_jobs" in user and user["my_jobs"]:
            my_jobs = list(db.jobs.find({"_id": {"$in": list(user["my_jobs"])}}))

    return render_template(
        "official_home.html",
        jobs=jobs,
        page=page,
        has_next=has_next,
        user_jobs=user_jobs,
        section="official"
    )

@app.route("/add_to_my_jobs/<job_id>", methods=["POST"])
def add_to_my_jobs(job_id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user_id = ObjectId(session["user_id"])
    db.users.update_one(
        {"_id": user_id},
        {"$addToSet": {"my_jobs": ObjectId(job_id)}}
    )

    flash("Job added to My Jobs.")
    return redirect(url_for("official_home"))

@app.route("/my_jobs")
def my_jobs():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user = db.users.find_one({"_id": ObjectId(session["user_id"])})
    my_jobs = []
    if user and "my_jobs" in user:
        my_jobs = list(db.jobs.find({"_id": {"$in": [ObjectId(j) for j in user["my_jobs"]]}}))

    return render_template("my_jobs.html", jobs=my_jobs, section="official")

@app.route("/job/<job_id>")
def view_job(job_id):
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        flash("Job not found.")
        return redirect(url_for("official_home"))

    return render_template("job.html", job=job, section="official")


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
        
        new_user = {"username": username, "password": password}
        result = users.insert_one(new_user)
        flash("Registration successful!")
        session["username"] = username
        session["user_id"] = str(result.inserted_id)
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
            session["user_id"] = str(user["_id"])
            flash(f"Welcome, {username}!")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))       
        

    return render_template("login.html")



##logout route
@app.route("/logout")
def logout():
    session.clear()
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


# @app.route("/official")
# def official_home():
#     return render_template("official_home.html", section="official")

@app.route("/post/publish", methods=["GET", "POST"])
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
    _id = oid(pid)
    doc = posts.find_one({"_id": _id}) or abort(404)
    comms = list(comments.find({"post_id": _id}).sort("created_at", -1))
    return render_template("post.html", doc=doc, comms=comms, section="forum", pid = _id)

@app.route("/post/<pid>/comment/add", methods=["GET", "POST"])
def add_comment(pid):
    _id = oid(pid)
    doc = posts.find_one({"_id": _id}) or abort(404)

    if request.method == "POST":
        if "username" not in session:
            flash("Please log in before commenting.")
            return redirect(url_for("login"))
        user = db.users.find_one({"username": session["username"]})
        cmsg = request.form.get("cmessage", "").strip()
        comments.insert_one({
            "post_id": _id,
            "user_id": user["_id"],
            "name": user["username"],
            "message": cmsg,
            "created_at": datetime.now(timezone.utc)
        })
        flash("Comment added!")
    return redirect(url_for("post_detail", pid=pid))



@app.route("/post/<pid>/edit", methods=["GET", "POST"])
def edit_post(pid):
    """Edit post page:
       - GET: display edit form for an existing post
       - POST: save edited content to database"""
    _id = oid(pid)
    doc = posts.find_one({"_id": _id}) or abort(404)
    if request.method == "POST":
        title = request.form.get("ftitle","").strip()
        msg  = request.form.get("fmessage","").strip()
        if not (title and msg):
            flash("Name / Title / Message cannot be empty")
            return redirect(url_for("edit_post", pid=pid))
        posts.update_one({"_id": _id},
                         {"$set":{"title":title,"message":msg,"updated_at":datetime.utcnow()}})
        flash("Post updated")
        return redirect(url_for("post_detail", pid=pid))
    return render_template("edit.html", doc=doc)




@app.route("/post/<pid>/delete", methods=["POST"])
def delete_post(pid):
    """Delete a post:
       - Triggered by 'Delete' button form submission"""
    _id = oid(pid)
    posts.delete_one({"_id": _id})
    comments.delete_many({"post_id": _id})
    flash("Post deleted")
    return redirect(url_for("my_posts"))



if __name__ == "__main__":
    app.run(debug=True)
