SQL_CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS emprestimo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    data_emprestimo DATE NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente (id)
)
"""

SQL_INSERIR = """
INSERT INTO emprestimo(cliente_id, data_emprestimo)
VALUES (?, ?)
"""

SQL_OBTER_QUANTIDADE = """
SELECT COUNT(*) FROM emprestimo
"""

SQL_OBTER_TODOS = """   
SELECT id, cliente_id, data_emprestimo 
FROM emprestimo
ORDER BY id

"""

SQL_OBTER_UM = """
    SELECT id, cliente_id, data_emprestimo
    FROM emprestimo
    WHERE id=?
"""

SQL_EXCLUIR = """
    DELETE FROM emprestimo
    WHERE id=?

"""