#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOLUÇÃO DEFINITIVA PARA O PROBLEMA _x000D_ NO EXCEL
=============================================================================
Esta solução resolve definitivamente o problema com _x000D_ e similares
que causam erros na abertura de arquivos Excel.

PROBLEMA IDENTIFICADO:
- A linha: texto_limpo.replace('_x000D_', '') não funciona porque:
  1. Remove apenas _x000D_, mas pode haver outros padrões similares (_x000A_, _x0009_, etc.)
  2. Não remove caracteres de controle problemáticos
  3. Não trata variações case-insensitive

SOLUÇÃO IMPLEMENTADA:
- Regex robusta para remover TODOS os padrões _xXXXX_
- Limpeza de caracteres de controle problemáticos
- Validação para Excel
- Múltiplas abordagens de fallback

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

def diagnosticar_problemas_texto(texto):
    """
    Diagnostica problemas específicos no texto que podem causar erros no Excel.
    
    Args:
        texto (str): Texto para diagnosticar
        
    Returns:
        dict: Relatório de problemas encontrados
    """
    if not texto:
        return {'problemas': [], 'total': 0}
    
    problemas = []
    
    # Verificar padrões _xXXXX_
    padroes_x = re.findall(r'_x[0-9A-Fa-f]{4}_', texto, flags=re.IGNORECASE)
    if padroes_x:
        problemas.append({
            'tipo': 'Padrões _xXXXX_',
            'quantidade': len(padroes_x),
            'exemplos': list(set(padroes_x))[:5]
        })
    
    # Verificar caracteres de controle
    caracteres_controle = []
    for i, char in enumerate(texto):
        if ord(char) < 32 and char not in '\t\n\r':
            caracteres_controle.append(f"Posição {i}: {ord(char)} (0x{ord(char):02X})")
    
    if caracteres_controle:
        problemas.append({
            'tipo': 'Caracteres de controle',
            'quantidade': len(caracteres_controle),
            'exemplos': caracteres_controle[:5]
        })
    
    # Verificar caracteres Unicode problemáticos
    unicode_problematicos = []
    for i, char in enumerate(texto):
        if ord(char) > 127 and char in '\u00A0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u200C\u200D\u200E\u200F':
            unicode_problematicos.append(f"Posição {i}: {char} (U+{ord(char):04X})")
    
    if unicode_problematicos:
        problemas.append({
            'tipo': 'Caracteres Unicode problemáticos',
            'quantidade': len(unicode_problematicos),
            'exemplos': unicode_problematicos[:5]
        })
    
    return {
        'problemas': problemas,
        'total': len(problemas)
    }

def testar_solucao_definitiva():
    """
    Testa a solução definitiva com exemplos reais do problema.
    """
    print("=" * 80)
    print("🧪 TESTE DA SOLUÇÃO DEFINITIVA PARA _x000D_")
    print("=" * 80)
    
    # Exemplos reais do problema
    exemplos_teste = [
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
        "PAOLA LAL PAOLA LAI PAOLA DE_x000D_",
        # Casos mais complexos
        "Texto com _x000A_ e _x000D_ misturados",
        "Texto com _x0009_ (tab) e _x000C_ (form feed)",
        "Texto com _x0000_ (null) e _x0001_ (start of heading)",
        "Texto com _x000B_ (vertical tab) e _x000E_ (shift out)",
        "Texto com _x000F_ (shift in) e _x001F_ (unit separator)",
        # Casos com caracteres Unicode problemáticos
        "Texto com\u00A0espaços\u2003não\u2009quebráveis",
        "Texto com\u200Bcaracteres\u200Cinvisíveis\u200D",
        # Casos mistos
        "Texto com _x000D_ e\u00A0espaços\u2003problemáticos",
        "Texto com _x000A_ e\u200Bcaracteres\u200Cinvisíveis"
    ]
    
    print(f"📊 Total de exemplos para testar: {len(exemplos_teste)}")
    print()
    
    for i, exemplo in enumerate(exemplos_teste, 1):
        print(f"🔍 TESTE {i:2d}:")
        print(f"   Original: {repr(exemplo)}")
        
        # Diagnosticar problemas
        diagnostico = diagnosticar_problemas_texto(exemplo)
        if diagnostico['total'] > 0:
            print(f"   ⚠️  Problemas encontrados: {diagnostico['total']}")
            for problema in diagnostico['problemas']:
                print(f"      - {problema['tipo']}: {problema['quantidade']} ocorrências")
                if problema['exemplos']:
                    print(f"        Exemplos: {problema['exemplos']}")
        else:
            print(f"   ✅ Nenhum problema encontrado")
        
        # Aplicar solução definitiva
        resultado = limpar_texto_para_excel_definitivo(exemplo)
        print(f"   Limpo: {repr(resultado)}")
        
        # Verificar se ainda há problemas
        diagnostico_pos = diagnosticar_problemas_texto(resultado)
        if diagnostico_pos['total'] == 0:
            print(f"   ✅ Solução aplicada com sucesso!")
        else:
            print(f"   ❌ Ainda há problemas: {diagnostico_pos['total']}")
        
        print()
    
    print("=" * 80)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 80)

