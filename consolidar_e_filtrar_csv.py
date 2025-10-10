#!/usr/bin/env python3
"""
Script para consolidar múltiplos arquivos CSV, aplicar um filtro para manter
apenas o registro mais recente de cada ID e salvar os resultados em arquivos separados.

Autor: QUALITY ASSURANCE
Data: 10/2025  
"""

import pandas as pd
import os
import sys
import warnings
import csv
import io
import re

# Suprimir warnings de parsing de datas do pandas
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings('ignore', message='.*Parsing dates.*')
warnings.filterwarnings('ignore', message='.*Could not infer format.*')
warnings.filterwarnings('ignore', message='.*dayfirst.*')
warnings.filterwarnings('ignore', message='.*columns are not unique.*')
warnings.filterwarnings('ignore', message='.*DataFrame columns are not unique.*')
warnings.filterwarnings('ignore', category=UserWarning)

def deduplicar_cabecalhos(cabecalho):
    """Gera nomes únicos para colunas repetidas preservando o texto original.
    Ex.: ["ID", "ID", "Criado"] -> ["ID", "ID_2", "Criado"]
    """
    nomes_unicos = []
    contagem = {}
    for nome in cabecalho:
        nome_base = (nome or '').strip()
        if nome_base in contagem:
            contagem[nome_base] += 1
            nomes_unicos.append(f"{nome_base}_{contagem[nome_base]}")
        else:
            contagem[nome_base] = 1
            nomes_unicos.append(nome_base)
    return nomes_unicos

def normalizar_coluna_id(df):
    """Coalesce de colunas equivalentes a 'ID' em uma única coluna 'ID'.
    Mantém todos os dados sem perdas e remove duplicatas de cabeçalho para ID.
    """
    try:
        def norm(s):
            return ''.join(ch for ch in str(s) if ch.isalnum()).lower()

        # Considerar 'ID' e duplicatas criadas (ID_2, ID_3, ...)
        candidatos = [c for c in df.columns if str(c).upper() == 'ID' or str(c).upper().startswith('ID_')]
        if not candidatos:
            return df

        # Escolher o candidato mais "numérico" (menos textos/HTML)
        melhor = None
        melhor_score = -1
        for c in candidatos:
            col = df[c].astype(str)
            # Score: quantidade de linhas com apenas dígitos (após strip)
            score = (col.str.strip().str.fullmatch(r"\d+").fillna(False)).sum()
            if score > melhor_score:
                melhor_score = score
                melhor = c

        if melhor is None:
            melhor = candidatos[0]
        df['ID'] = df[melhor].astype(str)

        # Remover colunas duplicadas de ID mantendo apenas 'ID'
        para_remover = [c for c in candidatos if c != 'ID']
        if para_remover:
            df = df.drop(columns=para_remover)
        return df
    except Exception:
        return df

def limpar_texto(valor: str) -> str:
    """Remove caracteres invisíveis comuns e normaliza espaços/bordas."""
    try:
        if valor is None:
            return ''
        s = str(valor)
        # Remover BOM e espaços não separáveis / zero-width
        s = s.replace('\ufeff', '')  # BOM
        s = s.replace('\u00A0', ' ')  # NBSP
        s = s.replace('\u200B', '')  # zero-width space
        s = s.replace('\u200C', '')  # zero-width non-joiner
        s = s.replace('\u200D', '')  # zero-width joiner
        # Normalizar tabs/CR
        s = re.sub(r"[\r\t]", " ", s)
        return s.strip()
    except Exception:
        return '' if valor is None else str(valor)

def higienizar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df.columns = [limpar_texto(c) for c in df.columns]
        return df
    except Exception:
        return df

