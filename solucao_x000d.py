#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução definitiva para o problema _x000D_ no Excel
"""

import re
import unicodedata

def limpar_texto_para_excel(texto):
    """
    Limpa texto para uso seguro no Excel, removendo caracteres problemáticos
    
    Esta função resolve especificamente o problema com _x000D_ e similares
    que causam erros na abertura de arquivos Excel.
    
    Args:
        texto (str): Texto a ser limpo
        
    Returns:
        str: Texto limpo e seguro para Excel
    """
    if not isinstance(texto, str):
        return str(texto)
    
    # 1. Remove _x000D_ e similares (representações hexadecimais de caracteres)
    # Este é o padrão que o Excel usa para representar caracteres especiais
    texto = re.sub(r'_x[0-9A-Fa-f]{4}_', '', texto)
    
    # 2. Remove caracteres de controle problemáticos
    # Mantém apenas caracteres imprimíveis e quebras de linha básicas
    texto = ''.join(char for char in texto if ord(char) >= 32 or char in '\t\n\r')
    
    # 3. Remove espaços extras no início e fim
    texto = texto.strip()
    
    # 4. Normaliza quebras de linha múltiplas
    texto = re.sub(r'\n+', '\n', texto)
    texto = re.sub(r'\r+', '\r', texto)
    
    # 5. Remove caracteres de controle invisíveis que podem causar problemas
    texto = ''.join(char for char in texto if unicodedata.category(char) not in ['Cc', 'Cf'])
    
    return texto

def limpar_texto_para_excel_alternativa(texto):
    """
    Alternativa mais agressiva para casos extremos
    """
    if not isinstance(texto, str):
        return str(texto)
    
    # Remove TODOS os padrões _xXXXX_
    texto = re.sub(r'_x[0-9A-Fa-f]{4}_', '', texto, flags=re.IGNORECASE)
    
    # Remove caracteres de controle (exceto espaços e quebras de linha)
    texto = ''.join(char for char in texto if char.isprintable() or char in '\t\n\r ')
    
    # Limpa espaços extras
    texto = ' '.join(texto.split())
    
    return texto

# Exemplo de uso prático
if __name__ == "__main__":
    # Teste com dados reais do seu problema
    dados_problema = [
        "JULIANA GJULIANA GJULIANA_x000D_",
        "CAROLINE CAROLINE CAROLINE_x000D_",
        "MARCELO MARCELO MARCELO_x000D_",
        "ANDREIA ANDREIA ANDREIA_x000D_",
        "CAMILA SI CAMILA SI CAMILA R_x000D_",
        "RENATA CORENATA C RENATA C_x000D_",
        "FABIANA FABIANA FABIANA F_x000D_",
        "LUIZ BRAG LUIZ BRAG LUIZ HENR_x000D_",
        "MARIA AN MARIA AN MARIA LU_x000D_",
        "STEPHANI STEPHANI STEPHANI_x000D_",
        "PAOLA LAL PAOLA LAI PAOLA DE_x000D_"
    ]
    
    print("=== ANTES DA LIMPEZA ===")
    for i, dado in enumerate(dados_problema, 1):
        print(f"{i:2d}. {repr(dado)}")
    
    print("\n=== DEPOIS DA LIMPEZA (Método Principal) ===")
    for i, dado in enumerate(dados_problema, 1):
        limpo = limpar_texto_para_excel(dado)
        print(f"{i:2d}. {repr(limpo)}")
    
    print("\n=== DEPOIS DA LIMPEZA (Método Alternativo) ===")
    for i, dado in enumerate(dados_problema, 1):
        limpo = limpar_texto_para_excel_alternativa(dado)
        print(f"{i:2d}. {repr(limpo)}")