import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from project import app, db, bcrypt
from project.forms import RegisterForm, LoginForm, CreateCourse, UpdateUserInfo, UpdateUserImg, UpdateUserPassword, RateCourse, CreateUniCourse
from project.models import User, Course, Rating, UniversityCourses
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.sql import func



def save_picture(form_picture, width, height, place):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics/' + place, picture_fn)

    output_size = (width, height)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/")
@app.route("/home")
def home():
    courses = Course.query.order_by(Course.date.desc())
    uni_courses = UniversityCourses.query.order_by(UniversityCourses.date.desc())
    return render_template('home.html', courses=courses, uni_courses=uni_courses)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, user_type=form.user_type.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/courses", methods=['GET', 'POST'])
def course():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    page = request.args.get('page', 1, type=int)
    courses = Course.query.order_by(Course.date.desc()).paginate(page=page, per_page=20)
    form = CreateCourse()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 210, 210, 'course_pics')
            new_course = Course(name=form.title.data, course_email=form.email.data, image=picture_file,
                                description=form.description.data, author=current_user)
            db.session.add(new_course)
            db.session.commit()
            flash('The course has been added to the list!', 'success')
            return redirect(url_for('course'))
    rate_form = RateCourse()
    if rate_form.validate_on_submit() and rate_form.rate_button.data:
        clicked_course_id = int(rate_form.clicked_course_id.data)
        clicked_course_rated = Course.query.filter_by(course_id=clicked_course_id).first()
        existing = Rating.query.filter(Rating.course_id == clicked_course_id, Rating.user_id == current_user.id).first()
        if not existing:
            rate = Rating(rating=rate_form.rate.data, maker=current_user, owner=clicked_course_rated)
            db.session.add(rate)
            db.session.commit()
        else:
            existing.rating = rate_form.rate.data
            db.session.commit()

    cs = db.session.execute('SELECT course_id, rating, user_id FROM rating')
    id_list = []
    for i in cs:
        if i[0] not in id_list:
            id_list.append(i[0])
    sc = db.session.execute('SELECT course_id, rating FROM rating')
    total_ratings = dict()
    for i in id_list:
        total_ratings[i] = []
    for i in sc:
        total_ratings[i[0]].append(i[1])

    ratings = dict()

    for i in id_list:
        ratings[i] = int(sum(total_ratings[i])/len(total_ratings[i]))

    return render_template('courses.html', title='Courses', courses=courses, form=form, rate_form=rate_form, ratings=ratings)


@app.route("/user_profile", methods=['GET', 'POST'])
@login_required
def user_profile():
    form = UpdateUserInfo()
    img_form = UpdateUserImg()
    password_form = UpdateUserPassword()

    if form.validate_on_submit() and form.save_changes.data:
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.description = form.description.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user_profile'))

    elif password_form.validate_on_submit() and password_form.update_password.data:
        hashed_new_password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
        current_user.password = hashed_new_password
        db.session.commit()
        logout_user()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('user_profile'))

    elif img_form.validate_on_submit() and img_form.change_image.data:
        if current_user.image != 'img.png':
            current_user_img = os.path.join(app.root_path, 'static/pics/profile_pics/' + current_user.image)
            if os.path.exists(current_user_img):
                os.remove(current_user_img)
        profile_img = save_picture(img_form.image.data, 250, 250, 'profile_pics')
        current_user.image = profile_img
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user_profile'))

    return render_template('user_profile.html', title='User Profile', form=form, img_form=img_form, password_form=password_form)



@app.route("/university", methods=['GET', 'POST'])
@login_required
def university():
    page = request.args.get('page', 1, type=int)
    courses = UniversityCourses.query.order_by(UniversityCourses.date.desc()).paginate(page=page, per_page=20)
    form = CreateUniCourse()
    available_days = request.form.getlist('days')
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 210, 210, 'uni_course_pics')
            days = {
                'monday': False,
                'tuesday': False,
                'wednesday': False,
                'thursday': False,
                'friday': False,
                'saturday': False,
                'sunday': False,
            }
            for day in available_days:
                if day in days.keys():
                    days[day] = True
            new_course = UniversityCourses(course_title=form.course_title.data,
                                           org_name=form.org_name.data,
                                           uni_name=current_user.username,
                                           location=form.location.data,
                                           org_email=current_user.email,
                                           image=picture_file,
                                           monday=days['monday'],
                                           tuesday=days['tuesday'],
                                           wednesday=days['wednesday'],
                                           thursday=days['thursday'],
                                           friday=days['friday'],
                                           saturday=days['saturday'],
                                           sunday=days['sunday'],
                                           start_date=str(request.form['start_date']),
                                           end_date=str(request.form['end_date']),
                                           start_time=str(request.form['start_time']),
                                           end_time=str(request.form['end_time']),
                                           description=form.description.data)
            db.session.add(new_course)
            db.session.commit()
            flash('The course has been added to the list!', 'success')
            return redirect(url_for('university'))
    return render_template('university.html', title='Universities', courses=courses, form=form, available_days=available_days)