def normalizar_csvs(pasta_entrada: str, pasta_saida: str = "csv_normalizados") -> str:
    """Normaliza TODOS os CSVs de pasta_entrada para um padrão único e grava em pasta_saida.
    Padrão: delimitador ';', encoding 'utf-8-sig', lineterminator='\n', quote '"'.
    Mantém cabeçalho e ordem de colunas exatamente como no arquivo original.
    Retorna o caminho da pasta normalizada.
    """
    try:
        # Resolver pasta de saída relativa à entrada caso necessário
        if not os.path.isabs(pasta_saida):
            base_dir = pasta_entrada if os.path.isabs(pasta_entrada) else os.path.join(os.getcwd(), pasta_entrada)
            base_dir = os.path.dirname(base_dir) if os.path.isfile(base_dir) else base_dir
            pasta_saida_abs = os.path.join(base_dir, pasta_saida)
        else:
            pasta_saida_abs = pasta_saida

        os.makedirs(pasta_saida_abs, exist_ok=True)

        arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith('.csv')]
        print(f"\n🧹 Normalizando {len(arquivos)} CSV(s) em '{pasta_saida_abs}'...")

        for idx, nome in enumerate(arquivos, 1):
            caminho_in = os.path.join(pasta_entrada, nome)
            caminho_out = os.path.join(pasta_saida_abs, nome)

            # Detectar encoding por tentativas leves (somente encoding, SEM sniffer de delimitador)
            encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'windows-1252', 'latin-1']
            leitor_ok = False

            # Pular arquivos totalmente vazios (0 bytes)
            try:
                if os.path.getsize(caminho_in) == 0:
                    print(f"   ⚠️ {idx}/{len(arquivos)}: {nome} vazio (0 bytes) — ignorado")
                    continue
            except Exception:
                pass

            for enc in encodings:
                try:
                    with open(caminho_in, 'r', encoding=enc, newline='') as fin:
                        # Detectar delimitador por amostra; fallback para ';' ou ','
                        amostra = fin.read(4096)
                        fin.seek(0)
                        try:
                            delimitador = csv.Sniffer().sniff(amostra, delimiters=';,|\t').delimiter
                        except Exception:
                            # Fallback simples: contar separadores comuns
                            counts = {
                                ';': amostra.count(';'),
                                ',': amostra.count(','),
                                '|': amostra.count('|'),
                                '\t': amostra.count('\t'),
                            }
                            delimitador = max(counts, key=counts.get) if any(counts.values()) else ';'

                        reader = csv.reader(
                            fin,
                            delimiter=delimitador,
                            quotechar='"',
                            # IMPORTANTE: não usar escapechar para evitar tratar '\\' como escape de newline
                            doublequote=True,
                            skipinitialspace=False,
                        )

                        # Abrir saída com padrão definido
                        with open(caminho_out, 'w', encoding='utf-8-sig', newline='') as fout:
                            writer = csv.writer(
                                fout,
                                delimiter=';',
                                quotechar='"',
                                lineterminator='\n',
                                quoting=csv.QUOTE_ALL,  # citar tudo para máxima robustez
                                # doublequote True por padrão
                            )

                            # Ler cabeçalho
                            try:
                                header = next(reader)
                            except StopIteration:
                                header = []

                            header = [limpar_texto(str(h)) for h in header]
                            largura = len(header)
                            if largura == 0:
                                # Arquivo sem cabeçalho — ignorar
                                leitor_ok = True
                                # remover arquivo de saída se criado
                                try:
                                    fout.flush()
                                except Exception:
                                    pass
                                try:
                                    os.remove(caminho_out)
                                except Exception:
                                    pass
                                print(f"   ⚠️ {idx}/{len(arquivos)}: {nome} sem cabeçalho — ignorado")
                                break
                            writer.writerow(header)

                            # Stream de linhas, garantindo largura consistente
                            linhas_escritas = 0
                            for row in reader:
                                if row is None:
                                    continue
                                row = [limpar_texto(str(x)) for x in row]
                                # Pular linhas totalmente vazias
                                if not row or all(x == '' for x in row):
                                    continue
                                if len(row) < largura:
                                    row.extend([''] * (largura - len(row)))
                                elif len(row) > largura:
                                    row = row[:largura]
                                writer.writerow(row)
                                linhas_escritas += 1

                        # Se não há linhas de dados, remover arquivo normalizado vazio
                        if linhas_escritas == 0:
                            try:
                                os.remove(caminho_out)
                            except Exception:
                                pass
                            print(f"   ⚠️ {idx}/{len(arquivos)}: {nome} sem dados (apenas cabeçalho) — ignorado")
                        else:
                            print(f"   ✓ {idx}/{len(arquivos)}: {nome} → {linhas_escritas:,} linhas normalizadas")

                        leitor_ok = True
                        break
                except Exception:
                    continue

            if not leitor_ok:
                print(f"   ⚠️ Falha ao normalizar '{nome}' (enc/forma não suportada)")

        return pasta_saida_abs
    except Exception as e:
        print(f"⚠️ Aviso: normalização falhou: {e}")
        return pasta_entrada

