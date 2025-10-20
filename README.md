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

## Installation and Setup Guide

### 1. Clone Repository
```bash
git clone https://github.com/swe-students-fall2025/2-web-app-404found.git
cd 2-web-app-404found
```

### 2. Environment Setup
```bash
cp env.example .env
```
**Important:** Edit `.env` file with your actual values:
- `MONGO_URI`: Your MongoDB connection string
- `NAME`: Your database name

### 3. Dependencies Installation
For Linux/macOS:
```bash
python -m pip install --user pipenv
pipenv install
pipenv shell
```

For Windows:
```bash
py -m pip install --user pipenv
pipenv install
pipenv shell
```

### 4. Run Application
```bash
flask run
```

### Usage Notes
- Open the link displayed in the terminal to access the website
- To stop the application:
  1. Press `Ctrl + C` to stop the server
  2. Type `exit` to leave the virtual environment
  3. Disconnect from VPN if you were using it

## Task Boards

We use GitHub Projects to track progress during each sprint:

- [404Found - Sprint 1](https://github.com/orgs/swe-students-fall2025/projects/42)
- [404Found - Sprint 2](https://github.com/orgs/swe-students-fall2025/projects/53)
