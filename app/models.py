from sqlalchemy import Column,Integer,String, Date
from .database import Base
from datetime import date

class User(Base):
	__tablename__ = "tbl_users"
	
	id = Column(Integer,primary_key=True,index=True)
	username = Column(String,unique=True)
	email = Column(String,unique=True)
	password = Column(String)
	is_deleted = Column(Integer,default=0)
	created_date = Column(Date,default=date.today)
