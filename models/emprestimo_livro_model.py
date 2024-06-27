from dataclasses import dataclass
from models.emprestimo_model import Emprestimo
from models.livro_model import Livro
from typing import List, Optional


@dataclass
class EmprestimoLivro:
    id: Optional[int] = None
    emprestimo_id: Optional[int] = None
    livro_id: Optional[int] = None
    