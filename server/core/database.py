import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from server.core import env
from server.utils import path_util

Base = declarative_base()

SessionLocal = None


def init_db():
    if os.getenv("TESTING"):
        engine = create_engine(path_util.path_to_sqlalchemy_uri(path_util.TEST_DATABASE))
    else:
        engine = create_engine(path_util.path_to_sqlalchemy_uri(path_util.DATABASE))

    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from server.models.orm.match import Match
    from server.models.orm.player import Player
    Base.metadata.create_all(engine)

    return engine


def get_sessionlocal():
    global SessionLocal
    return SessionLocal

def set_sessionmaker(sm):
    global SessionLocal
    SessionLocal = sm
