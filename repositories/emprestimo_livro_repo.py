import sqlite3
import json
from typing import List, Optional
from models.emprestimo_model import Emprestimo
from models.emprestimo_livro_model import EmprestimoLivro
from models.cliente_model import Cliente

from sql.emprestimo_livro_sql import *
from util.database import obter_conexao

class EmprestimoLivroRepo:

    @classmethod
    def criar_tabela(cls):
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(SQL_CRIAR_TABELA)

    @classmethod
    def inserir(cls, emprestimo_id: int, livro_id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_INSERIR, (emprestimo_id, livro_id))
                if cursor.rowcount > 0:
                    return True
        except sqlite3.Error as ex:
            print(ex)
            return False
    @classmethod
    def inserir_emprestimo_livro_json(cls, arquivo_json: str):
        try:
            if EmprestimoLivroRepo.obter_quantidade() == 0:
                with open(arquivo_json, "r", encoding="utf-8") as arquivo:
                    emprestimos = json.load(arquivo)
                    for emprestimo_data in emprestimos:
                        emprestimo_id = emprestimo_data.get('emprestimo_id')
                        livro_id = emprestimo_data.get('livro_id')
                        if emprestimo_id is not None and livro_id is not None:
                            EmprestimoLivroRepo.inserir(emprestimo_id, livro_id)

        except FileNotFoundError:
            print(f"Arquivo '{arquivo_json}' não encontrado.")
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON '{arquivo_json}'.")
        except sqlite3.Error as ex:
            print(f"Erro SQL ao inserir empréstimo-livro do JSON: {ex}")


    @classmethod
    def obter_quantidade(cls) -> Optional[int]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_QUANTIDADE).fetchone()
                return int(tupla[0])
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def obter_todos(cls) -> List[EmprestimoLivro]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_TODOS).fetchall()

                emprestimos = [EmprestimoLivro(*t) for t in tuplas]
              
                return emprestimos
        except sqlite3.Error as ex:
            print(ex)
            return None

