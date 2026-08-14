from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import mysql.connector
import os
from werkzeug.utils import secure_filename
import uuid
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv #add

app = Flask(__name__)
load_dotenv() #add

# ==========================================
# Secret Key
# ==========================================

app.secret_key = "civicconnect_secret_key"

# ==========================================
# Email Config (Gmail SMTP)
# ==========================================
# IMPORTANT: Use a Gmail "App Password", NOT your normal
# Gmail login password. Steps to generate one:
# 1. Go to myaccount.google.com/security
# 2. Turn on 2-Step Verification (if not already on)
# 3. Search "App Passwords" -> create one for "Mail"
# 4. Paste that 16-character password below

EMAIL_ADDRESS = "EMAIL_ADDRESS"
EMAIL_APP_PASSWORD = "EMAIL_APP_PASSWORD"


def send_email(to_email, subject, body):
    """Send a simple text email. Fails silently (prints error)
    so a broken email config never crashes the app."""

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print(f"❌ Email failed to send: {e}")

# ==========================================
# File Upload Config
# ==========================================

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ==========================================
# MySQL Connection
# ==========================================

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

# Ensures the app always sees the latest committed data
# (fixes stale/old data showing even after updates made
# from MySQL Workbench or another connection)
db.autocommit = True

# IMPORTANT
cursor = db.cursor(dictionary=True, buffered=True)

print("✅ MySQL Connected Successfully!")

# ==========================================
# Home
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# About
# ==========================================

@app.route("/about")
def about():
    return render_template("about.html")


# ==========================================
# Services
# ==========================================

@app.route("/services")
def services():
    return render_template("services.html")


# ==========================================
# Wards
# ==========================================

@app.route("/wards")
def wards():
    cursor.execute("SELECT ward_id, ward_number, ward_name, area_name FROM wards ORDER BY ward_number")
    wards_list = cursor.fetchall()
    return render_template("wards.html", wards=wards_list)


# ==========================================
# Representatives
# ==========================================

@app.route("/representatives")
def representatives():

    # Fetch all wards
    cursor.execute("SELECT ward_id, ward_number, ward_name, area_name FROM wards ORDER BY ward_number")
    wards_list = cursor.fetchall()

    # For each ward, fetch its representatives and attach them
    for w in wards_list:
        cursor.execute(
            "SELECT rep_id, full_name, area, mobile, email FROM representatives WHERE ward_id=%s ORDER BY rep_id",
            (w["ward_id"],)
        )
        w["reps"] = cursor.fetchall()

    return render_template("representatives.html", wards=wards_list)

# ==========================================
# Register
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        area = request.form["area"]
        ward_no = request.form["ward_no"]
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password", "")

        # ---------------------------------------------
        # 1. Passwords must match
        # ---------------------------------------------

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match. Please try again."
            )

        # ---------------------------------------------
        # 2. Email must not already be registered
        # ---------------------------------------------

        cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template(
                "register.html",
                error="This email is already registered. Please login instead."
            )

        # ---------------------------------------------
        # 3. Ward number must be a valid, existing ward
        # ---------------------------------------------

        cursor.execute("SELECT ward_id FROM wards WHERE ward_number=%s", (ward_no,))
        valid_ward = cursor.fetchone()

        if not valid_ward:
            return render_template(
                "register.html",
                error="Invalid Ward Number. Please enter a valid ward (e.g. 11 or 12)."
            )

        sql = """
        INSERT INTO users
        (
            full_name,
            email,
            mobile,
            area,
            ward_no,
            password
        )
        VALUES
        (%s,%s,%s,%s,%s,%s)
        """

        values = (
            full_name,
            email,
            mobile,
            area,
            ward_no,
            password
        )

        cursor.execute(sql, values)
        db.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================================
# Login
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        sql = """
        SELECT *
        FROM users
        WHERE email=%s AND password=%s
        """

        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:

            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["ward_no"] = user["ward_no"]

            return redirect(url_for("dashboard"))

        return "❌ Invalid Email or Password"

    return render_template("login.html")


