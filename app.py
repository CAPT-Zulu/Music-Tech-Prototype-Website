from flask import Flask, render_template, request, redirect, flash, session, url_for
from datetime import datetime, date
from flask_wtf import FlaskForm
import sqlite3
import psutil
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectMultipleField, SelectField, widgets
from wtforms.validators import DataRequired, URL, Optional, InputRequired

app = Flask(__name__)

# Security Key
app.config['SECRET_KEY'] = 'DjjeigkgJHJkHGF76KJGnRUIdhg/5UARf6WqQ7T88jx4cfjfsDoZqD59SRNdgqWeIuEcc762AX7th4zXv4CVGsgHNJfTkugXj8A1A8u1S3mjoeSt6F0GBf69abefgpXrIaVNtjIXRW61VDyuH5xERGjJBoBLW1Xb9UoyyiiZCiVsMccpsI='

# Connect database
# con = sqlite3.connect('/var/www/Music-Tech-Website-Demo/system.db', check_same_thread=False)
con = sqlite3.connect('system.db', check_same_thread=False)
cur = con.cursor()

# TODO:
#   Chatroom page
#   Layouts managment page
#   Job progress: Peoples jobs who has done what and who needs to do certain tasks.

### Form models ####
class NoValSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        """per_validation is disabled"""

class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Log In')

