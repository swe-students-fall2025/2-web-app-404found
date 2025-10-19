# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Our vision is to build an interactive and inclusive Job Forum web application where students and professionals can discover job opportunities, share experiences, and connect through posts and comments.

## User stories

### As a visitor:
- I want to browse available job listings so that I can learn about open opportunities.
- I want to register or sign in easily so that I can set up my own account.

### As a user:
- I want to search job posts by keyword, location, or company so that I can quickly find relevant openings.
- I want to comment under posts so that I can discuss or ask questions.
- I want to delete my own comments so that I can manage my interactions responsibly.
- I want to create new posts so that I can share insights or opportunities with others.
- I want to be able to  edit my posts so that I can upadte new info
- I want to able to delete my posts so that I can remove mistaken contents
- I want to save or bookmark posts that I find useful so that I can easily revisit them later
- I want to reply to comments under my post so that I can engage in direct conversations and clarify information.
- I want to upvote/like posts and comments so that helpful content surfaces.
- I want to edit my profile so that others understand my background.
### As an admin:
- I want to review and remove inappropriate content so that the community stays professional and safe.
- I want to suspend or reinstate user accounts so that the community stays safe.

## Steps necessary to run the software

## 1) Clone
git clone https://github.com/swe-students-fall2025/2-web-app-404found.git <br> 
cd 2-web-app-404found

## 2) Env
cp env.example .env <br>

**Tip:** Edit .env with real values: MONGO_URI / NAME

## 3) Deps
python -m pip install --user pipenv **Windows:** py -m pip install --user pipenv <br>
pipenv install <br>
pipenv shell

## 4) Run
flask run

### Notice
- Click the link shown in terminal to open the site
- When finished: Ctrl + C to stop, exit to leave the shell, and exit VPN if needed


## Task boards

We use GitHub Projects to track progress during each sprint:

- [404Found - Sprint 1](https://github.com/orgs/swe-students-fall2025/projects/42)
- [404Found - Sprint 2](https://github.com/orgs/swe-students-fall2025/projects/53)
