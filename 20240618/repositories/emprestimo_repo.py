import sqlite3
import json

from typing import Optional, List
from models.cliente_model import Cliente
from models.emprestimo_model import Emprestimo
from sql.emprestimo_sql import *
from util.database import obter_conexao

class EmprestimoRepo:
    @classmethod
    def criar_tabela(cls):
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(SQL_CRIAR_TABELA)

    @classmethod
    def inserir(cls, emprestimo: Emprestimo) -> Optional[Emprestimo]:
        try:
    
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_INSERIR, (
                    emprestimo.cliente_id,
                    emprestimo.data_emprestimo,
                ))
                if cursor.rowcount > 0:
                    emprestimo.id = cursor.lastrowid
                    return emprestimo
        except sqlite3.Error as ex:
            print(ex)
            return None
    @classmethod
    def inserir_emprestimo_json(cls, arquivo_json: str):
        if EmprestimoRepo.obter_quantidade() == 0:
            with open(arquivo_json, "r", encoding="utf-8") as arquivo:
                emprestimos = json.load(arquivo)
                for emprestimo in emprestimos:
                    EmprestimoRepo.inserir(Emprestimo(**emprestimo))

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
    def obter_todos(cls) -> List[Emprestimo]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_TODOS).fetchall()
                emprestimo = [Emprestimo(*t) for t in tuplas]
                return emprestimo
        except sqlite3.Error as ex:
            print(ex)
            return None


