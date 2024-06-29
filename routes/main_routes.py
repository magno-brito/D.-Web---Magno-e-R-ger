import math
import os


from sqlite3 import DatabaseError
from fastapi import APIRouter,Form, Depends, UploadFile, File, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from models.emprestimo_model import Emprestimo
from repositories.emprestimo_repo import EmprestimoRepo
from repositories.emprestimo_livro_repo import EmprestimoLivroRepo
from models.emprestimo_livro_model import EmprestimoLivro
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError  
from fastapi import Form


from dtos.entrar_dto import EntrarDTO
from ler_html import ler_html
from dtos.novo_cliente_dto import NovoClienteDTO
from dtos.livro_dto import LivroDTO
from models.cliente_model import Cliente
from models.emprestimo_model import Emprestimo
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



@router.get("/html/{arquivo}")
async def get_html(arquivo: str):
    response = HTMLResponse(ler_html(arquivo))
    return response


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

@router.post("/cadastrar_livro", response_class=JSONResponse)
async def post_cadastrar_livro(livro: Livro):
   
    livro_cadastrado = LivroRepo.inserir(livro)
    if not livro_cadastrado or not livro_cadastrado.id:
        raise HTTPException(status_code=400, detail="Erro ao alterar livro.")
    return {"redirect": {"url": "/cadastro_livro_realizado"}}


########################################
@router.get("/alterar_livro/{id}")
async def get_alterar_livro(request: Request, id: int):
    livro = LivroRepo.obter_um(id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
   

    return templates.TemplateResponse(
        "alterar_livro.html",
        {"request": request, "livro": livro},
    )

@router.post("/alterar_livro", response_class=JSONResponse)
async def post_alterar_livro(livro: Livro):
    livro_alterado = LivroRepo.alterar(livro)
    if not livro_alterado or not livro_alterado.id:
        raise HTTPException(status_code=400, detail="Erro ao alterar livro.")
    return {"redirect": {"url": "/alterar_livro_realizado"}}



@router.get("/excluir_livro/{id}")
async def get_excluir_livro(request: Request, id: int):
    livro = LivroRepo.obter_um(id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return templates.TemplateResponse(
        "excluir_livro.html",
        {"request": request, "livro": livro},
    )

@router.post("/excluir_livro", response_class=JSONResponse)
async def post_excluir_livro(livro: Livro):
    print("ISBN>>>>" + livro.isbn)
    livro_excluido = LivroRepo.excluir(livro.id)
    print(livro_excluido)
    if not livro_excluido :
        raise HTTPException(status_code=400, detail="Erro ao excluir livro.")
    return {"redirect": {"url": "/excluir_livro_realizado"}}



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

@router.get("/alterar_livro_realizado")
async def get_alterar_realizado(request: Request):
    return templates.TemplateResponse(
        "alterar_livro_confirmado.html",
        {"request": request},
    )

@router.get("/excluir_livro_realizado")
async def get_excluir_realizado(request: Request):
    return templates.TemplateResponse(
        "excluir_livro_confirmado.html",
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
    print(f'TESTE----------->{livros}')
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


#################################################################
# Empréstimo

@router.get("/emprestar")
async def get_emprestar(request: Request):
    lista_clientes = ClienteRepo.obter_todos()
    lista_livros = LivroRepo.obter_todos()
    return templates.TemplateResponse(
        "emprestar.html",
        {"request": request, "lista_clientes": lista_clientes, "lista_livros": lista_livros},
    )


@router.get("/emprestimos")
async def get_emprestimos(request: Request):
    lista_emprestimos = EmprestimoRepo.obter_todos()
    lista_livros = LivroRepo.obter_todos()
    lista_clientes = ClienteRepo.obter_todos()
    lista_emprestimos_livro = EmprestimoLivroRepo.obter_todos()
    
    lista_final = []

    for emprestimo in lista_emprestimos:
        cliente = ClienteRepo.obter_um(emprestimo.cliente_id)
        nome = cliente.nome
        print("----------> CLIENTE NOME", nome)
        livro_selecionado = None
        for elivro in lista_emprestimos_livro:
            if emprestimo.id == elivro.id:
                for livro in lista_livros:
                    if livro.id == elivro.emprestimo_id:
                        livro_selecionado = livro.nome
        lista_final.append([emprestimo.data_emprestimo,nome,livro_selecionado, emprestimo.id])
    
    print(lista_final)


    return templates.TemplateResponse(
        "emprestimos.html",
        {"request": request,
        "lista_final":lista_final
        },
    )


@router.get("/cadastro_emprestimo_realizado")
async def get_cadastro_realizado(request: Request):
    return templates.TemplateResponse(
        "cadastro_emprestimo_confirmado.html",
        {"request": request},
    )


@router.post("/cadastrar_emprestimo", response_class=JSONResponse)
async def post_cadastrar_emprestimo(emprestimo: Emprestimo):
    try:
        cliente = ClienteRepo.obter_um(emprestimo.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail=f"Cliente com ID {emprestimo.cliente_id} não encontrado.")
        
        #Deixe a classe Emprestimo com livro_id porque não encontrei outro jeito. O que de fato vai importar é a classe EmprestimoLivro. De lá que vem a relação de 1 para N
        livro = LivroRepo.obter_um(emprestimo.livro_id)
        if not livro:
            raise HTTPException(status_code=404, detail=f"Livro com ID {emprestimo.livro_id} não encontrado.")
        
      
        EmprestimoRepo.inserir(emprestimo)
        livro.emprestado = 1
        LivroRepo.alterar_emprestimo(livro)
        EmprestimoLivroRepo.inserir(emprestimo.id, livro.id)
        if LivroRepo.alterar_emprestimo(livro) is None:
            raise HTTPException(status_code=400, detail="Erro ao atualizar o status do livro.")
        
        return {"redirect": {"url": "/cadastro_emprestimo_realizado"}}    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/excluir_emprestimo/{id}")
async def get_excluir_emprestimo(request: Request, id: int):
    emprestimo = EmprestimoRepo.obter_um(id)
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    return templates.TemplateResponse(
        "excluir_emprestimo.html",
        {"request": request, "emprestimo": emprestimo},
    )




@router.post("/excluir_emprestimo", response_class=JSONResponse)
async def post_excluir_emprestimo(emprestimo: Emprestimo):
    try:
        
        emprestimo_livro = EmprestimoLivroRepo.obter_um(emprestimo.id)
        print("-------------->")
        print(emprestimo.id)
        livro = LivroRepo.obter_um(emprestimo_livro.emprestimo_id)
        livro.emprestado = False
        LivroRepo.alterar(livro)
        EmprestimoLivroRepo.excluir(emprestimo.id)
        emprestimo_excluido = EmprestimoRepo.excluir(emprestimo.id)
        print(EmprestimoLivroRepo.excluir(emprestimo.id))
        print("-------------->")

        

        if not emprestimo_excluido:
            raise HTTPException(status_code=400, detail="Erro ao excluir empréstimo.")
        return {"redirect": {"url": "/excluir_emprestimo_realizado"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/excluir_emprestimo_realizado")
async def get_excluir_realizado(request: Request):
    return templates.TemplateResponse(
        "emprestimo_excluido_realizado.html",
        {"request": request},
    )
