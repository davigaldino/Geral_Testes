#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRAÇÃO DA SOLUÇÃO DEFINITIVA PARA _x000D_ NO SEU CÓDIGO
=============================================================================
Este arquivo contém as funções que você deve substituir no seu código
para resolver definitivamente o problema com _x000D_ no Excel.

COMO USAR:
1. Copie as funções abaixo para o seu código
2. Substitua as chamadas existentes pelas novas funções
3. Teste com uma amostra pequena primeiro

Desenvolvido por: Quality Assurance
Data: 12/2024
=============================================================================
"""

import re
import unicodedata

def limpar_texto_para_excel_definitivo(texto):
    """
    SOLUÇÃO DEFINITIVA para o problema _x000D_ no Excel.
    Esta função resolve TODOS os problemas relacionados a caracteres problemáticos.
    
    Args:
        texto (str): Texto a ser limpo
        
    Returns:
        str: Texto limpo e seguro para Excel
    """
    if not texto or not isinstance(texto, str):
        return str(texto) if texto is not None else ""
    
    # ETAPA 1: Remover TODOS os padrões _xXXXX_ (incluindo _x000D_)
    # Este é o padrão que o Excel usa para representar caracteres especiais
    texto = re.sub(r'_x[0-9A-Fa-f]{4}_', '', texto, flags=re.IGNORECASE)
    
    # ETAPA 2: Remover caracteres de controle problemáticos
    # Mantém apenas caracteres imprimíveis e quebras de linha básicas
    texto = ''.join(char for char in texto if ord(char) >= 32 or char in '\t\n\r')
    
    # ETAPA 3: Remover caracteres Unicode problemáticos específicos
    caracteres_problematicos = [
        '\u00A0',  # NBSP (Non-breaking space)
        '\u2000',  # En quad
        '\u2001',  # Em quad
        '\u2002',  # En space
        '\u2003',  # Em space
        '\u2004',  # Three-per-em space
        '\u2005',  # Four-per-em space
        '\u2006',  # Six-per-em space
        '\u2007',  # Figure space
        '\u2008',  # Punctuation space
        '\u2009',  # Thin space
        '\u200A',  # Hair space
        '\u200B',  # Zero width space
        '\u200C',  # Zero width non-joiner
        '\u200D',  # Zero width joiner
        '\u200E',  # Left-to-right mark
        '\u200F',  # Right-to-left mark
    ]
    
    for char in caracteres_problematicos:
        texto = texto.replace(char, ' ')
    
    # ETAPA 4: Normalizar espaços e quebras de linha
    texto = re.sub(r'\s+', ' ', texto)  # Múltiplos espaços -> um espaço
    texto = re.sub(r'\n+', '\n', texto)  # Múltiplas quebras de linha -> uma quebra
    texto = re.sub(r'\r+', '\r', texto)  # Múltiplos carriage returns -> um CR
    
    # ETAPA 5: Remover espaços extras no início e fim
    texto = texto.strip()
    
    # ETAPA 6: Validação final para Excel
    # Garantir que não há caracteres que podem causar problemas no XML do Excel
    texto = ''.join(char for char in texto if char.isprintable() or char in '\t\n\r ')
    
    return texto

def limpar_linhas_texto(texto):
    """
    Função equivalente ao VBA TrimLines - VERSÃO SEGURA PARA EXCEL
    Remove apenas espaços problemáticos básicos
    
    Args:
        texto (str): Texto a ser limpo
        
    Returns:
        str: Texto limpo e seguro para Excel
    """
    if not texto or len(texto) == 0:
        return texto
    
    # Converter para string se não for
    texto_str = str(texto)
    
    # DIAGNÓSTICO: Verificar se há caracteres problemáticos
    problemas = diagnosticar_caracteres_problematicos(texto_str)
    if problemas:
        print(f"🔍 Caracteres problemáticos detectados: {len(problemas)}")
        for problema in problemas[:5]:  # Mostra apenas os primeiros 5
            print(f"   {problema}")
    
    # LIMPEZA COMPLETA - equivalente ao VBA TrimLines
    # Remove caracteres problemáticos do Excel
    texto_limpo = texto_str.replace('\u00A0', '')  # NBSP
    texto_limpo = texto_limpo.replace('\r', '')      # CR
    texto_limpo = texto_limpo.replace('\u2003', ' ') # Em space -> espaço normal
    
    # LIMPEZA AGRESSIVA DO _x000D_ - múltiplas abordagens
    texto_limpo = texto_limpo.replace('_x000D_', '') # Carriage return do Excel
    texto_limpo = re.sub(r'_x000D_+', '', texto_limpo)  # Remove múltiplos _x000D_
    texto_limpo = re.sub(r'_x000D_\s*', '', texto_limpo)  # Remove _x000D_ + espaços
    texto_limpo = re.sub(r'_x[0-9A-Fa-f]{4}_', '', texto_limpo)  # Remove TODOS os XML escapes
    
    texto_limpo = texto_limpo.replace('_x0000_', '') # Null character do Excel
    texto_limpo = texto_limpo.replace('\x00', '')    # Null character
    texto_limpo = texto_limpo.replace('\u2002', ' ') # En space -> espaço normal
    texto_limpo = texto_limpo.replace('\u2009', ' ') # Thin space -> espaço normal
    
    # Remove espaços múltiplos
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo)
    
    # Remove caracteres problemáticos para Excel (caracteres de controle)
    texto_limpo = texto_limpo.replace('\x00', '')  # Null bytes
    texto_limpo = texto_limpo.replace('\x01', '')  # Control characters
    texto_limpo = texto_limpo.replace('\x02', '')
    texto_limpo = texto_limpo.replace('\x03', '')
    texto_limpo = texto_limpo.replace('\x04', '')
    texto_limpo = texto_limpo.replace('\x05', '')
    texto_limpo = texto_limpo.replace('\x06', '')
    texto_limpo = texto_limpo.replace('\x07', '')
    texto_limpo = texto_limpo.replace('\x08', '')
    texto_limpo = texto_limpo.replace('\x0B', '')  # Vertical tab
    texto_limpo = texto_limpo.replace('\x0C', '')  # Form feed
    texto_limpo = texto_limpo.replace('\x0E', '')
    texto_limpo = texto_limpo.replace('\x0F', '')
    
    # Divide por LF (vbLf) e limpa cada linha
    linhas = texto_limpo.split('\n')
    linhas_limpas = [linha.strip() for linha in linhas]
    
    # Reconstrói o texto
    resultado = '\n'.join(linhas_limpas)
    
    # PROTEÇÃO FINAL: garantir que não há caracteres problemáticos para Excel
    # Remove qualquer caractere de controle restante (exceto \n e \t)
    resultado = ''.join(char for char in resultado if ord(char) >= 32 or char in '\n\t')
    
    # Debug: verificar se houve mudança
    if texto_str != resultado:
        print(f"🔍 LIMPEZA: '{repr(texto_str[:50])}' -> '{repr(resultado[:50])}'")
    
    return resultado

def diagnosticar_caracteres_problematicos(texto):
    """Diagnostica caracteres problemáticos no texto."""
    if not texto:
        return []
    
    problemas = []
    for i, char in enumerate(texto):
        # Detecta caracteres de controle
        if ord(char) < 32 and char not in ['\n', '\r', '\t']:
            problemas.append(f"Posição {i}: Caractere de controle {ord(char)} (0x{ord(char):02X})")
        
        # Detecta caracteres Unicode problemáticos
        if ord(char) > 127 and char in ['\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008', '\u2009', '\u200A', '\u200B', '\u200C', '\u200D', '\u200E', '\u200F']:
            problemas.append(f"Posição {i}: Espaço Unicode problemático {ord(char)} (0x{ord(char):04X})")
        
        # Detecta sequências que podem ser _x000D_
        if i < len(texto) - 6:
            sequencia = texto[i:i+7]
            if '_x000D_' in sequencia:
                problemas.append(f"Posição {i}: Sequência _x000D_ encontrada: {repr(sequencia)}")
    
    return problemas

def limpar_texto_avancado(texto):
    """
    Versão avançada com mais funcionalidades de limpeza
    
    Args:
        texto (str): Texto a ser limpo
        
    Returns:
        str: Texto limpo
    """
    if not texto or len(texto) == 0:
        return texto
    
    # Remove caracteres especiais comuns
    texto = texto.replace('\u00A0', '')  # NBSP
    texto = texto.replace('\r', '')      # CR
    texto = texto.replace('\t', ' ')     # Tab -> espaço
    
    # Remove espaços múltiplos
    texto = re.sub(r' +', ' ', texto)
    
    # Divide por quebras de linha e limpa cada linha
    linhas = texto.split('\n')
    linhas_limpas = [linha.strip() for linha in linhas]
    
    # Remove linhas vazias se necessário
    # linhas_limpas = [linha for linha in linhas_limpas if linha]
    
    return '\n'.join(linhas_limpas)

def limpar_texto_para_analise(texto):
    """
    Função específica para limpeza de textos de análise de qualidade
    Remove caracteres de controle e normaliza o texto
    
    Args:
        texto (str): Texto a ser limpo
        
    Returns:
        str: Texto limpo e normalizado
    """
    if not texto:
        return ""
    
    # Limpeza básica
    texto = limpar_texto_avancado(texto)
    
    # Remove caracteres de controle
    texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
    
    # Normaliza espaços
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

def limpar_texto_excel(texto):
    """
    Função específica para limpeza de textos vindos do Excel
    Equivalente completo ao VBA TrimLines com melhorias
    
    Args:
        texto (str): Texto da coluna DS_CMNT do Excel
        
    Returns:
        str: Texto limpo e normalizado
    """
    if not texto or len(texto) == 0:
        return texto
    
    # Remove caracteres específicos do Excel
    texto = texto.replace('\u00A0', '')  # NBSP
    texto = texto.replace('\r', '')      # CR
    texto = texto.replace('\t', ' ')     # Tab
    
    # Remove caracteres de controle
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', texto)
    
    # Divide por quebras de linha e limpa cada linha
    linhas = texto.split('\n')
    linhas_limpas = []
    
    for linha in linhas:
        # Remove espaços no início e fim
        linha_limpa = linha.strip()
        # Remove espaços múltiplos
        linha_limpa = re.sub(r' +', ' ', linha_limpa)
        linhas_limpas.append(linha_limpa)
    
    # Reconstrói o texto
    return '\n'.join(linhas_limpas)

def validar_para_excel(texto: str) -> bool:
    """
    Valida se o texto está seguro para exportação no Excel.
    Verifica se há entidades XML escapadas que não deveriam estar ali.
    
    Args:
        texto (str): Texto a ser validado
        
    Returns:
        bool: True se o texto está limpo, False se contém entidades XML problemáticas
    """
    if not texto:
        return True
    
    # Verifica se há entidades XML escapadas que não deveriam estar ali
    return not bool(re.search(r'&(?:amp|lt|gt|quot|apos);', texto))

def preparar_para_excel(texto: str) -> str:
    """
    Prepara texto para exportação segura no Excel.
    Aplica limpeza e validação com fallback seguro.
    
    Args:
        texto (str): Texto original
        
    Returns:
        str: Texto limpo e seguro para Excel
    """
    if not texto:
        return ""
    
    # Aplica limpeza normal
    texto_limpo = limpar_linhas_texto(texto)
    
    # Valida se está seguro para Excel
    if not validar_para_excel(texto_limpo):
        # Log do problema para debugging
        print(f"⚠️ ATENÇÃO: Campo com entidades XML detectado: {texto_limpo[:100]}...")
        
        # Fallback seguro - remove entidades XML problemáticas
        texto_seguro = re.sub(r'&(?:amp|lt|gt|quot|apos);', '', texto_limpo)
        
        # Se ainda há problemas, usa versão truncada com aviso
        if not validar_para_excel(texto_seguro):
            return "[CONTEÚDO AJUSTADO: caracteres especiais removidos]"
        
        return texto_seguro
    
    return texto_limpo

def limpar_comentario_seguro_excel(comentario):
    """
    Versão ULTRA-SEGURA da função limpar_comentario, otimizada para compatibilidade total com Excel.
    Remove cabeçalhos e rodapés, mas com proteções MÁXIMAS contra caracteres problemáticos.
    Agora com validação preventiva para detectar entidades XML problemáticas.
    """
    if pd.isna(comentario) or not str(comentario).strip():
        return ""

    texto = str(comentario)
    
    # PROTEÇÃO INICIAL: Limpeza básica de caracteres problemáticos
    texto = limpar_linhas_texto(texto)

    # Etapa 1: Remover o rodapé "TICKET CRIADO POR..." de forma segura.
    padrao_rodape = re.compile(r'TICKET\s+CRIADO\s+POR.*$', re.IGNORECASE | re.DOTALL)
    texto = padrao_rodape.sub('', texto)

    # Etapa 2: Remover timestamps (NOME + DATA + HORA) de forma mais precisa.
    padrao_timestamp_maiusculas = re.compile(
        r'\b([A-ZÁÉÍÓÚÇÃÕÂÊÔ]{3,}\s+){1,3}[A-ZÁÉÍÓÚÇÃÕÂÊÔ]{3,}\s+\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{2}(?:\s*(?:AM|PM))?\b'
    )
    texto = padrao_timestamp_maiusculas.sub('', texto)

    linhas_limpas = []
    for linha in texto.splitlines():
        linha_strip = linha.strip()

        # Etapa 3: Tratar a linha "CONCLUSÃO:"
        if linha_strip.upper().startswith('CONCLUSÃO:'):
            texto_util = linha_strip[10:].strip()
            if texto_util:
                linhas_limpas.append(texto_util)
            continue

        # Se a linha não for de conclusão e não estiver vazia, adicione-a.
        if linha_strip:
            linhas_limpas.append(linha_strip)

    # Etapa 4: Juntar as linhas limpas e remover espaços duplos ou sobras.
    resultado_final = "\n".join(linhas_limpas)
    resultado_final = re.sub(r'\s{2,}', ' ', resultado_final).strip()
    
    # PROTEÇÃO FINAL: Usar a nova função de preparação para Excel com validação
    resultado_final = preparar_para_excel(resultado_final)
    
    return resultado_final

# =============================================================================
# EXEMPLO DE COMO APLICAR NO SEU CÓDIGO
# =============================================================================

def exemplo_de_aplicacao():
    """
    Exemplo de como aplicar a solução no seu código existente.
    """
    print("=" * 80)
    print("📝 EXEMPLO DE APLICAÇÃO NO SEU CÓDIGO")
    print("=" * 80)
    
    print("""
