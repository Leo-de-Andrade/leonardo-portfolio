"""
Gerador de dados fictícios para o projeto de portfólio.

Por que gerar dados sintéticos em vez de baixar um dataset pronto do Kaggle?
1. Você controla exatamente o formato (parecido com o que você vê no trabalho: 
   centro de custo, país, categoria de despesa, mês).
2. Você pratica pandas + Faker, que são ferramentas do dia a dia de quem trabalha
   com dados em Python.
3. Zero risco de compliance -- 100% inventado, nenhuma relação com dados reais.

Rode assim: python scripts/generate_data.py
Isso vai criar data/financeiro_ficticio.csv
"""

import pandas as pd
from faker import Faker
import random
from datetime import date

fake = Faker("pt_BR")
random.seed(42)  # reprodutibilidade: sempre gera os mesmos dados fictícios

PAISES = ["Brasil", "Argentina", "Chile", "Colômbia", "México", "Peru"]
CATEGORIAS = ["Viagens", "TI", "Marketing", "Consultoria", "Treinamento", "Infraestrutura"]
CENTROS_CUSTO = [f"CC-{i:03d}" for i in range(1, 16)]

def gerar_linha(id_transacao: int) -> dict:
    """Gera uma linha fictícia de transação financeira."""
    pais = random.choice(PAISES)
    categoria = random.choice(CATEGORIAS)
    # Valores com alguma lógica: TI e Infraestrutura tendem a ser mais caros
    base = 15000 if categoria in ["TI", "Infraestrutura"] else 4000
    valor = round(random.uniform(base * 0.3, base * 2.5), 2)

    return {
        "id": id_transacao,
        "data": fake.date_between(start_date=date(2024, 1, 1), end_date=date(2025, 12, 31)),
        "pais": pais,
        "centro_custo": random.choice(CENTROS_CUSTO),
        "categoria": categoria,
        "descricao": fake.bs().capitalize(),
        "valor_usd": valor,
        "aprovado": random.choice([True, True, True, False]),  # ~75% aprovado
    }

def main(n_linhas: int = 2500):
    dados = [gerar_linha(i) for i in range(1, n_linhas + 1)]
    df = pd.DataFrame(dados)
    df = df.sort_values("data").reset_index(drop=True)

    caminho_saida = "data/financeiro_ficticio.csv"
    df.to_csv(caminho_saida, index=False)
    print(f"Gerado {len(df)} registros fictícios em {caminho_saida}")
    print(df.head())

if __name__ == "__main__":
    main()
