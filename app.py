import os

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db, User,Note
from forms import RegisterForm, LoginForm, CSRFProtectForm,NoteForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///flask_notes")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

##############################################################################
#auth routes

@app.get('/')
def redirect_to_register():
    """Redirects to /register"""

    return redirect('/register')

@app.route('/register', methods=['POST', 'GET'])
def load_register_page():
    """Display register html template or handle form submit to database"""


    if 'username' in session:
        username = session['username']
        return redirect(f"/users/{username}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        return redirect(f'/users/{user.username}')

    else:
        return render_template('register_form.html', form = form)

@app.route('/login', methods=['POST', 'GET'])
def login_user():
    """Display user login  html template or validate user"""


    if 'username' in session:
        username = session['username']
        return redirect(f"/users/{username}")


    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login_form.html", form=form)

@app.post('/logout')
def logout_user():
    """Will log out user"""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop("username", None)

    return redirect("/")



# FIXME: rearrange routes to organize them, auth, user, notes section
##############################################################################
#user route

@app.get('/users/<username>')
def show_user(username):
    """Loads individual user page"""
    user = User.query.get_or_404(username)
    notes = Note.query.all()

    if "username" not in session or session["username"] != username:
        flash("You must be logged in to view!")
        return redirect("/")

    form = CSRFProtectForm()
    # user = User.query.get_or_404(username)
    return render_template("user.html", form=form,user=user,notes=notes)

##############################################################################
#notes route

@app.post('/users/<username>/delete')
def delete_user(username):
    """delete registered user and redirect to the root rout"""

    form = CSRFProtectForm()
    username =User.query.get_or_404(username)

    if form.validate_on_submit():
        session.pop("username", None)

    db.session.delete(username)
    db.session.commit()

    return redirect('/')


@app.route('/users/<username>/notes/add', methods=['POST', 'GET'])
def add_notes(username):

    form = NoteForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title,content=content)
        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{username}")

    else:

        return render_template("note_form.html", form=form)


