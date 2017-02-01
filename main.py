from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, session as login_session
import ctypes
from ctypes import *
import sys
import logging
import os
from PIL import Image
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.secret_key = 'MY_SUPER_SECRET_KEY'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from database_setup import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///capstone.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
dbsession = DBSession()


def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
	return render_template('home_page.html')

@app.route('/signup' , methods=['GET', 'POST'])
def sign_up():
	if (request.method == 'GET'):
		return render_template('sign_up.html')
	else:
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		username = request.form['username']
		password = request.form['password']
		day_of_birth = request.form['day_of_birth']
		month_of_birth = request.form['month_of_birth']
		year_of_birth = request.form['year_of_birth']
		gender = request.form['gender']
		hometown = request.form['hometown']
		profession = request.form['profession']
		about_me = request.form['about_me']
		#profile_pic = request.form['profile_pic']


		profile_pic = request.files['profile_pic']

		if profile_pic.filename == '':
			profile_pic = url_for('uploaded_file', filename='None_.jpg')
		if profile_pic and allowed_file(profile_pic.filename):
			user = User(first_name=first_name, last_name=last_name, username=username, day_of_birth = day_of_birth, month_of_birth = month_of_birth, year_of_birth = year_of_birth, gender = gender, hometown=hometown, profession = profession, about_me = about_me, profile_pic = profile_pic, password=password)
			dbsession.add(user)
			filename = str(user.id) + "_" + secure_filename(profile_pic.filename)
			profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			user.set_photo(filename)
			dbsession.add(user)
			dbsession.commit()
			flash("User Created Successfully!")
			return redirect(url_for('sign_in'))
		else:
			flash("Please upload either a .jpg, .jpeg, .png, or .gif file.")
			return redirect(url_for('sign_up'))

@app.route('/signin',  methods=['GET', 'POST'])
def sign_in():
	if (request.method == 'POST'):
		username = request.form['username']
		password = request.form['password']
		user = dbsession.query(User).filter_by(username = username).first()
		if user == None or user.password != password:
			return render_template('sign_in.html', error = True)
		else:
			login_session['user_id'] = user.id
			login_session['user_profile_pic'] = user.profile_pic
			return render_template('home_page.html')
	else :
		return render_template('sign_in.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/myprofile')
def my_profile():
	print('user_id' in login_session)
	if 'user_id' not in login_session:
		return render_template('my_profile.html', error = True)
	else:
		user = dbsession.query(User).filter_by(id = login_session['user_id']).first()
		if user.profile_pic!=None:
			profile_pic_path = url_for('uploaded_file', filename=user.profile_pic)
		elif user.profile_pic.name == '' or user.profile_pic==None:
			default_profile_pic = url_for('uploaded_file', filename='None_.jpg')
			profile_pic_path = default_profile_pic
		return render_template('my_profile.html', user = user, profile_pic_path = profile_pic_path)


@app.route('/editprofile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
	user=dbsession.query(User).filter_by(id = login_session['user_id']).first()
	if (request.method == 'GET'):
		return render_template('edit_profile.html', user=user, user_id=user_id)
	else:
		password = request.form['oldpass']
		if (user.password!=password):
			return render_template ('edit_profile.html', error = True, user = user, user_id = user_id)
		else:
			user.password = request.form['newpass']
			dbsession.commit()
			return redirect(url_for('my_profile'))

@app.route('/logout')
def logout():
	login_session.pop('user_id', None)
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.run(debug=True)
