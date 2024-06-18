from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Livro:
    id: Optional[int] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    isbn: Optional[str] = None
