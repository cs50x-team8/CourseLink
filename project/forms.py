from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, RadioField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from project.models import User

from project import bcrypt


class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired(), Length(min=5, max=25)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Re-Password", validators=[DataRequired(), EqualTo("password")])
    user_type = SelectField("Account Type", choices=[("student", "student"), ("university", "university"), ("organization", "organization")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField("E-mail",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class CreateCourse(FlaskForm):
    title = StringField("Course Title", validators=[DataRequired(), Length(min=5, max=25)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    description = TextAreaField('Description', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class UpdateUserInfo(FlaskForm):
    username = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    description = TextAreaField('Personal Information')
    save_changes = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class UpdateUserImg(FlaskForm):
    image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    change_image = SubmitField('Change Image')


class UpdateUserPassword(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_new_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("new_password")])
    update_password = SubmitField('Update Password')

    def validate_old_password(self, old_password):
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError('That password is not equal to your exiting password !')


class RateCourse(FlaskForm):
    rate = RadioField('star', choices=[('1','1 stars'),
                                       ('2','2 stars'),
                                       ('3','3 stars'),
                                       ('4','4 stars'),
                                       ('5','5 stars')]
                      )
    clicked_course_id = IntegerField('clicked_course_id')

    rate_button = SubmitField('RATE')


class CreateUniCourse(FlaskForm):
    course_title = StringField("Course Title", validators=[DataRequired(), Length(min=5, max=25)])
    org_name = StringField("User Name", validators=[DataRequired(), Length(min=5, max=20)])
    location = StringField("User Name", validators=[DataRequired(), Length(min=5, max=40)])
    description = TextAreaField('Description', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')
