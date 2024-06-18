import json
import sqlite3
from typing import List, Optional
from models.cliente_model import Cliente
from models.bibliotecario_model import Bibliotecario

from sql.cliente_sql import *
from util.database import obter_conexao


class BibliotecarioRepo:

    @classmethod
    def criar_tabela(cls):
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(SQL_CRIAR_TABELA)

    @classmethod
    def inserir(blo, bibliotecario: Bibliotecario) -> Optional[Bibliotecario]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    SQL_INSERIR,
                    (
                        bibliotecario.nome,
                        bibliotecario.cpf,
                        bibliotecario.data_nascimento,
                        bibliotecario.endereco,
                        bibliotecario.telefone,
                        bibliotecario.email,
                        bibliotecario.senha,
                        bibliotecario.admin,
                    ),
                )
                if cursor.rowcount > 0:
                    bibliotecario.id = cursor.lastrowid
                    return bibliotecario
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def obter_todos(blo) -> List[Bibliotecario]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_TODOS).fetchall()
                bibliotecarios = [Bibliotecario(*t) for t in tuplas]
                return bibliotecarios
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def alterar(blo, bibliotecario: Bibliotecario) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    SQL_ALTERAR,
                    (
                        bibliotecario.nome,
                        bibliotecario.cpf,
                        bibliotecario.data_nascimento,
                        bibliotecario.endereco,
                        bibliotecario.email,
                        bibliotecario.telefone,
                        bibliotecario.id,
                    ),
                )
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False

    @classmethod
    def excluir(blo, id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_EXCLUIR, (id,))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False

    @classmethod
    def obter_um(blo, id: int) -> Optional[Bibliotecario]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_UM, (id,)).fetchone()
                bibliotecario = Bibliotecario(*tupla)
                return bibliotecario
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def obter_quantidade(blo) -> Optional[int]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_QUANTIDADE).fetchone()
                return int(tupla[0])
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def inserir_bibliotecarios_json(blo, arquivo_json: str):
        if BibliotecarioRepo.obter_quantidade() == 0:
            with open(arquivo_json, "r", encoding="utf-8") as arquivo:
                bibliotecarios = json.load(arquivo)
                for bibliotecario in bibliotecarios:
                    BibliotecarioRepo.inserir(Bibliotecario(**bibliotecario))

    @classmethod
    def obter_busca(blo, termo: str, pagina: int, tamanho_pagina: int) -> List[Bibliotecario]:
        termo = "%" + termo + "%"
        offset = (pagina - 1) * tamanho_pagina
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(
                    SQL_OBTER_BUSCA, (termo, termo, tamanho_pagina, offset)
                ).fetchall()
                bibliotecarios = [Bibliotecario(*t) for t in tuplas]
                return bibliotecarios
        except sqlite3.Error as ex:
            print(ex)
            return None
    
    @classmethod
    def obter_quantidade_busca(blo, termo: str) -> Optional[int]:
        termo = "%" + termo + "%"
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(
                    SQL_OBTER_QUANTIDADE_BUSCA, (termo, termo)
                ).fetchone()
                return int(tupla[0])
        except sqlite3.Error as ex:
            print(ex)
            return None
    
    @classmethod
    def tornar_admin(blo, id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_TORNAR_ADMIN, (id,))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False
    
    @classmethod
    def revogar_admin(blo, id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_REVOGAR_ADMIN, (id,))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False
    
    @classmethod
    def obter_por_email(blo, email: str) -> Optional[Bibliotecario]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_POR_EMAIL, (email,)).fetchone()
                if tupla:
                    bibliotecario = Bibliotecario(*tupla)
                    return bibliotecario
                else:
                    return None
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def alterar_token(blo, id: int, token: str) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_ALTERAR_TOKEN, (token, id))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False

    @classmethod
    def obter_por_token(blo, token: str) -> Optional[Bibliotecario]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_POR_TOKEN, (token,)).fetchone()
                if tupla:
                    bibliotecario = Bibliotecario(*tupla)
                    return bibliotecario
                else:
                    return None
        except sqlite3.Error as ex:
            print(ex)
            return None



    # @classmethod
    # def obter_todos(cls) -> List[Cliente]:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tuplas = cursor.execute(SQL_OBTER_TODOS).fetchall()
    #             clientes = [Cliente(*t) for t in tuplas]
    #             return clientes
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None

    # @classmethod
    # def alterar(cls, cliente: Cliente) -> bool:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             cursor.execute(
    #                 SQL_ALTERAR,
    #                 (
    #                     cliente.nome,
    #                     cliente.cpf,
    #                     cliente.data_nascimento,
    #                     cliente.endereco,
    #                     cliente.email,
    #                     cliente.telefone,
    #                     cliente.id,
    #                 ),
    #             )
    #             return cursor.rowcount > 0
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return False

    # @classmethod
    # def excluir(cls, id: int) -> bool:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             cursor.execute(SQL_EXCLUIR, (id,))
    #             return cursor.rowcount > 0
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return False

    # @classmethod
    # def obter_um(cls, id: int) -> Optional[Cliente]:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tupla = cursor.execute(SQL_OBTER_UM, (id,)).fetchone()
    #             cliente = Cliente(*tupla)
    #             return cliente
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None

    # @classmethod
    # def obter_quantidade(cls) -> Optional[int]:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tupla = cursor.execute(SQL_OBTER_QUANTIDADE).fetchone()
    #             return int(tupla[0])
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None

    # @classmethod
    # def inserir_clientes_json(cls, arquivo_json: str):
    #     if ClienteRepo.obter_quantidade() == 0:
    #         with open(arquivo_json, "r", encoding="utf-8") as arquivo:
    #             clientes = json.load(arquivo)
    #             for cliente in clientes:
    #                 ClienteRepo.inserir(Cliente(**cliente))

    # @classmethod
    # def obter_busca(cls, termo: str, pagina: int, tamanho_pagina: int) -> List[Cliente]:
    #     termo = "%" + termo + "%"
    #     offset = (pagina - 1) * tamanho_pagina
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tuplas = cursor.execute(
    #                 SQL_OBTER_BUSCA, (termo, termo, tamanho_pagina, offset)
    #             ).fetchall()
    #             clientes = [Cliente(*t) for t in tuplas]
    #             return clientes
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None

    # @classmethod
    # def obter_quantidade_busca(cls, termo: str) -> Optional[int]:
    #     termo = "%" + termo + "%"
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tupla = cursor.execute(
    #                 SQL_OBTER_QUANTIDADE_BUSCA, (termo, termo)
    #             ).fetchone()
    #             return int(tupla[0])
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None

    # @classmethod
    # def tornar_admin(cls, id: int) -> bool:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             cursor.execute(SQL_TORNAR_ADMIN, (id,))
    #             return cursor.rowcount > 0
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return False

    # @classmethod
    # def revogar_admin(cls, id: int) -> bool:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             cursor.execute(SQL_REVOGAR_ADMIN, (id,))
    #             return cursor.rowcount > 0
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return False

    # @classmethod
    # def obter_por_email(cls, email: str) -> Optional[Cliente]:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tupla = cursor.execute(SQL_OBTER_POR_EMAIL, (email,)).fetchone()
    #             if tupla:
    #                 cliente = Cliente(*tupla)
    #                 return cliente
    #             else:
    #                 return None
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None

    # @classmethod
    # def alterar_token(cls, id: int, token: str) -> bool:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             cursor.execute(SQL_ALTERAR_TOKEN, (token, id))
    #             return cursor.rowcount > 0
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return False

    # @classmethod
    # def obter_por_token(cls, token: str) -> Optional[Cliente]:
    #     try:
    #         with obter_conexao() as conexao:
    #             cursor = conexao.cursor()
    #             tupla = cursor.execute(SQL_OBTER_POR_TOKEN, (token,)).fetchone()
    #             if tupla:
    #                 cliente = Cliente(*tupla)
    #                 return cliente
    #             else:
    #                 return None
    #     except sqlite3.Error as ex:
    #         print(ex)
    #         return None


