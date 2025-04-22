# Skill & Gig Exchange Platform

## Overview

The Skill & Gig Exchange platform is a web application that allows users to share and discover skills, gigs and hobbies. Users can create accounts, add skills they want to teach or learn, categorize them, and connect with others who share their interests.

## Features

### User Management

* Users can create an account and log in to the application.
* Each user has a profile page that displays statistics and their contributed skills.

### Skill Listings

* Users can add new skill listings (e.g., "Guitar Lessons," "Coding Help").
* Users can edit and delete their own skill listings. Deleting is only allowed if there's no orders for that skill.
* Each skill listing can be categorized (e.g., "Music," "Technology," "Sports").
* Users can search for skills based on keywords.

### Community Interaction

* Users can view all skill listings, including their own and those added by others.
* Users can make an order for someone else's listing.

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

As a user, I want to search for skills using keywords so that I can find relevant listings faster.

### 6. Adding Complementary Information

As a user, I want to be able to an order for someone's skill listing.

### 7. Completing An Order

As a user, when I have an order, I want to be able to complete it. Interaction between seller and user 
(the one making the order) is out of the scope.

### 8. Reviewing An Completed Order

As a user, when seller has completed the order, I want to be able to review it. I want give some comments
and a rating for the completed order.

## Technology Stack

* Backend: Python (Flask)
* Database: SQLite
* Version Control: Git, GitHub
* Frontend: HTML (No JavaScript per project constraints)
* Deployment: Local development with Flask

## Setup Instructions

### Clone the repository:

* git clone https://github.com/jhuhtanen/tikawe-skillr.git
* Go to newly created folder: cd tikawe-skillr

### Create virtual environment:
* Create and activate a virtual environment by running: python -m venv venv
* Activate the virtual environment: source venv/bin/activate .On Windows use `venv\Scripts\activate`

### Install dependencies:
* pip install flask

### Initialize the database by running:
* flask --app flaskr init-db
* OR
* init-db.sh on git-bash 

### Make sure application has valid config
* Copy the config.py -file from flaskr folder to instance folder.

NOTE: In order for the app to work the config.py from project root needs to be copied to instance folder.
This is due to the fact that instance folder shouldn't be in source control and config in production use is
instance data. But for this scope of project we can use the one config that is in source control and under the root.

In case you see errors like current_app.config["KEY_NAME"] with KeyError it's very likely that config.py was not copied
under instance folder.

### Run the application:

* python app.py 
* OR
* run.sh on git-bash
* Open http://127.0.0.1:5000/ in a web browser.

### Testing password reset:

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

## Delivery on 30.03.2025
* Current functionality:

User can register and loging to the site. They can request forgotten password link and reset password using it.
User can create a skill listing, edit it and delete it.
User can search skills by using text search from title or description.

## Delivery on 13.04.2025
* Current functionality:

User can make an order for a skill someone else has listed. The owner of the order is the owner of the skill.
User can complete an order someone else made for their skill. (Out of scope how the communication is handled or managed, but idea is that there's email for every user)
User can access a profile page that has the following functionality:
* List users skill listing (see their own skills)
* List orders user have made for someone else
* List orders everyone else has made for one of the skills user have listed
* Show reviews made for completed orders by user
* Show statistics
* Most of the pages support pagination with a specific template that can be added to a page

Additionally: There's a script that can be used to populate the database with a lot of data that allows
testing the pagination and how site behaves with a lot of data in DB. This script is called "fill-mock-data-db.sh". 
It can be also run with "flask --app flaskr create-mock-data" if you don't have bash execution environment. 