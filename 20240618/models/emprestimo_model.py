from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from models.cliente_model import Cliente
from models.livro_model import Livro

@dataclass
class Emprestimo:
    id: Optional[int] = None
    cliente_id: Optional[int] = None
    data_emprestimo: Optional[date] = None
    livro_id: Optional[int] = None