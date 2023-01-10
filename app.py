from flask import Flask, render_template, redirect, session, flash,url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,Feedback
from forms import RegisterForm,LoginForm,FeedbackForm,RemoveForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.app_context().push()
connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """show homepage with links to site areas"""
    
    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register_user():
    """show a form when submitted will create a user"""
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    form =RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        new_user = User.register(username =username, password =password,
                                 email =email, first_name=first_name,
                                 last_name = last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username'] =new_user.username
        return redirect('/register')
    # return redirect(f"/users/{user.username}")
        
    return render_template("/users/register.html", form=form)

@app.route('/login', methods=["GET","POST"])
def login_user():
    """log in a user """
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        login_user = User.authenticate(username,password)
        if login_user :
            session['username'] = login_user.username
            return redirect(f"/users/{login_user.username}")
        else:
            form.username.errors =['Invalid username/passowrd']
            return render_template('/users/login.html', form =form)
    return render_template('/users/login.html', form=form)
@app.route("/users/<username>")
def show_user(username):
    """show indivisual user login """
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    user = User.query.get_or_404(username)
    form = RemoveForm()
    return render_template('users/show.html',user=user,form=form)


### log out route

# @app.route('/logout', methods=["DELETE"])
# def logout_user():
#     user = User.query.get_or_404()

@app.route('/logout')
def logout_user():
    if "username" not in session :
        raise Unauthorized()
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/users/<username>/delete', methods =["POST"])
def delete_user(username):
    """delete user and redirect to login"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    user =User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect('/login')


# GET& POST /users/<username>/feedback/add
@app.route('/users/<username>/feedback/add',methods =["GET","POST"])
def add_feedback(username):
    """show add-feedback form and process it"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback/add_feedback.html", form=form)

# GET & POST /users/<username>/feedback-id/update
@app.route('/feedback/<int:feedback_id>/update',methods=["GET","POST"])
def update_feedback(feedback_id):
    """show update feedback form and process it"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("feedback/edit.html", form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """delete a feedback"""
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    
    form = RemoveForm()
    print("*************" ,feedback.username)
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
        
    return redirect(f"/users/{feedback.username}")
      