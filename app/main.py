from fastapi  import FastAPI,Depends,HTTPException
from .database import engine,SessionLocal
from .import models,schemas
from sqlalchemy.orm import Session
from .auth import hash_password,verify_password,create_access_token,verify_token
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

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
		raise HTTPException(status_code=400,detail="Username already exists")

	try:
		hashed_pwd = hash_password(user.password)

		new_user = models.User(
			username = user.username,
			email = user.email,
			password = hashed_pwd,
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


@app.post("/login/")
#def login(user:schemas.UserLogin,db:Session=Depends(get_db)):
def login(form_data:OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
	db_user = db.query(models.User).filter((models.User.email == form_data.username) | (models.User.username == form_data.username)).first()

	if not db_user:
		raise HTTPException(status_code=404,detail="User not found")

	if not verify_password(form_data.password,db_user.password):
		raise HTTPException(status_code=401,detail="Invalid password")

	token = create_access_token(
		{"sub":db_user.email}
	)

	return{
		"access_token":token,
		"token_type":"bearer"
	}


@app.get("/profile/")
def get_profile(token:str=Depends(oauth2_scheme)):
	email = verify_token(token)

	return{"message":"Protected route accessed","email":email}



@app.post("/tickets/")
def create_ticket(ticket:schemas.TicketCreate,db:Session=Depends(get_db),token:str=Depends(oauth2_scheme)):
	email = verify_token(token)

	user = db.query(models.User).filter(models.User.email == email).first()
	
	new_ticket = models.Ticket(
			title=ticket.title,
			description = ticket.description,
			created_by = user.id)

	db.add(new_ticket)
	db.commit()
	db.refresh(new_ticket)

	return{
		"message":"Ticket created successfully",
		"ticket_id":new_ticket.id
	}
