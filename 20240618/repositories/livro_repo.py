import json
import sqlite3
from typing import List, Optional
from models.livro_model import Livro
from sql.livro_sql import *
from util.database import obter_conexao


class LivroRepo():

    @classmethod
    def criar_tabela(cls):
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(SQL_CRIAR_TABELA)

    @classmethod
    def inserir(cls, livro: Livro) -> Optional[Livro]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_INSERIR, (
                    livro.nome,
                    livro.autor,
                    livro.descricao,
                    livro.isbn,
                    livro.emprestado
                    
                ))
                if cursor.rowcount > 0:
                    livro.id = cursor.lastrowid
                    conexao.commit()
                    print(f"Livro inserted with ID: {livro.id}")
                    return livro
                else:
                    print("Failed to insert livro. No rows affected.")
                    return None
                    
        except sqlite3.Error as ex:
            print(ex)
            return None
        
    @classmethod
    def obter_todos(cls) -> List[Livro]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_TODOS).fetchall()
                livros = [Livro(*t) for t in tuplas]
                return livros
        except sqlite3.Error as ex:
            print(ex)
            return None
        
    # @classmethod
    # def alterar(cls, livro: Livro) -> bool:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             cursor.execute(SQL_ALTERAR, (
    #                 livro.nome,
    #                 livro.autor,
    #                 livro.descricao,
    #                 livro.isbn,
    #                 livro.id
    #             ))
    #             return(cursor.rowcount > 0)
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return False

    @classmethod
    def alterar(cls, livro: Livro) -> Optional[Livro]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_ALTERAR, (
                    livro.nome,
                    livro.autor,
                    livro.descricao,
                    livro.isbn,
                    livro.emprestado,
                    livro.id
                ))
                if cursor.rowcount > 0:
                    conexao.commit()
                    return livro
                else:
                    return None
        except sqlite3.Error as ex:
            print(ex)
            return None
        
    @classmethod
    def alterar_emprestimo(cls, livro: Livro) -> Optional[Livro]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_ALTERAR_EMPRESTIMO, (
                    livro.emprestado,
                    livro.id
                ))
                if cursor.rowcount > 0:
                    conexao.commit()
                    return livro
                else:
                    return None
        except sqlite3.Error as ex:
            print(ex)
            return None
        
    @classmethod
    def excluir(cls, id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_EXCLUIR, (id,))
                return (cursor.rowcount > 0)
        except sqlite3.Error as ex:
            print(ex)
            return False
    
    @classmethod
    def obter_um(cls, id: int) -> Optional[Livro]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_UM, (id,)).fetchone()
                livro = Livro(*tupla)
                return livro
        except sqlite3.Error as ex:
            print(ex)
            return None
        
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
    def inserir_livros_json(cls, arquivo_json: str):
        if LivroRepo.obter_quantidade() == 0:
            with open(arquivo_json, "r", encoding="utf-8") as arquivo:
                livros = json.load(arquivo)
                for livro in livros:
                    LivroRepo.inserir(Livro(**livro))

    @classmethod
    def obter_busca(cls, termo: str, pagina: int, tamanho_pagina: int, ordem: int) -> List[Livro]:
        termo = "%"+termo+"%"
        offset = (pagina - 1) * tamanho_pagina
        match (ordem):
            case 1: SQL_OBTER_BUSCA_ORDENADA = SQL_OBTER_BUSCA.replace("#1", "nome")
            # case 2: SQL_OBTER_BUSCA_ORDENADA = SQL_OBTER_BUSCA.replace("#1", "preco ASC")
            # case 3: SQL_OBTER_BUSCA_ORDENADA = SQL_OBTER_BUSCA.replace("#1", "preco DESC")
            case _: SQL_OBTER_BUSCA_ORDENADA = SQL_OBTER_BUSCA.replace("#1", "nome")
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_BUSCA_ORDENADA, (termo, termo, tamanho_pagina, offset)).fetchall()
                livros = [Livro(*t) for t in tuplas]
                return livros
        except sqlite3.Error as ex:
            print(ex)
            return None
        
    @classmethod
    def obter_quantidade_busca(cls, termo: str) -> Optional[int]:
        termo = "%"+termo+"%"
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_QUANTIDADE_BUSCA, (termo, termo)).fetchone()
                return int(tupla[0])
        except sqlite3.Error as ex:
            print(ex)
            return None