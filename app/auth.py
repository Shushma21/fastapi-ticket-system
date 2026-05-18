from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timedelta
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import SessionLocal
from .import models

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(
	schemes = ["bcrypt"],
	deprecated = "auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password:str):
	return pwd_context.hash(password)

def verify_password(plain_password,hashed_password):
	return pwd_context.verify(
		plain_password,
		hashed_password
	)


def create_access_token(data:dict):
	to_encode = data.copy()
	expire = datetime.utcnow() + timedelta(minutes=10)
	to_encode.update({"exp":expire})

	return jwt.encode(
		to_encode,
		SECRET_KEY,
		algorithm = ALGORITHM
	)


def verify_token(token:str):
	try:
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		email = payload.get("sub")
		if email is None:
			raise HTTPException(
				status_code=401,
				details = "Invalid token"
			)
		return email
	except JWTError:
		raise HTTPException(
			status_code = 401,
			detail = "Token is invalid"
		)



def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
	email = verify_token(token)
	user = db.query(models.User).filter(models.User.email==email).first()

	if not user:
		raise HTTPException(status_code = 404,detail="User Not Found")

	return user
