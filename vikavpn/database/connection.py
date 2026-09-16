from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.app import DB_URL, DEBUG
from database.models import Base

engine = create_engine(DB_URL, echo=DEBUG)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
