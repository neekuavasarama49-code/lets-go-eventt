from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask_mail import Mail, Message

app = Flask(__name__)

# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = "lets_go_event_secret_key"


# =========================================================
# EMAIL SETTINGS
# =========================================================
# We will configure email later.

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "YOUR_GMAIL@gmail.com"
app.config["MAIL_PASSWORD"] = "YOUR_APP_PASSWORD"
app.config["MAIL_DEFAULT_SENDER"] = "YOUR_GMAIL@gmail.com"

mail = Mail(app)


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            event_type TEXT,
            event_date TEXT,
            message TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(enquiries)")
    columns = [column[1] for column in cursor.fetchall()]

    # Status
    if "status" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN status TEXT DEFAULT 'Pending'
        """)

    # Admin notes
    if "admin_notes" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN admin_notes TEXT DEFAULT ''
        """)

    # Payment status
    if "payment_status" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'
        """)

    # Guests
    if "guests" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN guests INTEGER
        """)

    # Package
    if "package" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN package TEXT
        """)

    # Total amount
    if "total_amount" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN total_amount REAL DEFAULT 0
        """)

    # Advance amount
    if "advance_amount" not in columns:

        cursor.execute("""
            ALTER TABLE enquiries
            ADD COLUMN advance_amount REAL DEFAULT 0
        """)

    conn.commit()
    conn.close()


create_database()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# BOOK PACKAGE
# =========================================================

