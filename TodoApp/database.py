from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
#SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password@localhost/TodoApplicationDatabase'
SQLALCHEMY_DATABASE_URL = 'postgresql://todoappdb_833x_user:nE1M16yHMQWdF1cd1MKEBWfikseJdo5c@dpg-db4c9e142hec73ar3dsg-a/todoappdb_833x'
#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:test1234@localhost:3306/TodoApplicationDatabase'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

