from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .exceptions import TicketNotFoundException
from .database import engine
from .import models
from .routes import users,tickets

app = FastAPI()

app.include_router(users.router)
app.include_router(tickets.router)

@app.get("/")
def read_root():
	return{"message":"Hello its shushma"}


@app.exception_handler(TicketNotFoundException)
async def ticket_not_found_handler(request,exc):
	return JSONResponse(status_code = 404,content={"message":f"Ticket {exc.ticket_id} not found"})
