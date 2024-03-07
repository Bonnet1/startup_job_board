import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///meander.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show current job listings"""
    m = request.args.get("m")
    if m == "success":
        message = "Your application has been received!"
    else:
        message = None
    rows = db.execute(
        """
            SELECT jobs.id as id
            , jobs.title as job_title
            , companies.name as company_name
            , jobs.location
            , jobs.type
            , companies.logo_url
            FROM jobs
            LEFT JOIN companies ON jobs.company_id = companies.id
            WHERE status = 'open'
            ORDER BY jobs.created_at DESC;
            """
    )
    return render_template("index.html", jobs=rows, message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM people WHERE email = ?", request.form.get("email")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        email = request.form.get("email")
        full_name = request.form.get("name")

        # Ensure name and email was submitted
        if not email:
            return apology("must provide email", 400)
        if not full_name:
            return apology("must provide your name", 400)

        # Ensure username is unique
        username_check = db.execute(
            "SELECT email FROM people WHERE email = ?", email
        )
        if len(username_check) != 0:
            return apology("email already registered", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmed password matches original password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords must match", 400)

        # Hash password
        hash = generate_password_hash(request.form.get("password"))

        # Save user in database
        db.execute(
            "INSERT INTO people (name, email, hash) VALUES(?, ?, ?)", full_name, email, hash
        )

        # Query database for username
        rows2 = db.execute(
            "SELECT * FROM people WHERE email = ?", request.form.get("email")
        )

        # Ensure username exists and password is correct
        if len(rows2) != 1 or not check_password_hash(
            rows2[0]["hash"], request.form.get("password")
        ):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows2[0]["id"]

        # Redirect user to portfolio
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add new job posting"""
    user_id = session.get("user_id")
    # Check to make sure user has company details completed
    rows = db.execute(
        "SELECT id FROM companies WHERE admin_id = ?", user_id
    )
    if len(rows) == 0:

        return render_template("/account.html", message="Company info needed before posting!")

    company_id = rows[0]['id']

    if request.method == "POST":
        # Create a new job posting if job id was not passed
        # Check to make sure all required fields have been completed
        if not request.form.get("jobTitle"):
            return apology("must provide job title", 400)
        if not request.form.get("jobDescription"):
            return apology("must provide job description", 400)
        if not request.form.get("jobSalary"):
            return apology("must provide salary information", 400)
        if not request.form.get("jobLocation"):
            return apology("must provide location", 400)
        if not request.form.get("jobIndustry"):
            return apology("must provide industry", 400)
        if not request.form.get("jobType"):
            return apology("must provide valid type of work", 400)
        if not request.form.get("jobUrl"):
            return apology("must provide an application link", 400)

        # Create a new job
        try:
            db.execute(
                "INSERT INTO jobs (company_id, owner_id, title, description, salary, location, industry, type, ats_url, status) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", company_id, user_id, request.form.get(
                    "jobTitle"), request.form.get("jobDescription"), request.form.get("jobSalary"), request.form.get("jobLocation"), request.form.get("jobIndustry"), request.form.get("jobType"), request.form.get("jobUrl"), "open"
            )
        except:
            return apology("something went wrong", 400)

        return redirect("/account")


    else:
        return render_template("job.html", company_id=company_id, mode="add")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """ Update company details"""
    user_id = session.get("user_id")
    if request.method == "POST":
        # Ensure all fields were completed
        if not request.form.get("companyName"):
            return apology("must provide company name", 400)

        if not request.form.get("companyDetails"):
            return apology("must provide company details", 400)

        else:
            # Check to see if company already exists
            name = request.form.get("companyName")
            details = request.form.get("companyDetails")
            try:
                logo = request.form.get("companyLogo")
            except:
                logo = "TODO"

            rows = db.execute(
                "SELECT id FROM companies WHERE admin_id = ?", user_id
            )

            if len(rows) == 0:
                # Create new company
                db.execute(
                    "INSERT INTO companies (name, about, logo_url, admin_id) VALUES(?, ?, ?, ?)", name, details, logo, user_id
                )

            elif len(rows) == 1:
                # Update existing company
                db.execute(
                    """UPDATE companies
                    SET name = ?
                    , about = ?
                    , logo_url = ?

                    WHERE admin_id = ?""", name, details, logo, user_id
                )

            else:
                # User has more than one company
                return apology("it looks like you have too many companies", 400)

            return redirect("/account")

    else:
        # Preload company details if user has an assigned company
        try:

            rows = db.execute(
                "SELECT name, about, logo_url FROM companies WHERE admin_id = ?", user_id
            )
            if len(rows) == 0:
                name = ""
                details = ""
                logo = ""

            else:
                name = rows[0]["name"]
                details = rows[0]["about"]
                logo = rows[0]["logo_url"]

                # Show active jobs
                jobs = db.execute(
                    """
                SELECT jobs.id as id
                , jobs.title as job_title
                , jobs.status
                , COUNT(applicants.person_id) as applications
                FROM jobs
                LEFT JOIN applicants ON jobs.id = applicants.job_id
                WHERE jobs.owner_id = ? AND (jobs.status != 'deleted')
                GROUP BY jobs.id
                ORDER BY jobs.status DESC, jobs.created_at DESC;
                """, user_id
                )

            return render_template("account.html", name=name, details=details, logo=logo, jobs=jobs)
        except:
            return render_template("/account.html", message="Add company info below")


@app.route("/view_job", methods=["GET", "POST"])
@login_required
def view_job():
    q = request.args.get("q")
    if request.method == "POST":
        ## Editable view
        job_id = request.form.get("job_id")
        user_id = session.get("user_id")
        # Get existing job details
        job = db.execute("""
                            SELECT
                            *
                            FROM jobs
                            WHERE jobs.id = ? AND jobs.owner_id = ?
                            """, job_id, user_id)

        return render_template("job.html", job=job[0], mode="edit")

    else:
        ## Render the job view page
        if q:
            job = db.execute("""
                            SELECT
                            companies.name as company_name
                            , jobs.title
                            , jobs.description
                            , jobs.ats_url
                            , jobs.industry
                            , jobs.location
                            , jobs.type
                            , jobs.salary
                            , companies.about
                            , jobs.owner_id
                            , jobs.id
                            FROM jobs
                            JOIN companies on companies.id = jobs.company_id
                            WHERE jobs.id = ?
                            """, q)
        else:
            return apology("could not find job", 400)
        return render_template("job.html", job=job[0], user_id=session.get("user_id"))


@app.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("resume"):
            return apology("must provide link to online resume", 403)

        # Ensure password was submitted
        if not request.form.get("cover_letter"):
            return apology("must provide details on your fit for the role", 403)

        # Create new applicant
        user_id = session.get("user_id")
        job_id = request.args.get("q")
        db.execute(
            """
                    INSERT INTO applicants
                    (person_id, job_id, cover_letter_url, resume_url)
                    VALUES(?, ?, ?, ?)""", user_id, job_id, request.form.get("cover_letter"), request.form.get("resume")
        )
        return redirect("/?m=success")
    else:
        return apology("something went wrong", 400)


@app.route("/view_candidates")
@login_required
def view_candidates():
    q = request.args.get("q")
    user_id = session.get("user_id")
    jobs = db.execute("""
                         SELECT
                            title
                            , company_id
                            , id
                            , owner_id
                            FROM jobs
                            WHERE jobs.id = ? AND jobs.owner_id = ?
                         """, q, user_id)
    if q:
        applications = db.execute("""
                         SELECT
                        people.name
                        , people.email
                        , applicants.person_id
                                  , applicants.job_id
                        , applicants.cover_letter_url
                        , applicants.resume_url
                                  , applicants.status
                        , jobs.title
                        FROM applicants
                        JOIN people on applicants.person_id = people.id
                        JOIN jobs on applicants.job_id = jobs.id
                        WHERE jobs.id = ? AND jobs.owner_id = ?
                                  ORDER BY applicants.created_at;
                         """, q, user_id)

    else:
        return apology("something went wrong", 400)

    return render_template("candidates.html", applications=applications, jobs=jobs[0], user_id=session.get("user_id"))


@app.route("/toggle_candidate", methods=["GET", "POST"])
@login_required
def toggle_candidate():
    if request.method == "POST":

        # Gather information to update
        applicant = request.form.get("applicant_id")
        job = request.form.get("job_id")
        status = 'inactive'

        # Update table
        db.execute("""
                       UPDATE applicants
                        SET status = ?
                        WHERE person_id = ? AND job_id = ?;
                       """, status, applicant, job)

        return redirect("/view_candidates?q=" + job)

    else:
        return apology("something went wrong", 400)

@app.route("/delete_job", methods=["POST"])
@login_required
def delete_job():
    user_id = session.get("user_id")
    job_id = request.form.get("job_to_delete")

    # Check to make sure user is job owner
    rows = db.execute(
        "SELECT * FROM jobs WHERE id = ? AND owner_id = ?", job_id, user_id
    )

    if len(rows) != 1:
        return apology("you don't have permission to delete this job", 400)
    else:
        # Update job
        db.execute("""
                       UPDATE jobs
                        SET status = 'deleted'
                        WHERE owner_id = ? AND id = ?;
                       """, user_id, job_id)

        return redirect("/account")

@app.route("/edit_job", methods=["POST"])
@login_required
def edit_job():
    # Create a new job posting if job id was not passed
    # Check to make sure all required fields have been completed
    if not request.form.get("jobTitle"):
        return apology("must provide job title", 400)
    if not request.form.get("jobDescription"):
        return apology("must provide job description", 400)
    if not request.form.get("jobSalary"):
        return apology("must provide salary information", 400)
    if not request.form.get("jobLocation"):
        return apology("must provide location", 400)
    if not request.form.get("jobIndustry"):
        return apology("must provide industry", 400)
    if not request.form.get("jobType"):
        return apology("must provide valid type of work", 400)
    if not request.form.get("jobUrl"):
        return apology("must provide an application link", 400)
    if not request.form.get("status"):
        return apology("must set status to open or closed", 400)

    # Create a new job
    try:
        db.execute(
            """UPDATE jobs
                SET title = ?, description = ?, salary = ?, location = ?, industry = ?, type = ?, ats_url = ?, status = ?
                WHERE jobs.id = ?"""
                , request.form.get("jobTitle")
                , request.form.get("jobDescription")
                , request.form.get("jobSalary")
                , request.form.get("jobLocation")
                , request.form.get("jobIndustry")
                , request.form.get("jobType")
                , request.form.get("jobUrl")
                , request.form.get("status")
                , request.form.get("job_id")
        )
    except:
        return apology("something went wrong", 400)

    return redirect("/account")
