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

### Creating mock data (OPTIONAL):
* flask --app flaskr create-mock-data
* OR
* fill-mock-data-db.sh on git-bash

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

## Delivery on 04.05.2025
This delivery contains everything on the previous deliveries, so it'a s completed web application.
Please, read carefully the setup part and specially pay attention to the copying of the config.py.
The functionality contains:

### User registration, authentication and password reset
* User can access most of the site without need to authenticate or create an account. This means browsing skills
listed by other users. Searching skills can also be done.
* Specific functions like Profile, Creating a skill listing, Creating an order or giving a review require account.
* User can create account from Login page or buy accessing the functionality that requires an account. User will be
redirected to the page requiring the account e.g. creating a new skill listing.
* Creating account requires username which is email and a password that has some specific requirements.
* After having created an account user can login to the site by using this account.
* Authenticated user has access to some specific functionality mentioned above.
* In case user forgets the password they can request password reset. Due to project
constraints (no additional libraries) password reset is now written to server console but
the functionality has been tested with a local SMTP server.

### Skill management
* User can browse skills created by other users by accessing all skills.
* User can access the front page which randomises skills for greater discoverability
* User can create a skill listing if they have an account
* By creating a skill listing user can give information about the skill they want so share
like title, description and category. Additionally skill can have a price or it can also be free.
User can also upload a picture that is presented as part of the listing.
* By completing the listing it becomes available for viewing for other users.
* User can update their skill listing by accessing it from Profile or by searching it.
* User can delete a skill listing if it doesn't have any orders.

### Orders
* When a user has found an interesting skill listing they can make an order.
* Order can be placed by accessing the skill listing. On the order page user can give some additional information
for the seller. 
* The order can be accessed from the Profile. User can access both orders they have made as a customer and orders
other users have done for skills they have listed.
* Orders that are fulfilled can be completed if they are not yet completed. Fulfilment of the order is out of the
scope of the application but generally communication would be handled via email.

### Reviews
* User who has completed orders can give a review.
* Review is done from a completed order by giving a rating and additional commentary.
* Seller of the skill can see their reviews from the user profile.

### User profile and statistics
* Users who are logged in can access their profile page
* Profile page has links to: Your own skill listings, To orders you have made, To orders everyone has made to you,
Reviews others have given to completed orders.
* There's also a statistics section providing information about how active
user had been on the site. 
* The statistics include: Number of open orders (as customer), Number of completed orders (as customer), Open orders
(as seller), Completed orders (as seller), Total reviews (as seller) and average score of the reviews.

### Technical information
* The application has been tested with 1M (million = 10 ** 6) rows as orders and reviews.
* Amount of skills has been tested with 100K (one hundred thousand = 10 ** 5) rows
* Amount of users has been tested with 1K (one thousand) rows
* The application remains responsive and queries execute without noticeable delay (< 200ms)
* The application has not been tested with different amounts of simultaneous clients.
* The database can be initialised with mock data. Read instructions above from delivery of 13.04.2025.
* Performance statistics (with mock data described above):
#### Without indices:
* Access random skill listing: 1000 - 2000ms
* Access profile: approx 2000 ms
* Access reviews: 1000 - 2000 ms
* Access random page of own orders: 300 - 500 ms
#### With indices:
* Access random skill listing: approx 50ms
* Access profile: approx 300 - 400 ms
* Access reviews: approx 200 - 300 ms
* Access random page of own orders: 130 - 160 ms