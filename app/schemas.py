from pydantic import BaseModel,EmailStr

#this validates username & password is string and email is a valid email
class UserCreate(BaseModel):
	username:str
	email:EmailStr
	password:str


class UserLogin(BaseModel):
	username:str
	password:str
