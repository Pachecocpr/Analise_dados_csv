import pandas as pd
import numpy as np
from pathlib import Path

class AnalisadorCSV:
    """Classe para análise de arquivos CSV"""
    
    def __init__(self, arquivo_csv):
        """
        Inicializa o analisador com um arquivo CSV
        
        Args:
            arquivo_csv (str): Caminho do arquivo CSV
        """
        self.arquivo = arquivo_csv
        self.dados = None
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega os dados do arquivo CSV"""
        try:
            self.dados = pd.read_csv(self.arquivo)
            print(f"✓ Arquivo '{self.arquivo}' carregado com sucesso!")
            print(f"  Dimensões: {self.dados.shape[0]} linhas × {self.dados.shape[1]} colunas\n")
        except FileNotFoundError:
            print(f"✗ Erro: Arquivo '{self.arquivo}' não encontrado!")
            return False
        except Exception as e:
            print(f"✗ Erro ao carregar arquivo: {e}")
            return False
        return True
    
    def info_basica(self):
        """Exibe informações básicas dos dados"""
        if self.dados is None:
            print("Nenhum dado carregado!")
            return
        
        print("=" * 50)
        print("INFORMAÇÕES BÁSICAS")
        print("=" * 50)
        print(self.dados.info())
        print("\n")
    
    def primeiras_linhas(self, n=5):
        """Exibe as primeiras N linhas"""
        if self.dados is None:
            print("Nenhum dado carregado!")
            return
        
        print("=" * 50)
        print(f"PRIMEIRAS {n} LINHAS")
        print("=" * 50)
        print(self.dados.head(n))
        print("\n")
    
    def estatisticas(self):
        """Exibe estatísticas descritivas"""
        if self.dados is None:
            print("Nenhum dado carregado!")
            return
        
        print("=" * 50)
        print("ESTATÍSTICAS DESCRITIVAS")
        print("=" * 50)
        print(self.dados.describe())
        print("\n")
    
    def valores_faltantes(self):
        """Identifica e exibe valores faltantes"""
        if self.dados is None:
            print("Nenhum dado carregado!")
            return
        
        print("=" * 50)
        print("VALORES FALTANTES")
        print("=" * 50)
        faltantes = self.dados.isnull().sum()
        print(faltantes[faltantes > 0] if faltantes.sum() > 0 else "Nenhum valor faltante encontrado!")
        print("\n")
    
    def analise_completa(self):
        """Executa uma análise completa dos dados"""
        self.info_basica()
        self.primeiras_linhas()
        self.estatisticas()
        self.valores_faltantes()


def main():
    """Função principal"""
    # Exemplo de uso
    arquivo = "dados.csv"  # Substitua pelo nome do seu arquivo
    
    if Path(arquivo).exists():
        analisador = AnalisadorCSV(arquivo)
        analisador.analise_completa()
    else:
        print(f"Arquivo '{arquivo}' não encontrado no diretório atual.")
        print("Certifique-se de que o arquivo CSV está no mesmo diretório que este script.")


if __name__ == "__main__":
    main()
