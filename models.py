from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """connect to database"""
    
    app.app = app
    db.init_app(app)
    

class User(db.Model):
    """create user model"""
    __tablename__='users'

    username = db.Column(db.String(20),nullable = False,unique =True,primary_key=True)
    password = db.Column(db.Text,nullable =False)
    email = db.Column(db.String(50),nullable = False,unique = True )
    first_name = db.Column(db.String(30),nullable = False)
    last_name = db.Column(db.String(30),nullable = False)
    
    feedback =db.relationship("Feedback",backref ='user',cascade="all,delete-orphan")
    #using classmethod to make things easier
    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        """Register a user, hashing their password."""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # db.session.add(user)
        # return user
        return user
    
     # start_authenticate
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False
    # end_authenticate 
    
class Feedback(db.Model):
    __tablename__="feedbacks"
    id =db.Column(db.Integer,primary_key=True,unique =True,
                  nullable =False, autoincrement =True)
    title =db.Column(db.String(100),nullable =False)
    content = db.Column(db.Text,nullable =False)
    username = db.Column(db.String(20),db.ForeignKey('users.username'),nullable =False)
    

    
    