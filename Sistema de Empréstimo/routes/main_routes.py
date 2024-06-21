import math
from sqlite3 import DatabaseError
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from dtos.entrar_dto import EntrarDTO
from dtos.novo_cliente_dto import NovoClienteDTO
from ler_html import ler_html
from models.cliente_model import Clientelogado
from models.bibliotecario_model import Bibliotecario
from repositories.cliente_repo import ClienteRepo
from repositories.bibliotecario_repo import BibliotecarioRepo
from repositories.produto_repo import ProdutoRepo
from util.auth import conferir_senha, gerar_token, obter_bibliotecario_logado, obter_hash_senha
from util.cookies import adicionar_cookie_auth, adicionar_mensagem_sucesso
from util.pydantic import create_validation_errors

router = APIRouter()

templates = Jinja2Templates(directory = "templates")

@router.get("/html/{arquivo}")
def get_html(arquivo: str):
    response = HTMLResponse(ler_html(arquivo))
    return response

@router.get("/")
def get_root(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    produtos = ProdutoRepo.obter_todos()
    return templates.TemplateResponse("principal.html", {"request": request, "produtos": produtos, "bibliotecario": bibliotecario_logado})


@router.get("/livros")
def get_livros(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    produtos = ProdutoRepo.obter_todos()
    return templates.TemplateResponse("index.html", {"request": request, "produtos": produtos, "bibliotecario": bibliotecario_logado})

@router.get("/emprestimo")
def get_emprestimo(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    produtos = ProdutoRepo.obter_todos()
    return templates.TemplateResponse("emprestimo.html", {"request": request, "produtos": produtos, "bibliotecario": bibliotecario_logado})



# @router.get("/")
# def get_root(request: Request, cliente_logado: Cliente = Depends(obter_cliente_logado)):
#     produtos = ProdutoRepo.obter_todos()
#     return templates.TemplateResponse("index.html", {"request": request, "produtos": produtos, "cliente": cliente_logado})



@router.get("/contato")
def get_contato(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    return templates.TemplateResponse("contato.html", {"request": request, "bibliotecario": bibliotecario_logado})

@router.get("/cadastro")
def get_cadastro(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    return templates.TemplateResponse("cadastro.html", {"request": request, "bibliotecario": bibliotecario_logado})

@router.get("/entrar")
def get_entrar(request: Cliente,  cliente_logado_logado: Cliente = Depends(obter_cliente_logado)):
    return templates.TemplateResponse("entrar.html", {"request": request, "cliente": cliente_logado})

@router.get("/produto/{id:int}")
def get_produto(request: Request, id: int, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    produto = ProdutoRepo.obter_um(id)
    return templates.TemplateResponse("produto.html", {"request": request, "produto": produto, "bibliotecario": bibliotecario_logado})

@router.get("/buscar")
def get_root(request: Request, q: str, p: int=1, tp: int=6, o: int=1, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    produtos = ProdutoRepo.obter_busca(q, p, tp, o)
    qtde_produtos = ProdutoRepo.obter_quantidade_busca(q)
    qtde_paginas = math.ceil(qtde_produtos / float(tp))
    
    return templates.TemplateResponse(
        "buscar.html", 
        {
            "request": request, 
            "produtos": produtos, 
            "qtde_paginas": qtde_paginas,
            "termo_busca": q, 
            "tamanho_pagina": tp,
            "pagina_atual": p,
            "ordem": o,
            "bibliotecario": bibliotecario_logado
        }
    )

@router.get("/cadastro")
def get_cadastro(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    return templates.TemplateResponse(
        "cadastro.html",
        {
            "request": request,
            "bibliotecario": bibliotecario_logado
        },
    )


@router.post("/post_cadastro", response_class=JSONResponse)
async def post_cadastro(bibliotecario: NovoClienteDTO):
    # Remover campo confirmacao_senha antes de inserir no banco de dados
    bibliotecario_data = bibliotecario.model_dump(exclude={"confirmacao_senha"})
    bibliotecario_data["senha"] = obter_hash_senha(bibliotecario_data["senha"])
    novo_bibliotecario = BibliotecarioRepo.inserir(Bibliotecario(**bibliotecario_data))
    if not novo_bibliotecario or not novo_bibliotecario.id:
        raise HTTPException(status_code=400, detail="Erro ao cadastrar bibliotecario.")
    return {"redirect": {"url": "/cadastro_realizado"}}


@router.get("/cadastro_realizado")
def get_cadastro_realizado(request: Request, bibliotecario_logado: Bibliotecario = Depends(obter_bibliotecario_logado)):
    return templates.TemplateResponse(
        "cadastro_confirmado.html",
        {
            "request": request,
            "bibliotecario": bibliotecario_logado
        },
    )

@router.post("/post_entrar", response_class=JSONResponse)
async def post_entrar(entrar_dto: EntrarDTO, return_url: str = Query("/")):
    bibliotecario_entrou = BibliotecarioRepo.obter_por_email(entrar_dto.email)
    if (
        (not bibliotecario_entrou)
        or (not bibliotecario_entrou.senha)
        or (not conferir_senha(entrar_dto.senha, bibliotecario_entrou.senha))
    ):
        return JSONResponse(
            content=create_validation_errors(
                entrar_dto,
                ["email", "senha"],
                ["Credenciais inválidas.", "Credenciais inválidas."],
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    token = gerar_token()
    if not BibliotecarioRepo.alterar_token(bibliotecario_entrou.id, token):
        raise DatabaseError(
            "Não foi possível alterar o token do bibliotecario no banco de dados."
        )
    response = JSONResponse(content={"redirect": {"url": return_url}})
    adicionar_mensagem_sucesso(response, "Entrada efetuada com sucesso.")
    adicionar_cookie_auth(response, token)
    return response