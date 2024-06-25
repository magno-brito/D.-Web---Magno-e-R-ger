import math
import os


from sqlite3 import DatabaseError
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError  # Add this import
from fastapi import Form


from dtos.entrar_dto import EntrarDTO
from ler_html import ler_html
from dtos.novo_cliente_dto import NovoClienteDTO
from dtos.livro_dto import LivroDTO
from models.cliente_model import Cliente
from models.livro_model import Livro

from repositories.cliente_repo import ClienteRepo
from repositories.livro_repo import LivroRepo
from repositories.produto_repo import ProdutoRepo
from util.auth import (
    conferir_senha,
    gerar_token,
    obter_hash_senha,
)

from util.cookies import adicionar_cookie_auth, adicionar_mensagem_sucesso
from util.pydantic import create_validation_errors

router = APIRouter()

templates = Jinja2Templates(directory="templates")

###################### Upload da imagem

UPLOAD_FOLDER = os.path.abspath('static/img/livros') 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(file: UploadFile, isbn: str) -> str:
    """Salva o arquivo enviado na pasta static/img/livros com um nome baseado no ISBN"""
    filename = f"{isbn}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return filename


######################

@router.get("/html/{arquivo}")
async def get_html(arquivo: str):
    response = HTMLResponse(ler_html(arquivo))
    return response


# @router.get("/")
# async def get_root(request: Request):
#     produtos = ProdutoRepo.obter_todos()
#     return templates.TemplateResponse(
#         "index.html",
#         {"request": request, "produtos": produtos},
#     )

@router.get("/")
async def get_root(request: Request):
    livros = LivroRepo.obter_todos()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "livros": livros},
    )


@router.get("/contato")
async def get_contato(request: Request):
    return templates.TemplateResponse(
        "contato.html",
        {"request": request},
    )


@router.get("/cadastro")
async def get_cadastro(request: Request):
    return templates.TemplateResponse(
        "cadastro.html",
        {"request": request},
    )

@router.get("/cadastrar_livro")
async def get_cadastro_livro(request: Request):
    return templates.TemplateResponse(
        "cadastrar_livro.html",
        {"request": request},
    )

# @router.post("/cadastrar_livro", response_class=JSONResponse)
# async def post_cadastrar_livro(livro: Livro):
#     livro_cadastrado = LivroRepo.inserir(livro)
#     if not livro_alterado or not livro_alterado.id:
#         raise HTTPException(status_code=400, detail="Erro ao alterar livro.")
#     return {"redirect": {"url": "/cadastro_realizado"}}