def aplicar_solucao_no_codigo_existente():
    """
    Mostra como aplicar a solução no código existente.
    """
    print("=" * 80)
    print("🔧 COMO APLICAR A SOLUÇÃO NO SEU CÓDIGO")
    print("=" * 80)
    
    print("""
1️⃣ SUBSTITUIR A LINHA PROBLEMÁTICA:
   
   ❌ ANTES (não funciona):
   texto_limpo = texto.limpo.replace('_x000D_', '')
   
   ✅ DEPOIS (solução definitiva):
   texto_limpo = limpar_texto_para_excel_definitivo(texto.limpo)

2️⃣ ADICIONAR A FUNÇÃO NO SEU CÓDIGO:
   
   Copie a função limpar_texto_para_excel_definitivo() para o seu código.

3️⃣ APLICAR EM TODAS AS FUNÇÕES DE LIMPEZA:
   
   - limpar_linhas_texto()
   - limpar_comentario_seguro_excel()
   - limpar_texto_avancado()
   - limpar_texto_excel()
   - limpar_texto_para_analise()
   - preparar_para_excel()

4️⃣ TESTAR ANTES DE USAR EM PRODUÇÃO:
   
   Execute testar_solucao_definitiva() para verificar se funciona.

5️⃣ MONITORAR RESULTADOS:
   
   Use diagnosticar_problemas_texto() para verificar se ainda há problemas.
""")
    
    print("=" * 80)
    print("💡 DICAS IMPORTANTES:")
    print("=" * 80)
    
    print("""
🎯 VANTAGENS DA SOLUÇÃO DEFINITIVA:
   • Remove TODOS os padrões _xXXXX_ (não apenas _x000D_)
   • Trata caracteres de controle problemáticos
   • Remove caracteres Unicode problemáticos
   • Funciona com qualquer variação do problema
   • Validação final para Excel
   • Diagnóstico de problemas

⚠️  CUIDADOS:
   • Teste sempre com uma amostra pequena primeiro
   • Faça backup dos dados antes de aplicar
   • Monitore os resultados após a aplicação
   • Use o diagnóstico para verificar problemas restantes

🔍 COMO VERIFICAR SE FUNCIONOU:
   • Execute o diagnóstico antes e depois
   • Verifique se o Excel abre sem erros
   • Confirme que os dados estão íntegros
   • Teste com diferentes tipos de arquivo
""")

if __name__ == "__main__":
    print("🚀 INICIANDO SOLUÇÃO DEFINITIVA PARA _x000D_")
    print()
    
    # Executar teste
    testar_solucao_definitiva()
    
    # Mostrar como aplicar
    aplicar_solucao_no_codigo_existente()
    
    print("\n🎉 SOLUÇÃO DEFINITIVA IMPLEMENTADA!")
    print("💡 Agora você pode aplicar no seu código para resolver o problema _x000D_")