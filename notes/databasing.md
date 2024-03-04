
# Getting started - flask + heroku postgres
Integrating a Heroku PostgreSQL database with a Flask application involves several steps. Here's a guide to get you started:

### Step 1: Add Heroku Postgres to Your App

If you haven't already added a PostgreSQL database to your Heroku app, you can do so by running:

```sh
heroku addons:create heroku-postgresql:hobby-dev --app your-app-name
```
This command adds a free `hobby-dev` instance of Heroku Postgres to your application.

### Step 2: Install Flask-SQLAlchemy

Flask-SQLAlchemy is an extension for Flask that simplifies using SQLAlchemy with Flask applications. SQLAlchemy is an ORM (Object-Relational Mapper) that allows you to interact with your database in a Pythonic way.

Add `Flask-SQLAlchemy` to your `requirements.txt` file:

```
Flask-SQLAlchemy
psycopg2-binary
```

Then, install the dependencies locally (if you haven't already):

```sh
pip install -r requirements.txt
```

### Step 3: Configure Your Flask App for PostgreSQL

Heroku sets an environment variable `DATABASE_URL` for your app's database connection string. In your Flask app, you can use this environment variable to configure the SQLALCHEMY_DATABASE_URI for Flask-SQLAlchemy.

Modify your app's main file (e.g., `app.py`) to include the following:

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)  # Fix for postgres:// scheme
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define a model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# Create the tables
with app.app_context():
    db.create_all()
```

Note the `.replace("://", "ql://", 1)` part in the `DATABASE_URL` setting. This is a workaround for a dialect name change in SQLAlchemy 1.4 for PostgreSQL URLs from `postgres://` to `postgresql://`. Heroku's environment variable might use the old dialect name, so this ensures compatibility.

### Step 4: Use Models in Your Application

Now that you have a model defined (`User` in the example above), you can start using it in your route handlers to create, read, update, and delete data in your database. For example, to create a new user:

```python
@app.route('/add_user/<username>')
def add_user(username):
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return f"User {username} added."
```

### Step 5: Deploy Your Changes

Commit your changes to Git and deploy to Heroku:

```sh
git add .
git commit -m "Add PostgreSQL database integration"
git push heroku main
```

### Step 6: Test Your Application

Make sure to test your application thoroughly to ensure that database operations are working as expected.

By following these steps, you integrate your Flask application with a Heroku PostgreSQL database, allowing you to perform database operations through your Flask app.