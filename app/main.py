from fastapi import FastAPI
from .database import engine
from .import models
from .routes import users,tickets

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(tickets.router)

@app.get("/")
def read_root():
	return{"message":"Hello its shushma"}
