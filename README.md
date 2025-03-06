# LCC Issue Tracker Project Setup & Usage Guide

A web-based issue tracking system for Lincoln Commutity Campground (LCC), built with Flask、MySQL and Responsive design using Bootstrap 5.

---
# How to Set Up LCC Issue Tracker Project
## Prerequisites

- Python 3.12+
- MySQL 8.0+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LCC-Issue-Tracker.git
cd LCC-Issue-Tracker/loginapp
```

2. Create and activate a virtual environment:
```bash
bash
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the MySQL database:
```bash
mysql -u root -p < create_database.sql # Create the Database Schema 
mysql -u root -p < seed.sql # Populate the Database
```

5. Run the application:
```bash
python3 run.py
```

---
# How to use LCC Issue Tracker Website

## Login
Use the login page to log in, there are given data(Username and Password) in password_hash_generator.py to login, such as:
```sql
Format: UserAccount(username, password, role)
    
# Administrators (2)
UserAccount('admin1', 'Admin1Pass!', 'admin'),
UserAccount('admin2', 'Admin2Pass!', 'admin')

# Helpers (5)
UserAccount('helper1', 'Helper1Pass!', 'helper'),
UserAccount('helper2', 'Helper2Pass!', 'helper'),
UserAccount('helper3', 'Helper3Pass!', 'helper'),
UserAccount('helper4', 'Helper4Pass!', 'helper'),
UserAccount('helper5', 'Helper5Pass!', 'helper'),

 # Visitors (20)
UserAccount('visitor1', 'Visitor1Pass!', 'visitor'),
UserAccount('visitor2', 'Visitor2Pass!', 'visitor'),
UserAccount('visitor3', 'Visitor3Pass!', 'visitor'),
UserAccount('visitor4', 'Visitor4Pass!', 'visitor'),
UserAccount('visitor5', 'Visitor5Pass!', 'visitor'),
UserAccount('visitor6', 'Visitor6Pass!', 'visitor'),
UserAccount('visitor7', 'Visitor7Pass!', 'visitor'),
UserAccount('visitor8', 'Visitor8Pass!', 'visitor'),
UserAccount('visitor9', 'Visitor9Pass!', 'visitor'),
UserAccount('visitor10', 'Visitor10Pass!', 'visitor'),
UserAccount('visitor11', 'Visitor11Pass!', 'visitor'),
UserAccount('visitor12', 'Visitor12Pass!', 'visitor'),
UserAccount('visitor13', 'Visitor13Pass!', 'visitor'),
UserAccount('visitor14', 'Visitor14Pass!', 'visitor'),
UserAccount('visitor15', 'Visitor15Pass!', 'visitor'),
UserAccount('visitor16', 'Visitor16Pass!', 'visitor'),
UserAccount('visitor17', 'Visitor17Pass!', 'visitor'),
UserAccount('visitor18', 'Visitor18Pass!', 'visitor'),
UserAccount('visitor19', 'Visitor19Pass!', 'visitor'),
UserAccount('visitor20', 'Visitor20Pass!', 'visitor'),
```

## Sign up
Click the Sign up button on the Login page to create your own account, your account will be a visitor for this issue tracker system.

## Navigation Bar - Home button

click the Home button to show the user Dashboard 

**Admin user dashboard**
1 - "View Active Issues" button
Click it to view the list of those issues that aren't resolved yet.
2 - "View Resolved Issues" button
Click it to view the list of those issues that have been resolved.
3 - "Manage Users" button
Click it to view the list of those issues that have been resolved. and then you can search users by username/fname/lname, can change the role(admin/helper/visitor) and the status(inactive and active) of the usrs, can view the users profile.
4 - "Report New Issue"
Click it to create a new issue.

**2. Helper user dashboard**
1 - "View Active Issues" button
Click it to view the list of those issues that aren't resolved yet.
2 - "View Resolved Issues" button
Click it to view the list of those issues that have been resolved.
3 - "Report New Issue"
Click it to create a new issue.

**3. Visitor user dashboard**



## Navigation Bar - Issues button

**1.Admin user**

**2.Helper user**
**3.visitor user**

## Navigation Bar - Manage Users button

**Only Visible to Admin User:**
Click it to view the list of those issues that have been resolved. and then you can search users by username/fname/lname, can change the role(admin/helper/visitor) and the status(inactive and active) of the usrs, can view the users profile.

## Navigation Bar - User Avatar and First Name

**Used for ALL Roles (Admin/Helper/Visitor):**
Click this button to show yours Profile details, and you can change your details and password in the "My profile" page.

## Navigation Bar - Log out

**Used for ALL Roles (Admin/Helper/Visitor):**
Click this button to log out your account from the LCC Issue Tracker system.