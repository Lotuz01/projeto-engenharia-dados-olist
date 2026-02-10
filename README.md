# de-olist-warehouse

Repositório de portfólio para Engenharia de Dados utilizando o dataset do Olist. O projeto foca em uma arquitetura local-first utilizando Python, SQL (PostgreSQL) e Docker.

## Arquitetura
A estrutura segue o padrão de medalhão simplificado:
- **Raw**: Dados brutos importados dos CSVs.
- **Staging (stg)**: Limpeza, tipagem e padronização.
- **Marts**: Tabelas de fato e dimensões otimizadas para análise.

## Métricas e KPIs
- **Lead Time (Days)**: Calculado como a diferença em dias entre a data de compra (`order_purchase_timestamp`) e a data de entrega efetiva (`order_delivered_customer_date`).
- **Is Late**: Flag binário que indica se a entrega foi realizada após a data estimada (`order_estimated_delivery_date`).
- **Taxa de Atraso**: Proporção de pedidos atrasados em relação ao total.
- **Frete Médio**: Custo médio de transporte por região ou vendedor.

## Como rodar do zero

### 1. Pré-requisitos
- Docker e Docker Compose
- Python 3.10+
- Dataset do Olist (arquivos CSV) colocados em `data/olist/`

### 2. Configuração inicial
```powershell
# Instalar dependências (Windows)
pip install -r requirements.txt
copy .env.example .env

# Subir o banco de dados Postgres (Certifique-se que o Docker Desktop está aberto)
docker compose up -d
```

### 3. Execução do Pipeline
Se você não tiver o comando `make` instalado, utilize o script Python:
```powershell
# Executa todo o processo (Init + Load + Build + Export)
python run_all.py
```

Ou execute os passos individualmente via CLI:
```powershell
# Inicializar schemas e tabelas
python src/cli.py init

# Carregar dados brutos
python src/cli.py load-raw

# Executar transformações (Staging e Marts)
python src/cli.py build

# Exportar relatórios de KPIs
python src/cli.py export
```

### 4. Testes
Para garantir a qualidade dos dados:
```powershell
pytest tests/
```

## Estrutura do Projeto
- `sql/`: Scripts de definição e transformação SQL.
- `src/`: Código Python da CLI de orquestração.
- `data/`: Local para armazenar os CSVs do dataset.
- `tests/`: Testes de qualidade de dados.
- `reports/`: Saída dos KPIs exportados em CSV.
#
