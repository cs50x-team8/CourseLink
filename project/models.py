from datetime import datetime
from project import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='img.png')
    user_type = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text)
    course = db.relationship('Course', backref='author', lazy=True)
    rating = db.relationship('Rating', backref='maker', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}', '{self.image}', '{self.user_type}', '{self.description}')"


class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    course_email = db.Column(db.String(120), nullable=False, unique=False)
    image = db.Column(db.String(20), nullable=False, default='course.png')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ratings = db.relationship('Rating', backref='owner', lazy=True)

    def __repr__(self):
        return f"Course('{self.name}', '{self.date}', '{self.description}')"


class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column(db.Integer())
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Rating('{self.rating}')"


class UniversityCourses(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_title = db.Column(db.String(100), nullable=False)
    org_name = db.Column(db.String(20), nullable=False)
    uni_name = db.Column(db.String(20), nullable=False)
    org_email = db.Column(db.String(120), nullable=False, unique=False)
    location = db.Column(db.String(40), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(20), nullable=False, default='course.png')
    monday = db.Column(db.Boolean)
    tuesday = db.Column(db.Boolean)
    wednesday = db.Column(db.Boolean)
    thursday = db.Column(db.Boolean)
    friday = db.Column(db.Boolean)
    saturday = db.Column(db.Boolean)
    sunday = db.Column(db.Boolean)
    start_date = db.Column(db.String(40), nullable=False)
    end_date = db.Column(db.String(40), nullable=False)
    start_time = db.Column(db.String(40), nullable=False)
    end_time = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"User('{self.course_title}', '{self.org_name}', '{self.org_email}', '{self.location}', '{self.date}', '{self.image}', '{self.monday}', '{self.tuesday}', '{self.wednesday}', '{self.thursday}', '{self.friday}', '{self.saturday}', '{self.sunday}', '{self.start_date}', '{self.end_date}', '{self.start_time}', '{self.end_time}', '{self.description}')"