import sys
import os

sys.path.append(os.getcwd())

from app.database.sessions import engine, BaseModel
from .client import Client
from .query import UserQuery
from .email_verification import EmailVerification
from .client_session import ClientSession
from .password_reset import PasswordReset
from .film import Film
from .genre import Genre
from .film_genre import FilmGenre
from .age_certification import AgeCertification
from .vectors import Vectors
from .admin import Admin
from .query_film import QueryFilm

import pgvector.sqlalchemy

def init_db():
    BaseModel.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()