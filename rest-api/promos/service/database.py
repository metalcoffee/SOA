from sqlalchemy import create_engine, Column, String, Double, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

Base = declarative_base()

class Promo(Base):
    __tablename__ = 'promos'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    creator_id = Column(String(36), nullable=False)
    discount = Column(Double, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Database:
    def __init__(self, db_url='sqlite:////app/data/promos.db'):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

db = Database()
db.create_tables()
