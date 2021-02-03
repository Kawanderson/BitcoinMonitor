from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

basedir = os.path.dirname(os.path.abspath(__file__))

engine = create_engine('sqlite:///'+os.path.join(basedir, "Users.db"))
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    username = Column(String(32), nullable=False)
    time_monitor = Column(Integer, default=15)
    last_price = Column(Float, default=0)
    win_percent = Column(Integer, default=1)
    loss_percent = Column(Integer, default=10)
    monitor_type = Column(Integer, default=1)
    start_date = Column(DateTime, default=datetime.now())

    def __init__(self, chat_id, username) -> None:
        self.chat_id = chat_id
        self.username = username
    

    def __repr__(self) -> str:
        return f"<User(name={self.username}, chat_id={self.chat_id})>"
    

if __name__ == "__main__":
    Base.metadata.create_all(engine)