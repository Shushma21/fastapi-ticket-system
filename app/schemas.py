from pydantic import BaseModel,EmailStr,ConfigDict
from typing import Optional

#this validates username & password is string and email is a valid email
class UserCreate(BaseModel):
	username:str
	email:EmailStr
	password:str


class UserLogin(BaseModel):
	username:str
	password:str

class TicketCreate(BaseModel):
	title:str
	description:str

class TicketStatusUpdate(BaseModel):
	status:str

class AssignTicket(BaseModel):
	assigned_to:int


class UserOut(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id:int
	username:str
	email:EmailStr
	role:str


class TicketOut(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id:int
	title:str
	description:str
	status:str
	created_by:int
	assigned_to:Optional[int]


class TokenOut(BaseModel):
	access_token:str
	token_type:str