@app.route("/book_package", methods=["GET", "POST"])
def book_package():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        event_type = request.form.get(
            "event_type",
            ""
        ).strip()

        event_date = request.form.get(
            "event_date",
            ""
        ).strip()

        guests = request.form.get(
            "guests",
            ""
        ).strip()

        package = request.form.get(
            "package",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()


        conn = sqlite3.connect("event.db")
        cursor = conn.cursor()


        cursor.execute("""
            INSERT INTO enquiries
            (
                name,
                phone,
                email,
                event_type,
                event_date,
                message,
                status,
                admin_notes,
                payment_status,
                guests,
                package,
                total_amount,
                advance_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            event_type,
            event_date,
            message,
            "Pending",
            "",
            "Unpaid",
            guests,
            package,
            0,
            0
        ))


        # Automatically generated Booking ID
        booking_id = cursor.lastrowid


        conn.commit()
        conn.close()


        # Show booking confirmation
        return render_template(
            "book_package.html",
            success=True,
            booking_id=booking_id,
            name=name,
            event_type=event_type,
            event_date=event_date,
            guests=guests,
            package=package,
            phone=phone
        )


    return render_template("book_package.html")


# =========================================================
# CUSTOMER BOOKING STATUS
# =========================================================

@app.route("/booking_status", methods=["GET", "POST"])
def booking_status():

    enquiry = None
    error = None


    # Customer submitted Booking ID
    if request.method == "POST":

        booking_id = request.form.get(
            "booking_id",
            ""
        ).strip()


        # Check empty Booking ID
        if booking_id == "":

            error = "Please enter your Booking ID."


        else:

            conn = sqlite3.connect("event.db")
            cursor = conn.cursor()


            # Find booking using ID
            cursor.execute("""
                SELECT *
                FROM enquiries
                WHERE id = ?
            """, (booking_id,))


            enquiry = cursor.fetchone()


            conn.close()


            # If booking does not exist
            if enquiry is None:

                error = "Booking ID not found. Please check your Booking ID."


    return render_template(
        "booking_status.html",
        enquiry=enquiry,
        error=error
    )


# =========================================================
# NORMAL ENQUIRY FORM
# =========================================================

@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get(
        "name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    event_type = request.form.get(
        "event_type",
        ""
    ).strip()

    event_date = request.form.get(
        "event_date",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO enquiries
        (
            name,
            phone,
            email,
            event_type,
            event_date,
            message,
            status,
            admin_notes,
            payment_status,
            guests,
            package,
            total_amount,
            advance_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        event_type,
        event_date,
        message,
        "Pending",
        "",
        "Unpaid",
        None,
        None,
        0,
        0
    ))


    conn.commit()
    conn.close()


    # Show success message and open dashboard
    return """
    <script>
        alert("Thank you! Your enquiry has been submitted successfully.");
        window.location.href = "/admin";
    </script>
    """


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )


        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        else:

            return """
            <script>
                alert("Invalid username or password!");
                window.location.href = "/login";
            </script>
            """


    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    # Get all enquiries
    cursor.execute("""
        SELECT *
        FROM enquiries
        ORDER BY id DESC
    """)

    enquiries = cursor.fetchall()


    # Total
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
    """)

    total = cursor.fetchone()[0]


    # Pending
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
        WHERE status = 'Pending'
    """)

    pending = cursor.fetchone()[0]


    # Confirmed
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
        WHERE status = 'Confirmed'
    """)

    confirmed = cursor.fetchone()[0]


    # Completed
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
        WHERE status = 'Completed'
    """)

    completed = cursor.fetchone()[0]


    # Unpaid
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
        WHERE payment_status = 'Unpaid'
    """)

    unpaid = cursor.fetchone()[0]


    # Advance Paid
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
        WHERE payment_status = 'Advance Paid'
    """)

    advance_paid = cursor.fetchone()[0]


    # Fully Paid
    cursor.execute("""
        SELECT COUNT(*)
        FROM enquiries
        WHERE payment_status = 'Fully Paid'
    """)

    fully_paid = cursor.fetchone()[0]


    conn.close()


    return render_template(
        "admin.html",
        enquiries=enquiries,
        total=total,
        pending=pending,
        confirmed=confirmed,
        completed=completed,
        unpaid=unpaid,
        advance_paid=advance_paid,
        fully_paid=fully_paid
    )


# =========================================================
# VIEW BOOKING
# =========================================================

@app.route("/view/<int:id>")
def view(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    cursor.execute("""
        SELECT *
        FROM enquiries
        WHERE id = ?
    """, (id,))


    enquiry = cursor.fetchone()


    conn.close()


    if enquiry is None:

        return """
        <script>
            alert("Booking not found!");
            window.location.href = "/admin";
        </script>
        """


    return render_template(
        "details.html",
        enquiry=enquiry
    )


# =========================================================
# UPDATE EVENT STATUS
# =========================================================

@app.route(
    "/update_status/<int:id>",
    methods=["POST"]
)
def update_status(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    status = request.form.get(
        "status",
        "Pending"
    )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    cursor.execute("""
        UPDATE enquiries
        SET status = ?
        WHERE id = ?
    """, (
        status,
        id
    ))


    conn.commit()
    conn.close()


    return redirect(
        url_for("admin")
    )


# =========================================================
# UPDATE ADMIN NOTES
# =========================================================

@app.route(
    "/update_notes/<int:id>",
    methods=["POST"]
)
def update_notes(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    admin_notes = request.form.get(
        "admin_notes",
        ""
    )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    cursor.execute("""
        UPDATE enquiries
        SET admin_notes = ?
        WHERE id = ?
    """, (
        admin_notes,
        id
    ))


    conn.commit()
    conn.close()


    return redirect(
        url_for("admin")
    )


# =========================================================
# UPDATE PAYMENT STATUS
# =========================================================

@app.route(
    "/update_payment/<int:id>",
    methods=["POST"]
)
def update_payment(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    payment_status = request.form.get(
        "payment_status",
        "Unpaid"
    )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    cursor.execute("""
        UPDATE enquiries
        SET payment_status = ?
        WHERE id = ?
    """, (
        payment_status,
        id
    ))


    conn.commit()
    conn.close()


    return redirect(
        url_for("admin")
    )


# =========================================================
# EDIT BOOKING
# =========================================================

@app.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    # Save edited information
    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        event_type = request.form.get(
            "event_type",
            ""
        ).strip()

        event_date = request.form.get(
            "event_date",
            ""
        ).strip()

        guests = request.form.get(
            "guests",
            ""
        ).strip()

        package = request.form.get(
            "package",
            ""
        ).strip()

        total_amount = request.form.get(
            "total_amount",
            "0"
        ).strip()

        advance_amount = request.form.get(
            "advance_amount",
            "0"
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()


        if total_amount == "":

            total_amount = "0"


        if advance_amount == "":

            advance_amount = "0"


        cursor.execute("""
            UPDATE enquiries
            SET
                name = ?,
                phone = ?,
                email = ?,
                event_type = ?,
                event_date = ?,
                guests = ?,
                package = ?,
                total_amount = ?,
                advance_amount = ?,
                message = ?
            WHERE id = ?
        """, (
            name,
            phone,
            email,
            event_type,
            event_date,
            guests,
            package,
            total_amount,
            advance_amount,
            message,
            id
        ))


        conn.commit()
        conn.close()


        return redirect(
            url_for(
                "view",
                id=id
            )
        )


    # Get booking for editing
    cursor.execute("""
        SELECT *
        FROM enquiries
        WHERE id = ?
    """, (id,))


    enquiry = cursor.fetchone()


    conn.close()


    if enquiry is None:

        return """
        <script>
            alert("Booking not found!");
            window.location.href = "/admin";
        </script>
        """


    return render_template(
        "edit.html",
        enquiry=enquiry
    )


# =========================================================
# DELETE BOOKING
# =========================================================

@app.route(
    "/delete/<int:id>",
    methods=["POST"]
)
def delete(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )


    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()


    cursor.execute("""
        DELETE FROM enquiries
        WHERE id = ?
    """, (id,))


    conn.commit()
    conn.close()


    return redirect(
        url_for("admin")
    )


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )