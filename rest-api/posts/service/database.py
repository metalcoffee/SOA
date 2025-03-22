from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    creator_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    is_private = Column(Boolean, default=False)
    tags = Column(JSON)

class Database:
    def __init__(self, db_url='sqlite:////app/data/posts.db'):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

db = Database()
db.create_tables()
