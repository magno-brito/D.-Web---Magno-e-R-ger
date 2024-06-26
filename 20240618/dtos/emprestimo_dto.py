from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime, timedelta
from util.validators import *


class EmprestimoDTO(BaseModel):
    cliente_id: int
    data_emprestimo: date
    livro_id: int
    
   
