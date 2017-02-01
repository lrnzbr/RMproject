from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from database_setup import Base, User, Course

engine = create_engine('sqlite:///capstone.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user = User(first_name = 'Admin', last_name = 'Admin', username = 'admin', password = 'admin', day_of_birth = 28, month_of_birth = 2, year_of_birth = 2001, gender = 'Male', hometown = 'jerusalem', profession = 'admin', about_me = 'admin', profile_pic = None)
session.add(user)
session.commit()