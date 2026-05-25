from fastapi import Depends,HTTPException,APIRouter,Query
from sqlalchemy.orm import Session

from ..import models,schemas
from ..auth import get_current_user,get_db
from ..logger import logger
from ..exceptions import TicketNotFoundException

router = APIRouter()


@router.post("/tickets/",response_model=schemas.TicketOut,status_code=201)
def create_ticket(ticket:schemas.TicketCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	new_ticket = models.Ticket(
					title=ticket.title,
					description=ticket.description,
					created_by=current_user.id
				)
	db.add(new_ticket)
	db.commit()
	db.refresh(new_ticket)

	return new_ticket


@router.get("/tickets/",response_model=list[schemas.TicketOut])
def get_tickets(skip:int=Query(0,ge=0,le=100),limit:int=Query(5,ge=1,le=100),status:str=Query(None,pattern="^(open|closed)$"),search:str=Query(None,example="login"),db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	
	logger.info("Tickets API Called")

	query = db.query(models.Ticket)

	#Role filtering
	if current_user.role != "admin":
		query = query.filter(models.Ticket.created_by == current_user.id)

	#status filtering
	if status:
		query = query.filter(models.Ticket.status == status)

	#Search filtering
	if search:
		query = query.filter(models.Ticket.title.ilike(f"%{search}%"))

	tickets = query.offset(skip).limit(limit).all()

	return tickets


@router.put("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id:int,ticket_data:schemas.TicketStatusUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	if current_user.role != "admin":
		raise HTTPException(status_code=403,detail="Only admin can update ticket status")

	ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()

	if not ticket:
#		raise HTTPException(status_code=404,detail="Ticket not found")
		raise TicketNotFoundException(ticket_id)

	ticket.status = ticket_data.status
	db.commit()
	return{"message":"Ticket status updated successfully"}


@router.put("/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id:int,assign_data:schemas.AssignTicket,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
	if current_user.role != "admin":
		raise HTTPException(status_code=403,detail="Only admin can assign tickets")

	ticket = db.query(models.Ticket).filter(models.Ticket.id==ticket_id).first()

	if not ticket:
		raise HTTPException(status_code=404,detail="Ticket not found")

	ticket.assigned_to = assign_data.assigned_to
	db.commit()
	return{"message":"Ticket assigned successfully"}