# ==========================================
# Logout
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ==========================================
# Dashboard
# ==========================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Total complaints by this user
    cursor.execute(
        "SELECT COUNT(*) AS total FROM complaints WHERE user_id=%s",
        (user_id,)
    )
    total_complaints = cursor.fetchone()["total"]

    # Resolved complaints
    cursor.execute(
        "SELECT COUNT(*) AS total FROM complaints WHERE user_id=%s AND status='Resolved'",
        (user_id,)
    )
    resolved_complaints = cursor.fetchone()["total"]

    # Pending complaints
    cursor.execute(
        "SELECT COUNT(*) AS total FROM complaints WHERE user_id=%s AND status='Pending'",
        (user_id,)
    )
    pending_complaints = cursor.fetchone()["total"]

    # Recent complaints (latest 5)
    cursor.execute(
        """
        SELECT complaint_id, title, status
        FROM complaints
        WHERE user_id=%s
        ORDER BY complaint_id DESC
        LIMIT 5
        """,
        (user_id,)
    )
    recent_complaints = cursor.fetchall()

    return render_template(
        "dashboard.html",
        name=session["full_name"],
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        pending_complaints=pending_complaints,
        recent_complaints=recent_complaints
    )


# ==========================================
# Complaint
# ==========================================

@app.route("/complaint", methods=["GET", "POST"])
def complaint():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        category = request.form["category"]
        title = request.form["title"]
        description = request.form["description"]
        area = request.form["area"]
        ward_no = request.form["ward_no"]

        # ---------------------------------------------
        # ward_no (ward number entered by user) is NOT
        # the same as wards.ward_id (auto-increment PK).
        # complaints.ward_id is a foreign key to
        # wards.ward_id, so we must look up the correct
        # ward_id using ward_number first.
        # ---------------------------------------------

        cursor.execute(
            "SELECT ward_id FROM wards WHERE ward_number = %s",
            (ward_no,)
        )

        ward_row = cursor.fetchone()

        if not ward_row:

            cursor.execute("SELECT ward_id, ward_number, ward_name, area_name FROM wards ORDER BY ward_number")
            ward_list = cursor.fetchall()

            area_ward_map = []
            for w in ward_list:
                areas = [a.strip() for a in w["area_name"].split(",")]
                for area in areas:
                    area_ward_map.append({"area": area, "ward_number": w["ward_number"]})

            return render_template(
                "complaint.html",
                wards=ward_list,
                selected_category=category,
                area_ward_map=area_ward_map,
                error="Invalid Ward Number. Please select a valid ward."
            )

        ward_id = ward_row["ward_id"]

        # ---------------------------------------------
        # Auto-assign the correct representative based on
        # the citizen's specific area (not just the ward),
        # so each complaint reaches only the representative
        # responsible for that area.
        # ---------------------------------------------

        cursor.execute(
            "SELECT rep_id FROM representatives WHERE ward_id=%s AND LOWER(TRIM(area))=LOWER(TRIM(%s))",
            (ward_id, area)
        )
        rep_row = cursor.fetchone()
        rep_id = rep_row["rep_id"] if rep_row else None

        # ---------------------------------------------
        # Handle optional image upload
        # ---------------------------------------------

        image_path = None

        image_file = request.files.get("image")

        if image_file and image_file.filename != "":

            if allowed_file(image_file.filename):

                ext = image_file.filename.rsplit(".", 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex}.{ext}"
                safe_name = secure_filename(unique_name)

                save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
                image_file.save(save_path)

                # Path stored in DB, used with url_for('static', filename=...)
                image_path = f"uploads/{safe_name}"

        sql = """
        INSERT INTO complaints
        (
            user_id,
            category,
            title,
            description,
            area,
            ward_id,
            rep_id,
            image_path
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            session["user_id"],
            category,
            title,
            description,
            area,
            ward_id,
            rep_id,
            image_path
        )

        print("VALUES =", values)

        cursor.execute(sql, values)
        db.commit()

        print("Complaint Inserted Successfully")

        return redirect(url_for("dashboard", submitted=1))

    # GET request — load ward list for dropdown
    cursor.execute("SELECT ward_id, ward_number, ward_name, area_name FROM wards ORDER BY ward_number")
    ward_list = cursor.fetchall()

    # Build a flat list of areas + which ward each belongs to,
    # so the frontend can auto-suggest area and auto-select ward.
    area_ward_map = []

    for w in ward_list:
        areas = [a.strip() for a in w["area_name"].split(",")]
        for area in areas:
            area_ward_map.append({
                "area": area,
                "ward_number": w["ward_number"]
            })

    # Pre-fill category if it was passed from homepage/services cards
    selected_category = request.args.get("category", "")

    return render_template(
        "complaint.html",
        wards=ward_list,
        selected_category=selected_category,
        area_ward_map=area_ward_map
    )


# ==========================================
# My Complaints
# ==========================================

@app.route("/my_complaints")
def my_complaints():

    if "user_id" not in session:
        return redirect(url_for("login"))

    sql = """
    SELECT *
    FROM complaints
    WHERE user_id=%s
    ORDER BY complaint_id DESC
    """

    cursor.execute(sql, (session["user_id"],))

    complaints = cursor.fetchall()

    return render_template(
        "my_complaints.html",
        complaints=complaints
    )


# ==========================================
# Announcements
# ==========================================

@app.route("/announcements")
def announcements():

    # Show announcements relevant to the logged-in user's ward,
    # plus any general announcements (ward_id is NULL).
    # If not logged in, show all announcements.

    if "user_id" in session:

        cursor.execute(
            """
            SELECT a.*, w.ward_number
            FROM announcements a
            LEFT JOIN wards w ON a.ward_id = w.ward_id
            WHERE a.ward_id IS NULL
               OR a.ward_id = (SELECT ward_id FROM wards WHERE ward_number = %s)
            ORDER BY a.created_at DESC
            """,
            (session["ward_no"],)
        )

    else:

        cursor.execute(
            """
            SELECT a.*, w.ward_number
            FROM announcements a
            LEFT JOIN wards w ON a.ward_id = w.ward_id
            ORDER BY a.created_at DESC
            """
        )

    announcement_list = cursor.fetchall()

    return render_template("announcements.html", announcements=announcement_list)


# ==========================================
# Profile
# ==========================================

@app.route("/track", methods=["GET"])
def track():

    complaint_id = request.args.get("complaint_id", "").strip()

    complaint = None
    searched = False
    representative = None

    if complaint_id:

        searched = True

        cursor.execute(
            """
            SELECT
                c.complaint_id,
                c.category,
                c.title,
                c.description,
                c.area,
                c.status,
                c.image_path,
                w.ward_number,
                u.full_name AS citizen_name
            FROM complaints c
            JOIN wards w ON c.ward_id = w.ward_id
            JOIN users u ON c.user_id = u.user_id
            WHERE c.complaint_id = %s
            """,
            (complaint_id,)
        )

        complaint = cursor.fetchone()

        if complaint:

            cursor.execute(
                """
                SELECT full_name, mobile, email
                FROM representatives
                WHERE ward_id = (SELECT ward_id FROM wards WHERE ward_number = %s)
                LIMIT 1
                """,
                (complaint["ward_number"],)
            )
            representative = cursor.fetchone()

    return render_template(
        "track.html",
        complaint=complaint,
        searched=searched,
        representative=representative,
        complaint_id=complaint_id
    )
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor.execute(
        "SELECT full_name, email, mobile, area, ward_no, created_at FROM users WHERE user_id=%s",
        (session["user_id"],)
    )
    user = cursor.fetchone()

    return render_template("profile.html", user=user)


# ==========================================
# Representative Login
# ==========================================

@app.route("/rep_login", methods=["GET", "POST"])
def rep_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        sql = """
        SELECT *
        FROM representatives
        WHERE email=%s AND password=%s
        """

        cursor.execute(sql, (email, password))

        rep = cursor.fetchone()

        if rep:

            session["rep_id"] = rep["rep_id"]
            session["rep_name"] = rep["full_name"]
            session["rep_ward_id"] = rep["ward_id"]

            return redirect(url_for("rep_dashboard"))

        return "❌ Invalid Email or Password"

    # GET request — load representative list for dropdown
    cursor.execute(
        """
        SELECT r.rep_id, r.full_name, r.email, w.ward_number
        FROM representatives r
        JOIN wards w ON r.ward_id = w.ward_id
        ORDER BY r.full_name
        """
    )
    rep_list = cursor.fetchall()

    return render_template("rep_login.html", representatives=rep_list)


# ==========================================
# Representative Dashboard
# ==========================================

@app.route("/rep_dashboard")
def rep_dashboard():

    if "rep_id" not in session:
        return redirect(url_for("rep_login"))

    rep_id = session["rep_id"]
    ward_id = session["rep_ward_id"]

    # Complaints assigned specifically to this representative
    # (based on area match at submission time), plus any
    # ward complaints that couldn't be matched to a specific
    # area/representative (rep_id IS NULL) so nothing gets lost.
    cursor.execute(
        """
        SELECT
            c.complaint_id,
            c.category,
            c.title,
            c.description,
            c.area,
            c.image_path,
            c.work_photo_path,
            c.status,
            c.created_at,
            u.full_name AS citizen_name,
            u.mobile AS citizen_mobile
        FROM complaints c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.rep_id = %s
           OR (c.ward_id = %s AND c.rep_id IS NULL)
        ORDER BY c.complaint_id DESC
        """,
        (rep_id, ward_id)
    )

    complaints = cursor.fetchall()

    # Quick stats
    total = len(complaints)
    pending = len([c for c in complaints if c["status"] == "Pending"])
    resolved = len([c for c in complaints if c["status"] == "Resolved"])

    return render_template(
        "rep_dashboard.html",
        name=session["rep_name"],
        complaints=complaints,
        total=total,
        pending=pending,
        resolved=resolved
    )


# ==========================================
# Update Complaint Status (Representative)
# ==========================================

@app.route("/update_status/<int:complaint_id>", methods=["POST"])
def update_status(complaint_id):

    if "rep_id" not in session:
        return redirect(url_for("rep_login"))

    new_status = request.form["status"]

    # ---------------------------------------------
    # Handle optional "work done" photo upload
    # ---------------------------------------------

    work_photo_file = request.files.get("work_photo")
    work_photo_path = None

    if work_photo_file and work_photo_file.filename != "":

        if allowed_file(work_photo_file.filename):

            ext = work_photo_file.filename.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            safe_name = secure_filename(unique_name)

            save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
            work_photo_file.save(save_path)

            work_photo_path = f"uploads/{safe_name}"

    # Only allow updating complaints that belong to this rep's ward.
    # Also auto-claim the complaint (assign rep_id) if it wasn't
    # matched to a specific representative at submission time.

    if work_photo_path:
        cursor.execute(
            "UPDATE complaints SET status=%s, work_photo_path=%s, rep_id=COALESCE(rep_id, %s) WHERE complaint_id=%s AND ward_id=%s",
            (new_status, work_photo_path, session["rep_id"], complaint_id, session["rep_ward_id"])
        )
    else:
        cursor.execute(
            "UPDATE complaints SET status=%s, rep_id=COALESCE(rep_id, %s) WHERE complaint_id=%s AND ward_id=%s",
            (new_status, session["rep_id"], complaint_id, session["rep_ward_id"])
        )

    db.commit()

    # ---------------------------------------------
    # Notify citizen by email if complaint is Resolved
    # ---------------------------------------------

    if new_status == "Resolved":

        cursor.execute(
            """
            SELECT u.email, u.full_name, c.title
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.complaint_id = %s
            """,
            (complaint_id,)
        )
        citizen = cursor.fetchone()

        if citizen and citizen["email"]:
            send_email(
                to_email=citizen["email"],
                subject=f"Your complaint #{complaint_id} has been Resolved - CivicConnect",
                body=(
                    f"Hi {citizen['full_name']},\n\n"
                    f"Good news! Your complaint \"{citizen['title']}\" (ID #{complaint_id}) "
                    f"has been marked as Resolved by your ward representative.\n\n"
                    f"Thank you for using CivicConnect to make your city better.\n\n"
                    f"- CivicConnect Team"
                )
            )

    return redirect(url_for("rep_dashboard"))


# ==========================================
# Representative Logout
# ==========================================

@app.route("/rep_logout")
def rep_logout():

    session.pop("rep_id", None)
    session.pop("rep_name", None)
    session.pop("rep_ward_id", None)

    return redirect(url_for("rep_login"))


# ==========================================
# Run App
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)