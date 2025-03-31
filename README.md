# Skill & Gig Exchange Platform

## Overview

The Skill & Gig Exchange platform is a web application that allows users to share and discover skills, gigs and hobbies. Users can create accounts, add skills they want to teach or learn, categorize them, and connect with others who share their interests.

## Features

### User Management

* Users can create an account and log in to the application.
* Each user has a profile page that displays statistics and their contributed skills.

### Skill Listings

* Users can add new skill listings (e.g., "Guitar Lessons," "Coding Help").
* Users can edit and delete their own skill listings.
* Each skill listing can be categorized (e.g., "Music," "Technology," "Sports").
* Users can search for skills based on keywords or categories.

### Community Interaction

* Users can view all skill listings, including their own and those added by others.
* Users can add complementary information (secondary data) to other skill listings (e.g., additional resources, related skills, or personal experiences).
* Users can filter skills based on categories stored in the database.

## Use Cases

### 1. User Registration & Login

As a user, I want to create an account and log in so that I can access and manage my skills.

### 2. Adding a Skill

As a user, I want to add a new skill to the platform so that others can see what I am offering or looking for.

### 3. Editing or Deleting a Skill

As a user, I want to modify or remove a skill I added in case I make a mistake or no longer want to offer it.

### 4. Viewing Available Skills

As a user, I want to browse the available skills so that I can find people to learn from or teach.

### 5. Searching for Skills

As a user, I want to search for skills using keywords or categories so that I can find relevant listings faster.

### 6. Viewing User Profiles

As a user, I want to view other users' profiles to see what skills they have contributed and their engagement in the platform.

### 7. Adding Complementary Information

As a user, I want to add additional information to other users’ skill listings to provide extra insights or related knowledge.

## Technology Stack

* Backend: Python (Flask)
* Database: SQLite
* Version Control: Git, GitHub
* Frontend: HTML (No JavaScript per project constraints)
* Deployment: Local development with Flask

## Setup Instructions

* Clone the repository:

git clone https://github.com/jhuhtanen/tikawe-skillr.git
cd tikawe-skillr 

* Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

* Install dependencies:

pip install flask

* Run the application:

python app.py 

OR

run.sh on git-bash

* Initialize the database by running:

flask --app flaskr init-db

OR

init-db.sh on git-bash 

* Open http://127.0.0.1:5000/ in a web browser.

* Testing password reset:
You can test the password reset in two ways. By using a mock service which just prints
the email and link to the console from which it can be copied and pasted to browser URL. Or
by having a local SMTP server which actually handles the SMTP call. The configuration is currently 
in the config file under key EMAIL_INTERFACE.
* Mock service. This is set by default and will just print it on the server console.
* Local SMTP server: This requires SMTP server. You can install e.g. aiosmtpd with
pip install aiosmtpd

Note: This is NOT part of the default implementation because no additional
python packages are not allowed to be installed. The site WILL function without
this dependency.


===

## Delivery on 30.04.2025
* Current functionality:

User can register and loging to the site. They can request forgotten password link and reset password using it.
User can create a skill listing, edit it and delete it.
User can search skills by using text search from title or description.

NOTE: In order for the app to work the config.py from project root needs to be copied to instance folder.
I couldn't figure out why it needs to be copied there yet but application uses config keys and instance folder is
by default on gitignore because it's instance level data.
