from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime, timedelta

from util.validators import *


class LivroDTO(BaseModel):
    nome: str
    autor: str
    descricao: str
    isbn: str
   
