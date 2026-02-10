import os
import csv
import psycopg
from dotenv import load_dotenv

def force_export():
    print("Iniciando exportação forçada...")
    load_dotenv()
    PG_URL = os.getenv("PG_URL")
    print(f"Usando URL: {PG_URL}")
    
    if not os.path.exists("reports"):
        print("Criando pasta reports...")
        os.makedirs("reports")
    else:
        print("Pasta reports já existe.")
        
    views = [
        "marts.kpi_delivery_performance_by_state",
        "marts.kpi_freight_by_state",
        "marts.kpi_freight_by_seller"
    ]
    
    try:
        print("Tentando conectar ao banco...")
        with psycopg.connect(PG_URL, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                for view in views:
                    print(f"Exportando {view}...")
                    cur.execute(f"SELECT * FROM {view}")
                    cols = [desc[0] for desc in cur.description]
                    rows = cur.fetchall()
                    filename = f"reports/{view.split('.')[1]}.csv"
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(cols)
                        writer.writerows(rows)
                    print(f"Salvo em {filename} com {len(rows)} linhas")
    except Exception as e:
        print(f"Erro durante a exportação: {e}")

if __name__ == '__main__':
    force_export()