@router.post("/cadastrar_livro")
async def post_cadastrar_livro(livro: Livro, imagem: UploadFile = File(...)):
    try:
        
        livro_cadastrado = LivroRepo.inserir(livro)
        if not livro_cadastrado or not livro_cadastrado.id:
            raise HTTPException(status_code=400, detail="Erro ao cadastrar livro.")
        
        with open(f"static/img/livros/{livro_cadastrado.id}.png", "wb") as f:
            f.write(await imagem.read())
        return {"redirect": {"url": "/cadastro_livro_realizado"}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar livro: {str(e)}")

    # try:
       
    #     livro_cadastrado = LivroRepo.inserir(livro)
    #     if not livro_cadastrado or not livro_cadastrado.id:
    #         raise HTTPException(status_code=400, detail="Erro ao cadastrar livro.")
    #     return {"redirect": {"url": "/cadastro_livro_realizado"}}
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Erro ao cadastrar livro: {str(e)}")



@router.get("/alterar_livro")
async def get_alterar_livro(request: Request):
    return templates.TemplateResponse(
        "alterar_livro.html",
        {"request": request},
    )

@router.post("/alterar_livro", response_class=JSONResponse)
async def post_alterar_livro(livro: Livro):
    livro_alterado = LivroRepo.alterar(livro)
    if not livro_alterado or not livro_alterado.id:
        raise HTTPException(status_code=400, detail="Erro ao alterar livro.")
    return {"redirect": {"url": "/cadastro_realizado"}}



@router.get("/excluir_livro")
async def get_excluir_livro(request: Request):
    return templates.TemplateResponse(
        "excluir_livro.html",
        {"request": request},
    )



@router.post("/post_cadastro", response_class=JSONResponse)
async def post_cadastro(cliente_dto: NovoClienteDTO):
    # Remover campo `confirmacao_senha` antes de inserir no banco de dados
    cliente_data = cliente_dto.model_dump(exclude={"confirmacao_senha"})
    cliente_data["senha"] = obter_hash_senha(cliente_data["senha"])
    novo_cliente = ClienteRepo.inserir(Cliente(**cliente_data))
    if not novo_cliente or not novo_cliente.id:
        raise HTTPException(status_code=400, detail="Erro ao cadastrar cliente.")
    return {"redirect": {"url": "/cadastro_realizado"}}



@router.get("/cadastro_realizado")
async def get_cadastro_realizado(request: Request):
    return templates.TemplateResponse(
        "cadastro_confirmado.html",
        {"request": request},
    )

@router.get("/cadastro_livro_realizado")
async def get_cadastro_realizado(request: Request):
    return templates.TemplateResponse(
        "cadastro_livro_confirmado.html",
        {"request": request},
    )



@router.get("/entrar")
async def get_entrar(
    request: Request,
    return_url: str = Query("/"),
):
    return templates.TemplateResponse(
        "entrar.html",
        {"request": request, "return_url": return_url},
    )


@router.post("/post_entrar", response_class=JSONResponse)
async def post_entrar(entrar_dto: EntrarDTO):
    cliente_entrou = ClienteRepo.obter_por_email(entrar_dto.email)
    if (
        (not cliente_entrou)
        or (not cliente_entrou.senha)
        or (not conferir_senha(entrar_dto.senha, cliente_entrou.senha))
    ):
        return JSONResponse(
            content=create_validation_errors(
                entrar_dto,
                ["email", "senha"],
                ["Credenciais inválidas.", "Credenciais inválidas."],
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    print(f"Cliente Admin Status in post_entrar: {cliente_entrou.admin}")
    print(f"Cliente Object: {cliente_entrou}")


    token = gerar_token()
    if not ClienteRepo.alterar_token(cliente_entrou.id, token):
        raise DatabaseError(
            "Não foi possível alterar o token do cliente no banco de dados."
        )
    response = JSONResponse(content={"redirect": {"url": entrar_dto.return_url}})
    adicionar_mensagem_sucesso(
        response,
        f"Olá, <b>{cliente_entrou.nome}</b>. Seja bem-vindo(a) à Loja Virtual!",
    )
    adicionar_cookie_auth(response, token)
    return response


@router.get("/produto/{id:int}")
async def get_produto(request: Request, id: int):
    produto = ProdutoRepo.obter_um(id)
    return templates.TemplateResponse(
        "produto.html",
        {"request": request, "produto": produto},
    )


@router.get("/buscar")
async def get_buscar(
    request: Request,
    q: str,
    p: int = 1,
    tp: int = 6,
    o: int = 1,
):
    livros = LivroRepo.obter_busca(q, p, tp, o)
    qtde_livros = LivroRepo.obter_quantidade_busca(q)
    qtde_paginas = math.ceil(qtde_livros / float(tp))
    return templates.TemplateResponse(
        "buscar.html",
        {
            "request": request,
            "livros": livros,
            "quantidade_paginas": qtde_paginas,
            "tamanho_pagina": tp,
            "pagina_atual": p,
            "termo_busca": q,
            "ordem": o,
        },
    )


# @router.get("/buscar")
# async def get_buscar(
#     request: Request,
#     q: str,
#     p: int = 1,
#     tp: int = 6,
#     o: int = 1,
# ):
#     produtos = ProdutoRepo.obter_busca(q, p, tp, o)
#     qtde_produtos = ProdutoRepo.obter_quantidade_busca(q)
#     qtde_paginas = math.ceil(qtde_produtos / float(tp))
#     return templates.TemplateResponse(
#         "buscar.html",
#         {
#             "request": request,
#             "produtos": produtos,
#             "quantidade_paginas": qtde_paginas,
#             "tamanho_pagina": tp,
#             "pagina_atual": p,
#             "termo_busca": q,
#             "ordem": o,
#         },
#     )