class CreateComment(FlaskForm):
    room = StringField('Room Name:', validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    comment = StringField('Comment:', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')

class EditComment(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    comment = StringField('Comment:', validators=[DataRequired()])
    submit = SubmitField('Submit Changes')

class CreateEvent(FlaskForm):
    name = StringField('Topic Name:', validators=[DataRequired()])
    description = StringField('Topic Description:', validators=[])
    location = StringField('Topic Location:', validators=[DataRequired()])
    starttime = StringField('Topic Start Time:', validators=[])
    endtime = StringField('Topic End Time:', validators=[])
    #layout = NoValSelectMultipleField("Select a Layout (if avaliable):", coerce=int, validators=[])
    jobs = NoValSelectMultipleField('Event Jobs:', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Event')

class EditEvent(FlaskForm):
    name = StringField('Topic Name:', validators=[DataRequired()])
    description = StringField('Topic Description:', validators=[])
    location = StringField('Topic Location:', validators=[DataRequired()])
    starttime = StringField('Topic Start Time:', validators=[])
    endtime = StringField('Topic End Time:', validators=[])
    #layout = NoValSelectMultipleField("Select a Layout (if avaliable):", coerce=int, validators=[])
    jobs = NoValSelectMultipleField('Event Jobs:', coerce=int, validators=[])
    submit = SubmitField('Submit Changes')

class CreateJob(FlaskForm):
    name = StringField('Job Title:', validators=[DataRequired()])
    description = StringField('Job Description:', validators=[])
    submit = SubmitField('Create Job')

### Functions ###
def getserverstats():
    temp = psutil.sensors_temperatures()
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage()
    network = psutil.net_io_counters()

    return [temp, cpu, memory, disk, network]

def getEvents(Limit):
    sql_events = """
        SELECT *
        FROM events
        ORDER BY event_starttime desc
        LIMIT ?"""
    cur.execute(sql_events, (Limit,))
    results_events = cur.fetchall()

    final_results = []
    for event in results_events:
        event = list(event)
        event.append(str(len(getJobsLeft(event[0]))))
        final_results.append(event)

    return final_results

def getPaperwork():
    results = ''
    return results

def getJobs():
    sql_jobs = """
        SELECT *
        FROM jobs;"""
    cur.execute(sql_jobs, ())
    results_jobs = cur.fetchall()

    return results_jobs

def getComments(room):
    sql_comments = """
        SELECT *
        FROM comments
        WHERE room = ?
        ORDER BY posted DESC;"""
    cur.execute(sql_comments, (room,))
    results_comments = cur.fetchall()

    return results_comments

def getEventJobs(event_id):
    sql_event_jobs = """
        SELECT j.job_name, j.job_description, ej.names, ej.job_id
        FROM jobs j, events_jobs ej
        WHERE ej.event_id = ?
        AND ej.job_id = j.job_id
        ORDER BY job_name ASC;"""
    cur.execute(sql_event_jobs, (event_id,))
    results_event_jobs = cur.fetchall()

    return results_event_jobs

def getJobsLeft(event_id):
    sql_jobs_left = """
        SELECT *
        FROM events_jobs
        WHERE event_id = ?
        AND names = '';"""
    cur.execute(sql_jobs_left, (event_id,))
    results_jobs_left = cur.fetchall()

    return results_jobs_left

### routes ###
@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    # Set LoginForm
    form = LoginForm()
    # If the user is logged in view recent videos
    if session.get('username'):
        results_events = getEvents('100')
        return render_template('index.html', title='Music Tech Events', results_events=results_events)
    else:
        # If the user is trying to log in using POST
        if request.method == 'POST':
            if form.validate_on_submit():
                # Set username and password variables
                un = form.username.data
                pw = form.password.data

                # Check users if the combination of username and password exists
                sql_user = """
                                select *
                                from users 
                                where username = ?
                                and password = ?;"""
                cur.execute(sql_user, (un, pw,))
                result_user = cur.fetchall()

                # If a user with that username and password combination exists set session values with the users data
                if len(result_user) == 1:
                    session['user_id'] = result_user[0][0]
                    session['acsess'] = result_user[0][1]
                    session['username'] = result_user[0][2]
                    session['firstname'] = result_user[0][4]
                    session['surname'] = result_user[0][5]

                    return redirect(url_for('index'))
                else:
                    flash("Username or password incorrect!")
            else:
                flash("There is something missing!")

        # If the user isnt logged in and isnt logging in
        results_events = getEvents('100')
        return render_template('index.html', title='Music Tech Events', form=form, results_events=results_events)

@app.route('/logout')
def logout():
    # clear out the session
    if session.get('username'):
        session['user_id'] = None
        session['acsess'] = None
        session['username'] = None
        session['firstname'] = None
        session['surname'] = None
        flash("You have successfully logged out")
    else:
        flash("You have to be logged in to do that!")
    return redirect(url_for('index'))

@app.route('/event', methods=['GET','POST'])
def event():
    form = CreateComment()
    if session.get('username'):
        if request.args.get('id'):
            event_id = request.args.get('id')

            # Get event
            sql_event = """
                SELECT *
                FROM events
                WHERE event_id = ?;"""
            cur.execute(sql_event, (event_id,))
            result_event = cur.fetchall()

            # Check if event_id is valid
            if len(result_event) > 0:
                # Event buttons
                if request.method == "POST":
                    if request.form.get('job_id'):
                        replace_job_id = request.form.get('job_id')
                        replace_names = request.form.get(('name_input[' + str(replace_job_id) + ']'))

                        sql_names = """
                            UPDATE events_jobs
                            SET names = ?
                            WHERE job_id = ?"""
                        cur.execute(sql_names, (replace_names, replace_job_id,))
                        con.commit()

                    elif form.validate_on_submit():
                        room = form.room.data
                        username = form.username.data
                        comment = form.comment.data

                        sql_comments = """
                            INSERT INTO comments (room, username, comment)
                            VALUES (?, ?, ?);"""
                        cur.execute(sql_comments, (room, username, comment,))
                        con.commit()

                        flash('Comment successfully posted!')

                # Get event jobs
                results_jobs = getEventJobs(event_id)

                # Get event comments
                results_comments = getComments('event_' + event_id)

                # Render html
                return render_template('event.html', title=str(result_event[0][1]), form=form, result_event=result_event, results_jobs=results_jobs, results_comments=results_comments)
            else:
                # Else a video could not be found so flash a message to the user and return them to the search page
                flash("An event with that id does not exist!")
                return redirect(url_for('event'))
        else:
            # If the user trys to request the page without the id get variable flash them a message and return them to the search page
            flash("You have to have a event_id to be able to accsess that page!")
            return redirect(url_for('event'))
    else:
        flash("You have to be logged in to do that!")
        return redirect(url_for('index'))

@app.route('/createevent', methods=['GET','POST'])
def createevent():
    form = CreateEvent()
    if session.get('acsess') == 'staff':
        avaliable_jobs = getJobs()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Form vars
                name = form.name.data
                description = form.description.data
                location = form.location.data
                starttime = form.starttime.data
                endtime = form.endtime.data
                layout = 'None' #form.layout.data
                jobs = form.jobs.data

                # Input
                sql_event = """
                            INSERT INTO events (event_name, event_description, event_location, event_starttime, event_endtime, event_layout)
                            VALUES (?, ?, ?, ?, ?, ?);"""
                cur.execute(sql_event, (name, description, location, starttime, endtime, layout,))
                con.commit()

                # Get the event_id for the just submitted event
                event_id = cur.lastrowid

                # add jobs for the event
                sql_event_jobs = """
                            INSERT INTO events_jobs (event_id, job_id)
                            VALUES (?, ?);"""

                for job in jobs:
                    cur.execute(sql_event_jobs, (event_id, job,))

                con.commit()

                flash("Event succesfully created!")
            else:
                flash("There is something missing or something is invalid!")

        return render_template('createevent.html', title='Create New Event', form=form, avaliable_jobs=avaliable_jobs)
    else:
        flash("You have to be logged in as staff to do that!")
        return redirect(url_for('index'))

@app.route('/editevent', methods=['GET','POST'])
def editevent():
    form = EditEvent()
    if session.get('acsess') == 'staff':
        if request.args.get('id'):
            event_id = request.args.get('id')

            # Get event
            sql_event = """
                SELECT *
                FROM events
                WHERE event_id = ?;"""
            cur.execute(sql_event, (event_id,))
            result_event = cur.fetchall()

            # Check if event_id is valid
            if len(result_event) > 0:
                # Event buttons
                if request.method == 'POST':
                    if request.form.get("delete_btn") == 'delete':
                        # delete event jobs
                        sql_jobs_delete = """
                                    DELETE FROM events_jobs
                                    WHERE event_id = ?;"""
                        cur.execute(sql_jobs_delete, (event_id,))
                        con.commit()

                        # delete the event
                        sql_event_delete = """
                                    DELETE FROM events
                                    WHERE event_id = ?;"""
                        cur.execute(sql_event_delete, (event_id,))
                        con.commit()

                        flash("Event successfully deleted!")
                        return redirect(url_for('index'))

                    elif form.validate_on_submit():
                        # Form vars
                        name = form.name.data
                        description = form.description.data
                        location = form.location.data
                        starttime = form.starttime.data
                        endtime = form.endtime.data
                        layout = 'None' #form.layout.data
                        jobs = form.jobs.data

                        # Update event
                        sql_event = """
                            UPDATE events
                            SET event_name = ?, event_description = ?, event_location = ?, event_starttime = ?, event_endtime = ?, event_layout = ?
                            WHERE event_id = ?;"""
                        cur.execute(sql_event, (name, description, location, starttime, endtime, layout, event_id,))
                        con.commit()

                        # Delete event jobs
                        sql_event_jobs_delete = """
                            DELETE FROM events_jobs
                            WHERE event_id = ?;"""
                        cur.execute(sql_event_jobs_delete, (event_id,))
                        con.commit()

                        # Add jobs for the event
                        sql_event_jobs = """
                            INSERT INTO events_jobs (event_id, job_id)
                            VALUES (?, ?);"""

                        for job in jobs:
                            cur.execute(sql_event_jobs, (event_id, job,))

                        con.commit()

                        flash("Event succesfully edited!")
                    else:
                        flash("There is something missing or something is invalid!")

                # Get events jobs
                event_jobs = getEventJobs(event_id)
                results_jobs = []
                for event_job in event_jobs:
                    if event_job[3] not in results_jobs:
                        results_jobs.append(event_job[3])

                # Get avaliable jobs
                avaliable_jobs = getJobs()

                # Render html
                return render_template('editevent.html', title='Edit: ' + str(result_event[0][1]), form=form, result_event=result_event[0], results_jobs=results_jobs, avaliable_jobs=avaliable_jobs)
            else:
                # Else a event could not be found
                flash("An event with that id does not exist or you dont have acsess to it!")
                return redirect(url_for('index'))
        else:
            flash("You have to have an event_id to be able to acsess that page!")
            return redirect(url_for('index'))
    else:
        flash("You have to be logged in as staff to do that!")
        return redirect(url_for('index'))

@app.route('/managejobs', methods=['GET','POST'])
def managejobs():
    form = CreateJob()
    if session.get('acsess') == 'staff':
        if request.method == 'POST':
            if request.form.get("delete_btn") == 'delete':
                job_id = request.form.get('job_id')
                # delete event jobs
                sql_jobs_delete = """
                            DELETE FROM events_jobs
                            WHERE job_id = ?;"""
                cur.execute(sql_jobs_delete, (job_id,))
                con.commit()

                # delete the event
                sql_job_delete = """
                            DELETE FROM jobs
                            WHERE job_id = ?;"""
                cur.execute(sql_job_delete, (job_id,))
                con.commit()

                flash("Job successfully deleted!")
                return redirect(url_for('managejobs'))

            elif form.validate_on_submit():
                # Form vars
                name = form.name.data
                description = form.description.data

                # Add job
                sql_job = """
                    INSERT INTO jobs (job_name, job_description)
                    VALUES (?, ?);"""
                cur.execute(sql_job, (name, description,))

                # Commit addition
                con.commit()

                flash('Job successfully created!')
            else:
                flash("There is something missing or something is invalid!")

        results_jobs = getJobs()

        return render_template('managejobs.html', title='Manage Jobs', form=form, results_jobs=results_jobs)
    else:
        flash("You have to be logged in as staff to do that!")
        return redirect(url_for('index'))

@app.route('/serverstats')
def serverstats():
    if session.get('acsess') == 'staff':
        serverStats = getserverstats()

        return render_template('serverstats.html', title='Server Stats', serverStats=serverStats)
    else:
        flash("You have to be logged in as staff to do that!")
        return redirect(url_for('index'))

# Website Startup
if __name__ == '__main__':
    host = '0.0.0.0'
    port = 7250
    app.run(host, port, debug=True)
    #app.run()