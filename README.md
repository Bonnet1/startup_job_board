# Startup Job Board
#### Video Demo:  https://youtu.be/ZT7YUX6a-iA
#### Description:

This project helps non-technical job seekers find great roles at tech companies.

When job seekers start looking for new opportunities, they need to search through thousands of online job postings in order to find something that could be a good fit. They would normally use a combination of LinkedIn, Indeed, and Google to build a shortlist, but because clear data on the job is rarely shared, these platforms no longer work as they were designed for a hiring environment when there were few jobs and many job seekers. This mismatch has created to mistrust between employees and employers, which led to high attrition and low engagement events such as the Great Resignation.

This job board helps proactive job seekers find the perfect fit by helping them connect directly with hiring managers rather than jump through the endless hurdles of traditional recruiting processes.

This is the prototype version of the product, which allows hiring managers and recruiters to:
* Setup a company profile
* Add jobs to a curated job board
* Review candidate applications from registered users directly on the platform
* Edit and delete jobs when they are no longer active

Candidates are required to register in order to view and apply to jobs, which aims to maintain a high quality bar with a focused talent community.

Technologies used in developing this job board include:

**Front End**:
* HTML/CSS
* JavaScript / AJAX
* Jinja

**Back End**:
* Python / Flask
* Sqlite3

**Functions and Routes**:

* /: Main index page shows a list of current open roles in reverse chronological order. There is a search feature that allows the user to search for jobs based on location, type, job title.

* /login: Clears current session and checks to make sure the login details match a registered account. Note that passwords are hashed and cannot be accessed using plain text.

* /logout: Clears the current session and logs out the current user.

* /register: Creates a new user in the database after checking to ensure the email address has not been registered. The username is also the email address of the user, and the password is hashed using the werkzeug.security package.

* /add: Allows a registred user to add a new job posting. If company details have not been completed then this will redirect to the company page for the user to update before a job posting is allowed.

* /account: Administrative page for hiring managers and recruiters to manage their company details and job postings. They can view number of applicants and click through to review the applicants to an open role. They can also click through to edit the job posting, including changing the status of the role between open, planned, and closed.

* /view_job: Renders the job posting that has been clicked on in either view mode for job seekers or edit mode for the user that owns the job posting.

* /apply: Users can apply to a job posting using a popup(modal) that takes in a link to their online resume and link to a cover letter.

* /view_candidates: Generates a list of all active candidates for a current job posting and allows users to see the name and email address of the applications. Users can remove candidates from a job posting to reject.

* /toggle_candidate: Function to set a candidate from active to inactive in order to reject them from a job application process.

* /delete_job: Changes the status of a job from active/planned to deleted. Note that the jobs will remain in the database so they can be recovered and/or analyzed in the future.

* /edit_job: Uses the same logic as add but prepopulates the fields with current data for a job in order to make editing as simple as possible.

**Database**:

The meander.db database includes 4 main tables and 1 additionalt able for future use:

* People: Stores the name and email address of every registered user with unique id and creation date.

* Companies: Stores the name, about details, and logo url for each company along with an admin_id linked to a registred user.

* Jobs: Stores relevant details for a job along with a company_id linked to the posting company and owner_id linked to the user that created the job listing.

* Applicants: Stores every application for a role with person_id linked to a user and job_id linked to a job along with the url for cover letter and resume and a timestamp.

* Employees (future use): Links every person to a company to unlock future logic for internal job postings and multi-user access to candidate applications.
