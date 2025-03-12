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

* Open http://127.0.0.1:5000/ in a web browser.
