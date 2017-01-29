from flask import Flask, render_template, request, redirect, url_for, session
import ctypes
from ctypes import *
import sys
import logging
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.secret_key = 'MY_SUPER_SECRET_KEY'
from database_setup import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///capstone.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

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
		proffesion = request.form['proffesion']
		about_me = request.form['about_me']
		profile_pic = request.form['profile_pic']
		user = User(first_name=first_name, last_name=last_name, username=username, day_of_birth = day_of_birth, month_of_birth = month_of_birth, year_of_birth = year_of_birth, gender = gender, hometown=hometown, proffesion = proffesion, about_me = about_me, profile_pic = profile_pic, password=password)
		dbsession.add(user)
		dbsession.commit()
		return redirect(url_for('sign_in'))

@app.route('/signin',  methods=['GET', 'POST'])
def sign_in():
	if (request.method == 'POST'):
		username = request.form['username']
		password = request.form['password']
		user = dbsession.query(User).filter_by(username = username).first()
		if user == None or user.password != password:
			return render_template('sign_in.html', error = True)
		else:
			session['user_id'] = user.id
			return render_template('home_page.html')
	else :
		return render_template('sign_in.html')


@app.route('/myprofile')
def my_profile():
	print('user_id' in session)
	if 'user_id' not in session:
		return render_template('my_profile.html', error = True)
	else:
		user = dbsession.query(User).filter_by(id = session['user_id']).first()
		return render_template('my_profile.html', user = user)


@app.route('/editprofile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
	user=dbsession.query(User).filter_by(id = session['user_id']).first()
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
	session.pop('user_id', None)
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.run(debug=True)