def ler_csv_manual(caminho_arquivo, encoding_preferido):
    """
    Leitor robusto usando csv.Sniffer e csv.reader para respeitar aspas e
    delimitadores reais do arquivo. Preserva o cabeçalho original e evita
    deslocamentos de colunas mesmo quando há separadores dentro de textos.
    """
    try:
        encodings_para_tentar = [encoding_preferido, 'utf-8-sig', 'cp1252', 'windows-1252', 'latin-1']
        for encoding in encodings_para_tentar:
            try:
                with open(caminho_arquivo, 'r', encoding=encoding, newline='') as arquivo:
                    amostra = arquivo.read(4096)
                    arquivo.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(amostra, delimiters=';,|\t')
                        delimitador = dialect.delimiter
                    except Exception:
                        # Fallback simples por contagem
                        counts = {
                            ';': amostra.count(';'),
                            ',': amostra.count(','),
                            '|': amostra.count('|'),
                            '\t': amostra.count('\t'),
                        }
                        delimitador = max(counts, key=counts.get) if any(counts.values()) else ';'

                    leitor = csv.reader(
                        arquivo,
                        delimiter=delimitador,
                        quotechar='"',
                        # NÃO usar escapechar para não tratar barra invertida como escape
                        doublequote=True,
                        skipinitialspace=False,
                    )
                    linhas = list(leitor)
                    if not linhas or len(linhas) < 2:
                        continue

                    cabecalho = [str(h).strip() for h in linhas[0]]
                    cabecalho = deduplicar_cabecalhos(cabecalho)
                    largura = len(cabecalho)

                    dados = []
                    for linha in linhas[1:]:
                        linha_atual = list(linha)
                        if len(linha_atual) < largura:
                            linha_atual.extend([''] * (largura - len(linha_atual)))
                        elif len(linha_atual) > largura:
                            linha_atual = linha_atual[:largura]
                        dados.append(linha_atual)

                    df = pd.DataFrame(dados, columns=cabecalho, dtype=str)
                    df.reset_index(drop=True, inplace=True)
                    if len(df.columns) > 0:
                        return df
            except Exception:
                continue
        return None
    except Exception:
        return None

