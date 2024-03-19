from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
from flask_app.models.user import User
from flask_app.models.event import Event
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from werkzeug.utils import secure_filename
from flask import send_from_directory
import os

UPLOAD_FOLDER = '/Users/michaelgoedel/Desktop/codingDojo/P&A/soloProject/iSport/UPLOAD_FOLDER'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))
    else:
        flash('Invalid file type')
        return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/validate/reg', methods=['POST'])
def validate_reg():
    if not User.validate_reg(request.form):
        return redirect('/')
    password = request.form['password']
    data = {'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(password),
            'birthdate': request.form['birthdate']}
    User.save(data)
    session['id'] = User.get_id_from_email(data['email'])
    session['first_name'] = data['first_name']
    session['last_name'] = data['last_name']
    session['email'] = data['email']
    return redirect('/home')

@app.route('/validate/login', methods=['POST'])
def validate_login():
    if not User.validate_log(request.form):
        return redirect('/')
    submitted_password = request.form['password']
    saved_password = User.get_password_hash(request.form['email'])
    if not bcrypt.check_password_hash(saved_password, submitted_password):
        flash("Incorrect password")
        return redirect('/')
    session['id'] = User.get_id_from_email(request.form['email'])
    session['first_name'] = User.get_name_from_id(session['id'])
    session['last_name'] = User.get_last_name_from_id(session['id'])
    session['email'] = request.form['email']
    return redirect('/home')

@app.route('/home')
def home():
    if not session:
        return redirect('/')
    count = []
    user = User.get_user_info_and_event_count(session['id'])
    events = Event.get_all_events_for_user(session['id'])
    creator = Event.get_attendees_events_with_creator(session['id'])
    for i in range(len(events)):
        id = events[i]['id']
        count.append(Event.get_events_counts(id))
    return render_template('home.html', user=user[0], events=events, count=count, creator=creator)

@app.route('/account')
def account():
    events = Event.get_all_events_for_user(session['id'])
    user = User.get_all_user_info(session['id'])
    return render_template('account.html', events=events, user=user[0])

@app.route('/account/<int:id>')
def user_account(id):
    events = Event.get_all_events_for_user(id)
    user = User.get_all_user_info(id)
    # return render_template('account.html', events=events, user=user[0])

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Save the file to a location on your server
                file.save('path/to/save/directory/filename.jpg')
                # Update the src attribute of the img tag
                img_src = 'path/to/save/directory/filename.jpg'  # Update this with the actual path
                return render_template('account.html', img_src=img_src, events=events, user=user[0])
    return render_template('account.html', events=events, user=user[0])

@app.route('/logout')
def clear():
    session.clear()
    return redirect('/')