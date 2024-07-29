from sqlalchemy import Column, Integer, String,Float
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    username = Column(String(255), unique=True,index=True)
    email = Column(String(255),unique=True,index=True)
    exp = Column(Float,default=0)
    coins = Column(Integer,default=0)
    profileImage = Column(String(255),default="")
    winStat = Column(Integer,default=0)
    loseStat = Column(Integer,default=0)
    