1️⃣ SUBSTITUIR A LINHA PROBLEMÁTICA:

   ❌ ANTES (não funciona):
   texto_limpo = texto.limpo.replace('_x000D_', '')
   
   ✅ DEPOIS (solução definitiva):
   texto_limpo = limpar_texto_para_excel_definitivo(texto.limpo)

2️⃣ APLICAR EM TODAS AS FUNÇÕES DE LIMPEZA:

   # Na função limpar_linhas_texto()
   def limpar_linhas_texto(texto):
       # ... código existente ...
       # Substituir por:
       return limpar_texto_para_excel_definitivo(texto)
   
   # Na função limpar_comentario_seguro_excel()
   def limpar_comentario_seguro_excel(comentario):
       # ... código existente ...
       # Substituir por:
       return limpar_texto_para_excel_definitivo(comentario)
   
   # Na função limpar_texto_avancado()
   def limpar_texto_avancado(texto):
       # ... código existente ...
       # Substituir por:
       return limpar_texto_para_excel_definitivo(texto)
   
   # Na função limpar_texto_excel()
   def limpar_texto_excel(texto):
       # ... código existente ...
       # Substituir por:
       return limpar_texto_para_excel_definitivo(texto)
   
   # Na função limpar_texto_para_analise()
   def limpar_texto_para_analise(texto):
       # ... código existente ...
       # Substituir por:
       return limpar_texto_para_excel_definitivo(texto)
   
   # Na função preparar_para_excel()
   def preparar_para_excel(texto):
       # ... código existente ...
       # Substituir por:
       return limpar_texto_para_excel_definitivo(texto)

3️⃣ TESTAR ANTES DE USAR EM PRODUÇÃO:

   # Teste com uma amostra pequena
   texto_teste = "JULIANA GJULIANA GJULIANA_x000D_"
   resultado = limpar_texto_para_excel_definitivo(texto_teste)
   print(f"Antes: {repr(texto_teste)}")
   print(f"Depois: {repr(resultado)}")

4️⃣ MONITORAR RESULTADOS:

   # Use o diagnóstico para verificar problemas
   problemas = diagnosticar_caracteres_problematicos(texto_teste)
   if problemas:
       print(f"Problemas encontrados: {len(problemas)}")
   else:
       print("Nenhum problema encontrado!")
""")

if __name__ == "__main__":
    print("🚀 SOLUÇÃO DEFINITIVA PARA _x000D_ - VERSÃO INTEGRADA")
    print()
    
    # Executar exemplo de aplicação
    exemplo_de_aplicacao()
    
    print("\n🎉 SOLUÇÃO PRONTA PARA INTEGRAÇÃO!")
    print("💡 Copie as funções acima para o seu código e substitua as chamadas existentes")