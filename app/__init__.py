#===========================================================
# Worker Task Assigner Project
# Ollie Bass
#-----------------------------------------------------------
# Assigns workers to certain tasks and keeps track of tasks and workers information.
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.            
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the tasks from the DB
        sql = """
            SELECT 
                id, 
                name, 
                priority, 
                completed 
            FROM tasks 
            WHERE completed=0
            ORDER BY priority DESC
        """
        params = []
        result = client.execute(sql, params)
        tasks = result.rows

                # Get all the tasks from the DB
        sql = """
            SELECT 
                id, 
                name, 
                priority, 
                completed 
            FROM tasks 
            WHERE completed=0
            ORDER BY priority DESC
        """
        params = []
        result = client.execute(sql, params)
        tasks = result.rows

        # Get all the workers from the DB
        sql = """
            SELECT 
                workers.id, 
                workers.name,
                allocations.task_id

            FROM workers
            JOIN allocations ON workers.id = allocations.worker_id

            ORDER BY workers.id ASC
        """
        params = []
        result = client.execute(sql, params)
        workers = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", tasks=tasks, workers=workers)


#-----------------------------------------------------------
# Worker page route - Show all Workers
#-----------------------------------------------------------
@app.get("/workers/<int:id>")
def show_all_workers():
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, notes, specialty, ethic FROM workers WHERE id=? ORDER BY name ASC"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            worker = result.rows[0]
            return render_template("pages/workers.jinja", workers=worker)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a worker, using data posted from a form
#-----------------------------------------------------------
@app.post("/workers/add")
def add_a_worker():
    # Get the data from the form
    name  = request.form.get("name")
    notes = request.form.get("notes")
    specialty = request.form.get("specialty")
    ethic = request.form.get("ethic")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO workers (name, price) VALUES (?, ?)"
        params = [name, notes, specialty, ethic]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Worker '{name}' added", "success")
        return redirect("/workers")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_worker(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM workers WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Worker removed", "thanks")
        return redirect("/workers")

