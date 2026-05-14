from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timedelta
from fastapi import HTTPException

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(
	schemes = ["bcrypt"],
	deprecated = "auto"
)

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