def consolidar_e_filtrar_csv(pasta_entrada, arquivo_saida_consolidado="consolidado.csv", arquivo_saida_filtrado="consolidado_filtrado.csv"):
    """
    Consolida, filtra e salva arquivos CSV de uma pasta.

    Args:
        pasta_entrada (str): Caminho para a pasta com os arquivos CSV.
        arquivo_saida_consolidado (str): Nome do arquivo CSV consolidado.
        arquivo_saida_filtrado (str): Nome do arquivo CSV filtrado.

    Returns:
        bool: True se o processo foi bem-sucedido, False caso contrário.
    """
    try:
        if not os.path.exists(pasta_entrada):
            print(f"❌ Erro: A pasta ‘{pasta_entrada}’ não existe.")
            return False

        # Pré-normalizar todos os CSVs para um padrão único antes de consolidar
        pasta_normalizada = normalizar_csvs(pasta_entrada, pasta_saida="csv_normalizados")
        # Apontar consolidação para a pasta normalizada (apenas arquivos com dados)
        arquivos_csv = [
            f for f in os.listdir(pasta_normalizada)
            if f.lower().endswith('.csv') and os.path.getsize(os.path.join(pasta_normalizada, f)) > 0
        ]
        if not arquivos_csv:
            print(f"❌ Erro: Nenhum arquivo CSV encontrado na pasta ‘{pasta_entrada}’.")
            return False

        print(f"📁 Encontrados {len(arquivos_csv)} arquivos CSV na pasta ‘{pasta_entrada}’")
       
        lista_dataframes = []
        for i, nome_arquivo in enumerate(arquivos_csv, 1):
            caminho_arquivo = os.path.join(pasta_normalizada, nome_arquivo)
            df = None
           
            # Estratégias de leitura em ordem de preferência
            estrategias = [
                # Estratégia 1: UTF-8 com ponto-e-vírgula
                {'encoding': 'utf-8', 'sep': ';', 'desc': 'UTF-8+;'},
                # Estratégia 2: UTF-8 com vírgula
                {'encoding': 'utf-8', 'sep': ',', 'desc': 'UTF-8+,'},
                # Estratégia 3: cp1252 com ponto-e-vírgula
                {'encoding': 'cp1252', 'sep': ';', 'desc': 'cp1252+;'},
                # Estratégia 4: cp1252 com vírgula
                {'encoding': 'cp1252', 'sep': ',', 'desc': 'cp1252+,'},
                # Estratégia 5: Latin-1 com ponto-e-vírgula
                {'encoding': 'latin-1', 'sep': ';', 'desc': 'Latin-1+;'},
                # Estratégia 6: Latin-1 com vírgula
                {'encoding': 'latin-1', 'sep': ',', 'desc': 'Latin-1+,'},
                # Estratégia 7: UTF-8 com separador automático
                {'encoding': 'utf-8', 'sep': None, 'desc': 'UTF-8+auto'},
                # Estratégia 8: cp1252 com separador automático
                {'encoding': 'cp1252', 'sep': None, 'desc': 'cp1252+auto'},
                # Estratégia 9: Latin-1 com separador automático
                {'encoding': 'latin-1', 'sep': None, 'desc': 'Latin-1+auto'},
                # Estratégia 10: Leitura linha por linha (último recurso)
                {'encoding': 'utf-8', 'sep': 'manual', 'desc': 'Manual+UTF-8'},
                # Estratégia 11: Leitura linha por linha com cp1252
                {'encoding': 'cp1252', 'sep': 'manual', 'desc': 'Manual+cp1252'},
                # Estratégia 12: Leitura linha por linha com Latin-1
                {'encoding': 'latin-1', 'sep': 'manual', 'desc': 'Manual+Latin-1'}
            ]
           
            for estrategia in estrategias:
                try:
                    if estrategia['sep'] == 'manual':
                        # Leitura manual linha por linha (último recurso)
                        df = ler_csv_manual(caminho_arquivo, estrategia['encoding'])
                        if df is not None and len(df) > 0:
                            # Garantir que o DataFrame tenha índice único
                            df.reset_index(drop=True, inplace=True)
                            df = higienizar_nomes_colunas(df)
                            lista_dataframes.append(df)
                            print(f"✅ Processado arquivo {i}/{len(arquivos_csv)}: {nome_arquivo} ({len(df)} linhas) [{estrategia['desc']}]")
                            break
                    else:
                        # Leitura normal com pandas
                        df = pd.read_csv(
                            caminho_arquivo,
                            dtype=str,
                            low_memory=False,
                            encoding=estrategia['encoding'],
                            sep=estrategia['sep'],
                            quotechar='"',
                            engine='python',  # usar engine python para maior robustez
                            on_bad_lines='warn',
                        )
                        if len(df) > 0:
                            # Garantir que o DataFrame tenha índice único
                            df.reset_index(drop=True, inplace=True)
                            df = higienizar_nomes_colunas(df)
                            # Tornar nomes de colunas únicos mesmo em leituras padrão
                            try:
                                df.columns = deduplicar_cabecalhos([str(c) for c in df.columns])
                            except Exception:
                                pass
                            lista_dataframes.append(df)
                            print(f"✅ Processado arquivo {i}/{len(arquivos_csv)}: {nome_arquivo} ({len(df)} linhas) [{estrategia['desc']}]")
                            break
                except Exception:
                    # Continuar para próxima estratégia
                    continue
           
            if df is None or len(df) == 0:
                print(f"❌ Erro: Não foi possível processar '{nome_arquivo}' com nenhuma estratégia disponível")
                continue

        if not lista_dataframes:
            print("❌ Erro: Nenhum arquivo CSV pôde ser lido com sucesso.")
            return False

        print("\n🔄 Consolidando todos os dados...")
       
        # Verificar se há DataFrames válidos
        if not lista_dataframes:
            print("❌ Erro: Nenhum DataFrame válido para consolidar.")
            return False
       
        # SOLUÇÃO DEFINITIVA: Converter para lista de dicionários e recriar DataFrame
        print(f"   📊 Processando {len(lista_dataframes)} DataFrames...")
       
        # Coletar todas as linhas como dicionários (elimina problema de índices)
        todas_linhas = []
        total_processados = 0
       
        for i, df in enumerate(lista_dataframes):
            try:
                # Garantir que o DataFrame seja válido
                if df is None or len(df) == 0:
                    print(f"⚠️ Aviso: DataFrame {i} está vazio ou None")
                    continue
               
                # Converter DataFrame para lista de dicionários (elimina índices)
                linhas_dict = df.to_dict('records')
                todas_linhas.extend(linhas_dict)
                total_processados += len(linhas_dict)
               
                print(f"   ✓ Processado DataFrame {i+1}/{len(lista_dataframes)}: {len(linhas_dict):,} registros")
                   
            except Exception as e:
                print(f"⚠️ Aviso: Erro ao processar DataFrame {i}: {e}")
                continue
       
        # Verificar se há dados válidos para consolidar
        if not todas_linhas:
            print("❌ Erro: Nenhum dado válido para consolidar após validação.")
            return False
       
        print(f"   📊 Total de registros coletados: {len(todas_linhas):,}")
       
        # Criar DataFrame consolidado a partir dos dicionários (índices novos e únicos)
        try:
            df_consolidado = pd.DataFrame(todas_linhas, dtype=str)
           
            # Garantir índice único e cabeçalhos únicos
            df_consolidado.reset_index(drop=True, inplace=True)
            try:
                df_consolidado.columns = deduplicar_cabecalhos([str(c) for c in df_consolidado.columns])
            except Exception:
                pass
           
        except Exception as e:
            print(f"❌ Erro ao criar DataFrame consolidado: {e}")
            return False
       
        # Verificar se a consolidação foi bem-sucedida
        if df_consolidado is None or len(df_consolidado) == 0:
            print("❌ Erro: DataFrame consolidado está vazio.")
            return False
       
        # Normalizar coluna ID logo após a consolidação
        try:
            df_consolidado = normalizar_coluna_id(df_consolidado)
        except Exception:
            pass
        # (Contagem detalhada removida a pedido do usuário)
       
        # Salvar consolidado (sem reabrir em memória para evitar consumo excessivo)
        df_consolidado.to_csv(arquivo_saida_consolidado, index=False)
       
        total_consolidado = len(df_consolidado)
        print(f"✅ Arquivo consolidado ‘{arquivo_saida_consolidado}’ salvo com {total_consolidado:,} registros.")

        # --- Início da Lógica de Filtragem ---
        print("\n🔄 Aplicando filtro de registros duplicados...")
       
        # Verificar se as colunas necessárias existem (com nomes higienizados)
        df_consolidado = higienizar_nomes_colunas(df_consolidado)
        colunas_necessarias = ['ID', 'Modificado', 'Criado']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_consolidado.columns]
       
        if colunas_faltantes:
            print(f"\n❌ Erro: As seguintes colunas são necessárias para o filtro, mas não foram encontradas:")
            for col in colunas_faltantes:
                print(f"   • '{col}'")
           
            print(f"\n💡 Sugestão: Verifique se os arquivos CSV têm as colunas corretas.")
            print(f"   As colunas disponíveis são: {', '.join(df_consolidado.columns)}")
            return False

        # Converte as colunas de data para datetime, tratando erros
        # Usar cópia do consolidado em memória para filtrar (garantindo mesma estrutura do consolidado.csv)
        df_base = df_consolidado.copy()

        df_base['modificado_convertida'] = pd.to_datetime(df_base['Modificado'], errors='coerce')
        df_base['criado_convertida'] = pd.to_datetime(df_base['Criado'], errors='coerce')
       
        # Verificar se há registros com datas inválidas (mas não removê-los)
        registros_modificado_invalidos = df_base['modificado_convertida'].isna().sum()
        registros_criado_invalidos = df_base['criado_convertida'].isna().sum()
       
        if registros_modificado_invalidos > 0:
            print(f"⚠️ Aviso: {registros_modificado_invalidos} registros possuem data de modificação inválida.")
        if registros_criado_invalidos > 0:
            print(f"⚠️ Aviso: {registros_criado_invalidos} registros possuem data de criação inválida.")

        # Criar uma condição para identificar registros onde modificado > criado
        # Para registros com datas inválidas, assumimos que a condição é verdadeira para não perdê-los
        try:
            # Converter para o mesmo tipo de datetime para comparação segura
            df_base['modificado_convertida'] = pd.to_datetime(df_base['modificado_convertida'], errors='coerce')
            df_base['criado_convertida'] = pd.to_datetime(df_base['criado_convertida'], errors='coerce')

            # Criar máscaras booleanas para comparação segura
            mask_modificado_valido = df_base['modificado_convertida'].notna()
            mask_criado_valido = df_base['criado_convertida'].notna()
            mask_ambos_validos = mask_modificado_valido & mask_criado_valido

            # Inicializar a condição como True para todos
            condicao_data_valida = pd.Series([True] * len(df_base), index=df_base.index)

            # Para registros com ambas as datas válidas, verificar se modificado > criado
            if mask_ambos_validos.sum() > 0:
                condicao_data_valida.loc[mask_ambos_validos] = (
                    df_base.loc[mask_ambos_validos, 'modificado_convertida'] >
                    df_base.loc[mask_ambos_validos, 'criado_convertida']
                )
        except Exception as e:
            print(f"⚠️ Erro ao comparar datas: {e}")
            # Em caso de erro, manter todos os registros
            condicao_data_valida = pd.Series([True] * len(df_base), index=df_base.index)

        # Adicionar coluna para marcar registros válidos
        df_base['condicao_valida'] = condicao_data_valida

        # Agrupar por ID e processar cada grupo
        ids_excluidos = []
        lista_registros_filtrados = []
       
        for id_atual, grupo in df_base.groupby('ID'):
            # Filtrar registros que atendem à condição (modificado > criado)
            registros_validos = grupo[grupo['condicao_valida'] == True]
           
            if len(registros_validos) > 0:
                # Se há registros válidos, pegar o mais recente (maior data de modificação)
                # Filtrar apenas registros com data de modificação válida para o idxmax
                registros_com_data_valida = registros_validos[registros_validos['modificado_convertida'].notna()]
                if len(registros_com_data_valida) > 0:
                    registro_escolhido = registros_com_data_valida.loc[registros_com_data_valida['modificado_convertida'].idxmax()]
                else:
                    # Se não há datas válidas, pegar o primeiro registro válido
                    registro_escolhido = registros_validos.iloc[0]
                lista_registros_filtrados.append(registro_escolhido)
               
                # Registrar IDs excluídos
                registros_excluidos_grupo = grupo[grupo.index != registro_escolhido.name]
                if len(registros_excluidos_grupo) > 0:
                    ids_excluidos.extend([id_atual] * len(registros_excluidos_grupo))
            else:
                # Se nenhum registro atende à condição, manter o primeiro do grupo
                registro_escolhido = grupo.iloc[0]
                lista_registros_filtrados.append(registro_escolhido)
               
                # Registrar IDs excluídos
                if len(grupo) > 1:
                    ids_excluidos.extend([id_atual] * (len(grupo) - 1))

        # Criar DataFrame filtrado
        df_filtrado = pd.DataFrame(lista_registros_filtrados)
       
        # Calcular estatísticas por mês ANTES de remover colunas auxiliares
        def calcular_cards_por_mes(dataframe, nome_dataset):
            """Calcula e exibe estatísticas de CARDs por mês."""
            if 'criado_convertida' in dataframe.columns:
                # Extrair ano-mês da coluna de criação
                dataframe_temp = dataframe.copy()
                # Remover informações de timezone antes de converter para período
                dataframe_temp['criado_sem_tz'] = dataframe_temp['criado_convertida'].dt.tz_localize(None)
                dataframe_temp['ano_mes'] = dataframe_temp['criado_sem_tz'].dt.to_period('M')
               
                # Contar registros por mês (apenas com datas válidas)
                cards_por_mes = dataframe_temp['ano_mes'].value_counts().sort_index()
               
                if len(cards_por_mes) > 0:
                    print(f"\n📅 CARDs por mês - {nome_dataset}:")
                    total_com_data_valida = 0
                    for periodo, quantidade in cards_por_mes.items():
                        if pd.notna(periodo):
                            print(f"   • {periodo}: {quantidade:,} CARDs")
                            total_com_data_valida += quantidade
                   
                    # Registros com datas inválidas
                    registros_sem_data = dataframe_temp['ano_mes'].isna().sum()
                    if registros_sem_data > 0:
                        print(f"   • Sem data válida: {registros_sem_data:,} CARDs")
                   
                    # Total consolidado
                    total_geral = total_com_data_valida + registros_sem_data
                    print(f"   📊 TOTAL: {total_geral:,} CARDs")
                else:
                    print(f"\n📅 CARDs por mês - {nome_dataset}: Nenhum registro com data válida encontrado.")
       
        # Calcular estatísticas ANTES do filtro
        calcular_cards_por_mes(df_consolidado, "ANTES do filtro")
       
        # Remove as colunas auxiliares antes de salvar
        colunas_para_remover = ['modificado_convertida', 'criado_convertida', 'condicao_valida']
        df_filtrado = df_filtrado.drop(columns=colunas_para_remover)
       
        total_filtrado = len(df_filtrado)
        registros_excluidos_duplicatas = total_consolidado - total_filtrado
        total_registros_excluidos = total_consolidado - total_filtrado

        print(f"\n📊 Filtros aplicados!")
        print(f"   • Registros excluídos por duplicatas: {registros_excluidos_duplicatas:,}")
        print(f"   • Total de registros excluídos: {total_registros_excluidos:,}")
       
        # Exibir resumo dos IDs excluídos (sem detalhes para não poluir o console)
        if ids_excluidos:
            ids_unicos_excluidos = list(set(ids_excluidos))
            print(f"🗑️ Total de IDs únicos com registros excluídos: {len(ids_unicos_excluidos):,}")
        else:
            print("✅ Nenhum ID teve registros excluídos.")

        # Unificar possíveis variações de coluna ID e ordenar
        try:
            df_filtrado = normalizar_coluna_id(df_filtrado)
            if 'ID' in df_filtrado.columns:
                df_filtrado = df_filtrado.sort_values('ID', kind='stable')
        except Exception:
            pass

        # Garantir que a primeira linha é o cabeçalho e não dados deslocados
        # (apenas sanity check; não grava nada além de CSV padrão)

        df_filtrado.to_csv(arquivo_saida_filtrado, index=False)
        print(f"✅ Arquivo filtrado '{arquivo_saida_filtrado}' salvo com {total_filtrado:,} registros únicos.")
       
        # Calcular estatísticas DEPOIS do filtro (recriar colunas auxiliares temporariamente)
        df_filtrado_temp = df_filtrado.copy()
        df_filtrado_temp['criado_convertida'] = pd.to_datetime(df_filtrado_temp['Criado'], errors='coerce')
        calcular_cards_por_mes(df_filtrado_temp, "DEPOIS do filtro")
       
        # --- Fim da Lógica de Filtragem ---

        print(f"\n📈 Estatísticas Finais:")
        print(f"   • Total de registros consolidados: {total_consolidado:,}")
        print(f"   • Total de registros únicos (filtrados): {total_filtrado:,}")
        print(f"   • Total de registros excluídos: {total_registros_excluidos:,}")
        print(f"   • Registros excluídos por duplicatas: {registros_excluidos_duplicatas:,}")
        # (Removida métrica específica de Auditoria Digital para esta versão)

        # --- Análise Específica: Criado > Data e Hora de envio para Concluído ---
        # (Executada APÓS todas as exclusões para analisar apenas os dados finais)
        print("\n🔍 Analisando registros com data de criação posterior ao envio para concluído...")
       
        nome_coluna_envio = "Data e Hora de envio para Concluído"
        arquivo_xlsx_anomalias = "registros_anomalos.xlsx"
       
        if nome_coluna_envio in df_filtrado.columns:
            # Usar o DataFrame filtrado final para a análise de anomalias
            df_analise = df_filtrado.copy()
            df_analise['criado_convertida'] = pd.to_datetime(df_analise['Criado'], errors='coerce')
            df_analise['envio_convertida'] = pd.to_datetime(df_analise[nome_coluna_envio], errors='coerce')
           
            # Identificar registros onde Criado > Data de envio para concluído
            # Considerar apenas registros com ambas as datas válidas
            condicao_anomala = (
                df_analise['criado_convertida'].notna() &
                df_analise['envio_convertida'].notna() &
                (df_analise['criado_convertida'] > df_analise['envio_convertida'])
            )
           
            registros_anomalos = df_analise[condicao_anomala].copy()
           
            if len(registros_anomalos) > 0:
                # Remover colunas auxiliares antes de salvar
                colunas_auxiliares = ['criado_convertida', 'envio_convertida']
                registros_anomalos_limpos = registros_anomalos.drop(columns=[col for col in colunas_auxiliares if col in registros_anomalos.columns])
               
                # Salvar em arquivo XLSX
                registros_anomalos_limpos.to_excel(arquivo_xlsx_anomalias, index=False, engine='openpyxl')
               
                print(f"⚠️  Encontrados {len(registros_anomalos):,} registros com data de criação posterior ao envio para concluído.")
                print(f"📄 Arquivo XLSX gerado: '{arquivo_xlsx_anomalias}' (baseado nos dados filtrados)")
               
                # Exibir alguns exemplos
                print("🔍 Exemplos de registros anômalos:")
                for idx, row in registros_anomalos.head(3).iterrows():
                    id_registro = row['ID']
                    data_criado = row['criado_convertida'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['criado_convertida']) else 'N/A'
                    data_envio = row['envio_convertida'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['envio_convertida']) else 'N/A'
                    print(f"   • ID {id_registro}: Criado={data_criado}, Envio={data_envio}")
               
                if len(registros_anomalos) > 3:
                    print(f"   ... e mais {len(registros_anomalos) - 3} registros no arquivo XLSX.")
                   
            else:
                print("✅ Nenhum registro encontrado com data de criação posterior ao envio para concluído.")
               
        else:
            print(f"⚠️  Coluna '{nome_coluna_envio}' não encontrada nos dados filtrados. Análise não realizada.")
       
        # --- Fim da Análise Específica ---

        return True

    except Exception as e:
        print(f"❌ Erro inesperado durante o processo: {e}")
        return False

def principal():
    """Função principal para executar o script via linha de comando."""
    print("🚀 Iniciando consolidação e filtragem de arquivos CSV...")
    print("=" * 60)
   
    pasta_padrao = "csv_arquivos"
   
    if len(sys.argv) > 2:
        print("❌ Uso: python consolidar_e_filtrar_csv.py [pasta_csv]")
        sys.exit(1)
   
    pasta_entrada = sys.argv[1] if len(sys.argv) == 2 else pasta_padrao

    print(f"📁 Pasta de entrada: {pasta_entrada}")
    print("-" * 60)

    sucesso = consolidar_e_filtrar_csv(pasta_entrada)

    if sucesso:
        print("\n🎉 Processo concluído com sucesso!")
    else:
        print("\n❌ O processo falhou. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    principal()
