from fastapi  import FastAPI,Depends,HTTPException
from .database import engine,SessionLocal
from .import models,schemas
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

@app.post("/register")
def register_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
	existing_email = db.query(models.User).filter(models.User.email == user.email).first()
	if existing_email:
		raise HTTPException(status_code=400,detail="Email already exists")

	existing_username = db.query(models.User).filter(models.User.username==user.username).first()
	if existing_username:
		raise HTTPException(status_code=400,details="Username already exists")

	try:
		new_user = models.User(
			username = user.username,
			email = user.email,
			password = user.password,
		)

		db.add(new_user)
		db.commit()
		db.refresh(new_user)
		return {
			"message":"User Created",
			"user_id":new_user.id
		}
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=500,details=str(e))

@app.get("/")
def read_root():
	return {"message":"FastAPI is running"}
