import sqlite3

conn = sqlite3.connect("dados_de_voo.db")

cur  = conn.cursor()

cur.execute("""
CREATE TABLE registro_itinerarios (
  id_voo TEXT NOT NULL,
  id_passageiro TEXT NOT NULL,
  id_refeicao TEXT NOT NULL,
  FOREIGN KEY (id_voo) REFERENCES registro_voo (id_voo),
  FOREIGN KEY (id_passageiro) REFERENCES registro_passageiros (id_passageiro),
  FOREIGN KEY (id_refeicao) REFERENCES registro_refeicoes (id_refeicao)
)
""")

# Aqui, inseri no registro_itinerarios seguindo os seguintes passos:
# Primeiro, busquei as combinações entre voos, passageiros e refeições.
# Segundo, adicionei um filtro nas combinações para remover as indesejadas (restrições alimentares dos passageiros)
# Terceiro, inserção das combinações válidas na tabela registro_itinerarios.

print(cur.execute("select * from registro_passageiros").fetchall())
print(cur.execute("select * from registro_refeicoes").fetchall())
print(cur.execute("select * from restricao_alimentar").fetchall())
print(cur.execute("select * from registro_alergicos").fetchall())

cur.execute("""
INSERT INTO registro_itinerarios (id_voo, id_passageiro, id_refeicao)
SELECT
    r_v.id_voo,
    r_p.id_passageiro,
    r_r.id_refeicao
FROM registro_voo r_v
CROSS JOIN registro_passageiros r_p
CROSS JOIN registro_refeicoes r_r
LEFT JOIN restricao_alimentar r_a ON r_a.id_passageiro = r_p.id_passageiro
LEFT JOIN registro_alergicos r_al ON r_al.id_refeicao = r_r.id_refeicao
WHERE r_a.st_alergia_alimentar IS NULL
    AND r_al.st_alergico IS NULL
    AND r_al.st_alergico NOT IN (r_a.st_alergia_alimentar)
""")

cur.execute("ALTER TABLE registro_voo ADD COLUMN valor_total REAL")

print(cur.execute("select * from registro_passageiros").fetchall())

# Aqui, atualizei a registro_voo de acordo com o registro_itinerarios, atribuindo o valor de cada categoria pela coluna st_categoria
# e subtraindo o valor 300. Mas como não houve retorno que casava com o chaveamento

cur.execute("""
UPDATE registro_voo
SET valor_total = (
    SELECT 
        COALESCE(
            SUM(CASE
                WHEN r_p.st_categoria = 'Silver' THEN 550.6
                WHEN r_p.st_categoria = 'Bronze' THEN 450.7
                WHEN r_p.st_categoria = 'Gold' THEN 350.2
                ELSE 0
            END)
            - COALESCE((
                SELECT SUM(r_r.float_custo)
                FROM registro_itinerarios r_i
                JOIN registro_refeicoes r_r ON r_i.id_refeicao = r_r.id_refeicao
                WHERE r_i.id_voo = registro_voo.id_voo
            ), 0)
            - 300.0
        , 0)
    FROM registro_itinerarios r_i
    JOIN registro_passageiros r_p ON r_i.id_passageiro = r_p.id_passageiro
    WHERE r_i.id_voo = registro_voo.id_voo
)
""")

print(cur.execute("select * from registro_voo").fetchall())

cur.execute("""
SELECT
    id_voo,
    COALESCE(valor_total, 0)
FROM
    registro_voo
ORDER BY
    valor_total DESC
LIMIT 1
""")
voo_mais_rentavel = cur.fetchone()

print("Voo mais rentável:", voo_mais_rentavel)

# Não houve retorno de voo rentável pois não encontrei um chaveamento existente.

conn.commit()
conn.close()