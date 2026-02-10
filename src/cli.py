import os
import csv
import click
from dotenv import load_dotenv
import psycopg

load_dotenv()

PG_URL = os.getenv("PG_URL")

def run_sql_file(file_path):
    try:
        with psycopg.connect(PG_URL, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
                    for stmt in statements:
                        cur.execute(stmt)
            conn.commit()
    except Exception as e:
        click.echo(f"Erro ao conectar ou executar SQL: {e}")
        raise

@click.group()
def cli():
    pass

@cli.command()
def init():
    """Cria schemas e tabelas raw."""
    click.echo("Inicializando schemas...")
    run_sql_file("sql/00_schemas.sql")
    click.echo("Criando tabelas raw...")
    run_sql_file("sql/01_raw_tables.sql")
    click.echo("Database inicializada com sucesso!")

@cli.command()
@click.option('--data-dir', default='data/olist', help='Diretório contendo os CSVs do Olist')
def load_raw(data_dir):
    """Carrega CSVs para as tabelas raw."""
    files = {
        'olist_orders_dataset.csv': 'raw.orders',
        'olist_order_items_dataset.csv': 'raw.order_items',
        'olist_customers_dataset.csv': 'raw.customers',
        'olist_sellers_dataset.csv': 'raw.sellers',
        'olist_geolocation_dataset.csv': 'raw.geolocation'
    }
    
    try:
        with psycopg.connect(PG_URL, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                for csv_file, table in files.items():
                    path = os.path.join(data_dir, csv_file)
                    if os.path.exists(path):
                        click.echo(f"Carregando {csv_file} para {table} via COPY...")
                        with open(path, 'r', encoding='utf-8') as f:
                            with cur.copy(f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)") as copy:
                                copy.write(f.read())
                    else:
                        click.echo(f"Aviso: Arquivo {path} não encontrado.")
            conn.commit()
    except Exception as e:
        click.echo(f"Erro ao carregar dados: {e}")
        raise

@cli.command()
def build():
    """Executa transformações de staging e marts."""
    click.echo("Executando staging...")
    run_sql_file("sql/10_staging.sql")
    click.echo("Executando marts...")
    run_sql_file("sql/20_marts.sql")
    click.echo("Executando KPIs...")
    run_sql_file("sql/30_kpis.sql")
    click.echo("Warehouse construído com sucesso!")

@cli.command()
def export():
    """Exporta KPIs para a pasta reports/."""
    views = [
        "marts.kpi_delivery_performance_by_state",
        "marts.kpi_freight_by_state",
        "marts.kpi_freight_by_seller"
    ]
    
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    try:
        with psycopg.connect(PG_URL, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                for view in views:
                    click.echo(f"Exportando {view}...")
                    cur.execute(f"SELECT * FROM {view}")
                    cols = [desc[0] for desc in cur.description]
                    rows = cur.fetchall()
                    filename = f"reports/{view.split('.')[1]}.csv"
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(cols)
                        writer.writerows(rows)
                    click.echo(f"Salvo em {filename}")
    except Exception as e:
        click.echo(f"Erro ao exportar KPIs: {e}")
        raise

if __name__ == '__main__':
    cli()
