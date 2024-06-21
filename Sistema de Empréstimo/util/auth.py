import secrets
from typing import Optional
import bcrypt
from fastapi import HTTPException, Request, status
from models.cliente_model import Cliente
from models.bibliotecario_model import Bibliotecario

from repositories.cliente_repo import ClienteRepo
from repositories.bibliotecario_repo import BibliotecarioRepo

async def obter_bibliotecario_logado(request: Request) -> Optional[Bibliotecario]:
    try:
        token = request.cookies["auth_token"]
        if token.strip() == "":
            return None
        bibliotecario = BibliotecarioRepo.obter_por_token(token)
        return bibliotecario
    except KeyError:
        return None



async def obter_cliente_logado(request: Request) -> Optional[Cliente]:
    try:
        token = request.cookies["auth_token"]
        if token.strip() == "":
            return None
        cliente = ClienteRepo.obter_por_token(token)
        return cliente
    except KeyError:
        return None

async def atualizar_cookie_autenticacao(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == status.HTTP_303_SEE_OTHER:
        return response
    bibliotecario = await obter_bibliotecario_logado(request)
    if bibliotecario:
        token = request.cookies["auth_token"]
        response.set_cookie(
            key="auth_token",
            value=token,
            max_age=1800,
            httponly=True,
            samesite="lax",
        )
    return response


async def atualizar_cookie_autenticacao(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == status.HTTP_303_SEE_OTHER:
        return response
    cliente = await obter_cliente_logado(request)
    if cliente:
        token = request.cookies["auth_token"]
        response.set_cookie(
            key="auth_token",
            value=token,
            max_age=1800,
            httponly=True,
            samesite="lax",
        )
    return response

def obter_hash_senha(senha: str) -> str:
    try:
        hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
        return hashed.decode()
    except ValueError:
        return ""


def obter_hash_senha(senha: str) -> str:
    try:
        hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
        return hashed.decode()
    except ValueError:
        return ""


def conferir_senha(senha: str, hash_senha: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_senha.encode())
    except ValueError:
        return False

def conferir_senha(senha: str, hash_senha: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_senha.encode())
    except ValueError:
        return False

def gerar_token(length: int = 32) -> str:
    try:
        return secrets.token_hex(length)
    except ValueError:
        return ""


def gerar_token(length: int = 32) -> str:
    try:
        return secrets.token_hex(length)
    except ValueError:
        return ""


def checar_autorizacao(bibliotecario_logado: Bibliotecario):
    if not bibliotecario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)



def checar_autorizacao(cliente_logado: Cliente):
    if not cliente_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


