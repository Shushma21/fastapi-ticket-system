class TicketNotFoundException(Exception):
	def __init__(self,ticket_id:int):
		self.ticket_id = ticket_id
