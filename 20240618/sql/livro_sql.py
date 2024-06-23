SQL_CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS livro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        autor TEXT NOT NULL,
        descricao TEXT NOT NULL,
        isbn TEXT NOT NULL)
"""

SQL_INSERIR = """
    INSERT INTO livro(nome, autor, descricao, isbn)
    VALUES (?, ?, ?, ?)
"""

SQL_OBTER_TODOS = """
    SELECT id, nome, autor, descricao, isbn
    FROM livro
    ORDER BY nome
"""

SQL_ALTERAR = """
    UPDATE livro
    SET nome=?, autor=?, descricao=?, isbn=?
    WHERE id=?
"""


SQL_EXCLUIR = """
    DELETE FROM livro  
    WHERE id=?
"""

SQL_OBTER_UM = """
    SELECT id, nome, autor, descricao, isbn
    FROM livro
    WHERE id=?
"""


SQL_OBTER_QUANTIDADE = """
    SELECT COUNT(*) FROM livro
"""

SQL_OBTER_BUSCA = """
    SELECT id, nome, autor, descricao, isbn
    FROM livro
    WHERE nome LIKE ? OR autor LIKE ?
    ORDER BY nome
    LIMIT ? OFFSET ?
"""

SQL_OBTER_QUANTIDADE_BUSCA = """
    SELECT COUNT(*) FROM livro
    WHERE nome LIKE ? OR autor LIKE ?
"""


