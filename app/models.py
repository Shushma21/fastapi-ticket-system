from sqlalchemy import Column,Integer,String, Date,ForeignKey
from .database import Base
from datetime import date

class User(Base):
	__tablename__ = "tbl_users"
	
	id = Column(Integer,primary_key=True,index=True)
	username = Column(String,unique=True)
	email = Column(String,unique=True)
	password = Column(String)
	role = Column(String,default="user")
	is_login = Column(Integer,default=0)
	is_deleted = Column(Integer,default=0)
	created_date = Column(Date,default=date.today)


class Ticket(Base):
	__tablename__ = "tbl_tickets"

	id = Column(Integer,primary_key=True,index=True)
	title = Column(String)
	description = Column(String)
	assigned_to = Column(Integer,ForeignKey("tbl_users.id"),nullable=True)
	status = Column(String,default="open")
	created_by = Column(Integer,ForeignKey("tbl_users.id"))
