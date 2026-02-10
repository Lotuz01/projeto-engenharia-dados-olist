import subprocess
import sys
import os

def run_command(command):
    print(f"\n> Executando: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nErro ao executar comando: {e}")
        return False
    except FileNotFoundError:
        print(f"\nErro: Comando '{command[0]}' não encontrado.")
        return False

def main():
    print("=== Olist Warehouse Pipeline ===")
    
    # 1. Init
    if not run_command([sys.executable, "src/cli.py", "init"]):
        sys.exit(1)
        
    # 2. Load Raw
    if not run_command([sys.executable, "src/cli.py", "load-raw"]):
        sys.exit(1)
        
    # 3. Build
    if not run_command([sys.executable, "src/cli.py", "build"]):
        sys.exit(1)
        
    # 4. Export
    if not run_command([sys.executable, "src/cli.py", "export"]):
        sys.exit(1)
        
    print("\n=== Pipeline concluído com sucesso! ===")
    print("Os relatórios estão disponíveis na pasta 'reports/'.")

if __name__ == "__main__":
    main()
