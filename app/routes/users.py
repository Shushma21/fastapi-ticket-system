from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

from ..import models,schemas
from ..auth import hash_password,verify_password,create_access_token,verify_token,get_db


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register/")
def register_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
	existing_email = db.query(models.User).filter(models.User.email==user.email).first()
	if existing_email:
		raise HTTPException(status_code=400,detail="Email already exists")

	existing_username = db.query(models.User).filter(models.User.username==user.username).first()
	if existing_username:
		raise HTTPException(status_code=400,detail="Username already exists")

	try:
		hashed_pwd = hash_password(user.password)
		new_user = models.User(
				username=user.username,
				email=user.email,
				password=hashed_pwd
				)

		db.add(new_user)
		db.commit()
		db.refresh(new_user)

		return{"message":"User Created Successfully","user_id":new_user.id}
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=500,detail=str(e))


@router.post("/login/")
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
	db_user = db.query(models.User).filter(models.User.username==form_data.username).first()

	if not db_user:
		raise HTTPException(status_code=404,detail="User not found")

	if not verify_password(form_data.password,db_user.password):
		raise HTTPException(status_code=401,detail="Invalid password")

	token = create_access_token({"sub":db_user.email})

	return{"access_token":token,"token_type":"bearer"}


@router.get("/profile/")
def get_profile(token:str=Depends(oauth2_scheme)):
	email = verify_token(token)
	return{"message":"Protected route accessed","email":email}
