from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#DATABASE_URL = "postgresql://postgres:password@localhost/ticket_db"
DATABASE_URL = "postgresql+psycopg2://postgres:mypassword@localhost/fastapi_ticket_system"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
	autocommit = False,
	autoflush = False,
	bind = engine
)


Base = declarative_base()
