from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Livro:
    id: Optional[int] = None
    nome: Optional[str] = None
    autor: Optional[str] = None
    descricao: Optional[str] = None
    isbn: Optional[str] = None
