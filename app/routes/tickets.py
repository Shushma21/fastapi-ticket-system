from fastapi import Depends,HTTPException,APIRouter
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..import models,schemas
from ..auth import verify_token,get_current_user
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

router = APIRouter()

def get_db():
	db=SessionLocal()
	try:
		yield db
	finally:
		db.close()


@router.post("/tickets/")
def create_ticket(ticket:schemas.TicketCreate,db:Session=Depends(get_db),token:str=Depends(oauth2_scheme)):
	email = verify_token(token)
	user = db.query(models.User).filter(models.User.email==email).first()
	new_ticket = models.Ticket(
					title=ticket.title,
					description=ticket.description,
					created_by = user.id
				)
	db.add(new_ticket)
	db.commit()
	db.refresh(new_ticket)

	return{"message":"Ticket created successfully","ticket_id":new_ticket.id}



@router.get("/tickets/")
def get_tickets(db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	if current_user.role == "admin":
		tickets = db.query(models.Ticket).all()
	else:
		tickets = db.query(models.Ticket).filter(models.Ticket.created_by==current_user.id).all()
	return tickets


@router.put("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id:int,ticket_data:schemas.TicketStatusUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	if current_user.role != "admin":
		raise HTTPException(status_code=403,detail="Only admin can update ticket status")

	ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()

	if not ticket:
		raise HTTPException(status_code = 404,detail="Ticket not found")

	ticket.status = ticket_data.status
	db.commit()
	return{"message":"Ticket status updated successfully"}


@router.put("/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id:int,assign_data:schemas.AssignTicket,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	if current_user.role != "admin":
		raise HTTPException(status_code=403,detail="Only admin can update ticket status")

	ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()

	if not ticket:
		raise HTTPException(status_code=404,details="Ticket not found")

	ticket.assigned_to = assign_data.assigned_to
	db.commit()
	return{"message":"Ticket assigned successfully"}

