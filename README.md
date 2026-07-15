# 📊 Análise de Despesas Corporativas — Projeto de Portfólio

Projeto de demonstração técnica com **dados 100% fictícios**, criado para praticar
e mostrar habilidades em Python, análise de dados e desenvolvimento de aplicações web.

> Nota: nenhum dado real de empresa é usado aqui. Todos os valores, países,
> centros de custo e transações são gerados sinteticamente com a biblioteca
> [Faker](https://faker.readthedocs.io/).

## O que este projeto demonstra

- **Python + pandas**: geração, limpeza e agregação de dados
- **Streamlit**: construção de dashboard web interativo, sem precisar de HTML/CSS/JS
- **Boas práticas de código**: funções pequenas e nomeadas, cache de dados,
  reprodutibilidade (seed fixa no gerador)
- **Deploy gratuito**: publicado via Streamlit Community Cloud

## Como rodar localmente

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU-USUARIO/leonardo-portfolio.git
cd leonardo-portfolio

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Gerar os dados fictícios
python scripts/generate_data.py

# 4. Rodar o app
streamlit run app/app.py
```

## Estrutura do projeto

```
leonardo-portfolio/
├── app/
│   └── app.py              # Dashboard Streamlit
├── data/
│   └── financeiro_ficticio.csv  # Gerado pelo script (não commitado)
├── scripts/
│   └── generate_data.py    # Gerador de dados sintéticos
├── requirements.txt
└── README.md
```

## Sobre mim

Leonardo de Andrade — atuo na área de melhoria de processos e automação (Alteryx,
Power BI, Python) suportando o time de Finanças na América Latina.
[LinkedIn](#) | [GitHub](#)
