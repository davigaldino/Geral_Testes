# -*- coding: utf-8 -*-
"""
Script: validation_reporter.py

Gera relatórios profissionais de validação/qualidade de dados em Excel (.xlsx) e PDF,
com métricas de sumário, detalhes por categoria, sugestões de correção e gráficos.

- Entrada: relatório de validação em CSV, TXT (texto estruturado) ou um pandas.DataFrame
- Saída: arquivos salvos em `reports/` com timestamp e nome do dataset

Dependências:
- pandas, numpy (opcional), matplotlib, openpyxl, reportlab

Observação:
- Todos os comentários estão em português para facilitar a auditoria e manutenção.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Importações de bibliotecas de dados e gráficos
import pandas as pd
import numpy as np
import matplotlib

# Utilizamos backend 'Agg' para permitir geração de gráficos em ambientes headless
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Bibliotecas para Excel (openpyxl) e PDF (reportlab)
from openpyxl.drawing.image import Image as OpenpyxlImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
)


# ===============================
# Utilitários e constantes
# ===============================

# Mapeamento de sinônimos para colunas canônicas
# Isso permite aceitar diferentes nomes vindos de ferramentas diversas
CANONICAL_COLUMNS = {
    "row": {"row", "linha", "row_index", "index", "lin"},
    "column": {"column", "col", "campo", "coluna"},
    "issue_type": {"issue_type", "tipo", "type", "categoria", "error", "erro"},
    "description": {"description", "descricao", "mensagem", "message", "details"},
    "expected": {"expected", "esperado"},
    "found": {"found", "encontrado", "valor"},
    "severity": {"severity", "severidade", "nivel"},
    "dataset": {"dataset", "dataset_name", "tabela", "origem"},
}

# Sugestões padrão para tipos de problema conhecidos
DEFAULT_SUGGESTIONS = {
    "missing_column": "Adicionar a coluna ausente ou alinhar o schema com a origem.",
    "null_value": "Preencher valores nulos, definir defaults ou ajustar regras de input.",
    "type_mismatch": "Converter tipos, revisar mapeamento e normalizar dados.",
    "duplicate": "Aplicar remoção de duplicatas com chave única e revisar origem.",
    "range_violation": "Validar limites de domínio e ajustar valores fora do intervalo.",
    "regex_mismatch": "Padronizar formato, revisar regex e limpeza de dados.",
    "foreign_key_violation": "Garantir integridade referencial e consistência com dimensões.",
    "primary_key_violation": "Revisar definição de chave primária e remover duplicatas.",
    "length_violation": "Adequar tamanho de campos, truncar/normalizar entrada conforme necessário.",
}

# ===============================
# Funções de normalização e parsing
# ===============================

def ensure_output_dir(output_dir: str) -> str:
    """Garante que o diretório de saída exista e retorna seu caminho absoluto."""
    abs_dir = os.path.abspath(output_dir)
    os.makedirs(abs_dir, exist_ok=True)
    return abs_dir


def _detect_canonical_name(col: str) -> Optional[str]:
    """Detecta o nome canônico de uma coluna a partir do mapeamento de sinônimos."""
    lower = col.strip().lower()
    for canonical, synonyms in CANONICAL_COLUMNS.items():
        if lower in synonyms:
            return canonical
    return None


def normalize_issue_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza o DataFrame de issues para colunas canônicas:
    ['row', 'column', 'issue_type', 'description', 'expected', 'found', 'severity', 'dataset'].

    - Colunas ausentes serão criadas com valores vazios.
    - Tipos de dados são suavemente convertidos quando possível.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "row", "column", "issue_type", "description", "expected", "found", "severity", "dataset"
        ])

    # Renomear colunas conforme mapeamento de sinônimos
    rename_map: Dict[str, str] = {}
    for col in df.columns:
        canon = _detect_canonical_name(str(col))
        if canon is not None:
            rename_map[col] = canon
    df = df.rename(columns=rename_map)

    # Criar colunas canônicas ausentes
    for col in ["row", "column", "issue_type", "description", "expected", "found", "severity", "dataset"]:
        if col not in df.columns:
            df[col] = ""

    # Padronizar tipos básicos
    if "row" in df.columns:
        # Tentar converter para inteiro quando possível
        with np.errstate(all="ignore"):
            df["row"] = pd.to_numeric(df["row"], errors="ignore")

    # Normalizar strings (strip)
    for col in ["column", "issue_type", "description", "expected", "found", "severity", "dataset"]:
        df[col] = df[col].astype(str).fillna("").map(lambda x: x.strip())

    # Substituir NaN por string vazia nas demais colunas
    df = df.fillna("")

    return df[["row", "column", "issue_type", "description", "expected", "found", "severity", "dataset"]]


def parse_csv_report(csv_path: str, encoding: str = "utf-8") -> pd.DataFrame:
    """Lê um relatório de validação em CSV e normaliza as colunas."""
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_path}")
    df = pd.read_csv(csv_path, encoding=encoding)
    return normalize_issue_dataframe(df)


# Regex simples para tentar extrair campos de linhas de texto estruturado
TEXT_LINE_PATTERNS = [
    # Formato chave=valor separados por vírgula
    re.compile(r"row\s*=\s*(?P<row>[^,\|]+).*?col(?:umn)?\s*=\s*(?P<column>[^,\|]+).*?type\s*=\s*(?P<issue_type>[^,\|]+).*?desc(?:ription)?\s*=\s*(?P<description>[^,\|]+)", re.IGNORECASE),
    # Formato com pipe
    re.compile(r"row\s*:\s*(?P<row>[^,\|]+)\s*\|\s*col(?:umn)?\s*:\s*(?P<column>[^,\|]+)\s*\|\s*type\s*:\s*(?P<issue_type>[^,\|]+)\s*\|\s*desc(?:ription)?\s*:\s*(?P<description>.+)", re.IGNORECASE),
]


def parse_text_report(txt_path: str, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Lê um relatório de validação em TXT e tenta extrair colunas canônicas
    usando regexes simples. É uma heurística para textos semiformatados.
    """
    if not os.path.isfile(txt_path):
        raise FileNotFoundError(f"Arquivo TXT não encontrado: {txt_path}")

    rows: List[Dict[str, str]] = []
    with open(txt_path, "r", encoding=encoding, errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            matched = None
            for pat in TEXT_LINE_PATTERNS:
                m = pat.search(line)
                if m:
                    matched = m
                    break
            if matched:
                row_val = matched.groupdict().get("row", "")
                column = matched.groupdict().get("column", "")
                issue_type = matched.groupdict().get("issue_type", "")
                description = matched.groupdict().get("description", "")
                rows.append({
                    "row": row_val,
                    "column": column,
                    "issue_type": issue_type,
                    "description": description,
                    "expected": "",
                    "found": "",
                    "severity": "",
                    "dataset": "",
                })
            else:
                # Se não casa, gravar a linha como descrição genérica
                rows.append({
                    "row": "",
                    "column": "",
                    "issue_type": "desconhecido",
                    "description": line,
                    "expected": "",
                    "found": "",
                    "severity": "",
                    "dataset": "",
                })

    df = pd.DataFrame(rows)
    return normalize_issue_dataframe(df)


# ===============================
# Sumarização e sugestões
# ===============================

def _guess_rows_checked(issues_df: pd.DataFrame) -> Optional[int]:
    """
    Tenta inferir o número de linhas checadas a partir da coluna 'row'.
    - Usa contagem de valores únicos como estimativa.
    - Se não for possível, retorna None.
    """
    if issues_df is None or issues_df.empty:
        return 0
    if "row" not in issues_df.columns:
        return None
    try:
        numeric_rows = pd.to_numeric(issues_df["row"], errors="coerce").dropna()
        if numeric_rows.empty:
            return None
        # Contagem de linhas únicas envolvidas em problemas (estimativa inferior)
        unique_count = int(numeric_rows.nunique())
        # Alternativa: usar máximo + 1 quando índices parecem 0-based
        max_val = int(numeric_rows.max())
        if max_val >= unique_count and max_val < unique_count * 10:
            # Heurística fraca para evitar números absurdos
            return max(unique_count, max_val + 1)
        return unique_count
    except Exception:
        return None


def generate_suggestion(issue_type: str, column: str = "") -> str:
    """Gera uma sugestão de correção baseada no tipo de issue."""
    key = (issue_type or "").strip().lower().replace(" ", "_")
    suggestion = DEFAULT_SUGGESTIONS.get(key)
    if suggestion:
        return suggestion
    # Sugestão genérica caso o tipo seja desconhecido
    if column:
        return f"Investigar causa raiz em '{column}' e padronizar regras de qualidade."
    return "Investigar causa raiz e padronizar regras de qualidade."


def attach_suggestions(issues_df: pd.DataFrame) -> pd.DataFrame:
    """Anexa uma coluna 'suggestion' ao DataFrame com recomendações de correção."""
    if issues_df is None or issues_df.empty:
        issues_df = pd.DataFrame(columns=["row", "column", "issue_type", "description", "expected", "found", "severity", "dataset"])  # noqa: E501
    issues_df = issues_df.copy()
    issues_df["suggestion"] = issues_df.apply(lambda r: generate_suggestion(str(r.get("issue_type", "")), str(r.get("column", ""))), axis=1)
    return issues_df


def summarize_issues(issues_df: pd.DataFrame, dataset_name: Optional[str] = None, rows_checked: Optional[int] = None) -> Dict:
    """
    Cria um dicionário de sumário com métricas principais do relatório.
    """
    now = datetime.now()
    issues_df = issues_df if issues_df is not None else pd.DataFrame()
    total_issues = int(len(issues_df))

    # Determinar dataset
    detected_dataset = None
    if not dataset_name and "dataset" in issues_df.columns:
        # Pegar o valor mais frequente como nome do dataset
        vc = issues_df["dataset"].astype(str).str.strip()
        vc = vc[vc != ""]
        if not vc.empty:
            detected_dataset = vc.value_counts().idxmax()
    dataset_name = dataset_name or detected_dataset or "dataset"

    # Determinar linhas checadas
    if rows_checked is None:
        rows_checked = _guess_rows_checked(issues_df)

    issues_by_type = {}
    if "issue_type" in issues_df.columns and not issues_df.empty:
        issues_by_type = issues_df["issue_type"].astype(str).str.strip().replace("", "desconhecido").value_counts().to_dict()  # noqa: E501

    top_columns = {}
    if "column" in issues_df.columns and not issues_df.empty:
        top_columns = issues_df["column"].astype(str).str.strip().replace("", "(vazio)").value_counts().head(10).to_dict()

    summary = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_name": dataset_name,
        "rows_checked": int(rows_checked) if rows_checked is not None else None,
        "total_issues": total_issues,
        "issues_by_type": issues_by_type,
        "top_columns": top_columns,
    }
    return summary


# ===============================
# Geração de gráficos
# ===============================

def make_issue_chart(issues_by_type: Dict[str, int], output_dir: str, dataset_name: str) -> str:
    """
    Cria um gráfico de barras com a contagem de issues por tipo e salva como PNG.
    Retorna o caminho do arquivo de imagem.
    """
    if not issues_by_type:
        issues_by_type = {"sem_registros": 1}

    labels = list(issues_by_type.keys())
    values = list(issues_by_type.values())

    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, values, color="#4C78A8")
    plt.title(f"Contagem de Issues por Tipo - {dataset_name}")
    plt.xlabel("Tipo de Issue")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=45, ha="right")
    # Adicionar rótulos acima das barras
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom")
    plt.tight_layout()

    ensure_output_dir(output_dir)
    img_path = os.path.join(output_dir, f"issues_by_type_{uuid.uuid4().hex}.png")
    plt.savefig(img_path, dpi=150)
    plt.close()
    return img_path


# ===============================
# Relatório Excel (openpyxl)
# ===============================

def generate_excel_report(issues_df: pd.DataFrame, summary: Dict, output_path: str, chart_path: Optional[str] = None) -> None:
    """
    Gera um arquivo Excel com abas:
    - Resumo: métricas principais
    - Por_Tipo: contagem de issues por tipo + sugestões
    - Detalhes: lista completa de issues com colunas canônicas e sugestão
    - Graficos: inserção de imagem do gráfico gerado pelo matplotlib
    """
    # Preparar dataframes auxiliares
    issues_by_type_df = pd.DataFrame([
        {"issue_type": k, "count": v, "suggestion": generate_suggestion(k)}
        for k, v in (summary.get("issues_by_type") or {}).items()
    ]).sort_values(by="count", ascending=False)

    summary_rows = [
        {"Métrica": "Dataset", "Valor": summary.get("dataset_name")},
        {"Métrica": "Timestamp", "Valor": summary.get("timestamp")},
        {"Métrica": "Linhas checadas", "Valor": summary.get("rows_checked")},
        {"Métrica": "Total de issues", "Valor": summary.get("total_issues")},
    ]
    summary_df = pd.DataFrame(summary_rows)

    # Garantir coluna de sugestão em detalhes
    if "suggestion" not in issues_df.columns:
        issues_df = attach_suggestions(issues_df)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Aba de Resumo
        summary_df.to_excel(writer, sheet_name="Resumo", index=False)

        # Aba por tipo
        if not issues_by_type_df.empty:
            issues_by_type_df.to_excel(writer, sheet_name="Por_Tipo", index=False)
        else:
            pd.DataFrame([{"info": "Sem issues"}]).to_excel(writer, sheet_name="Por_Tipo", index=False)

        # Aba de detalhes
        issues_df.to_excel(writer, sheet_name="Detalhes", index=False)

        # Aba de gráficos
        # Criar uma aba vazia e inserir a imagem
        pd.DataFrame([{"info": "Gráfico de issues por tipo"}]).to_excel(writer, sheet_name="Graficos", index=False)
        ws = writer.sheets.get("Graficos")
        if chart_path and os.path.isfile(chart_path):
            img = OpenpyxlImage(chart_path)
            # Inserir no topo da planilha
            ws.add_image(img, "A3")
        # writer salva automaticamente ao sair do contexto


# ===============================
# Relatório PDF (reportlab)
# ===============================

def _build_table(data: List[List], col_widths: Optional[List] = None, style: Optional[TableStyle] = None) -> Table:
    """Cria uma tabela reportlab com estilo padrão caso não seja fornecido."""
    table = Table(data, colWidths=col_widths)
    if style is None:
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ])
    table.setStyle(style)
    return table


def generate_pdf_report(issues_df: pd.DataFrame, summary: Dict, output_path: str, chart_path: Optional[str] = None, max_detail_rows: int = 50) -> None:
    """
    Gera um PDF com:
    - Capa com título, dataset e timestamp
    - Sumário de métricas
    - Tabela de issues por tipo
    - Imagem com gráfico de issues por tipo
    - Amostra dos detalhes (até max_detail_rows)
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)  # noqa: E501
    story: List = []

    styles = getSampleStyleSheet()
    title_style: ParagraphStyle = styles["Title"]
    normal_style: ParagraphStyle = styles["Normal"]
    h_style: ParagraphStyle = styles["Heading2"]

    # Capa
    title = f"Relatório de Validação de Dados - {summary.get('dataset_name')}"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Gerado em: {summary.get('timestamp')}", normal_style))
    story.append(Spacer(1, 0.6 * cm))

    # Sumário
    story.append(Paragraph("Visão Geral", h_style))
    summary_data = [
        ["Métrica", "Valor"],
        ["Dataset", summary.get("dataset_name")],
        ["Linhas checadas", summary.get("rows_checked")],
        ["Total de issues", summary.get("total_issues")],
    ]
    story.append(_build_table(summary_data, col_widths=[6 * cm, 10 * cm]))
    story.append(Spacer(1, 0.6 * cm))

    # Issues por tipo
    story.append(Paragraph("Issues por Tipo", h_style))
    ibt = summary.get("issues_by_type") or {}
    if ibt:
        type_table = [["Tipo", "Quantidade", "Sugestão"]]
        # ordenar por quantidade desc
        for k, v in sorted(ibt.items(), key=lambda kv: kv[1], reverse=True):
            type_table.append([k, v, generate_suggestion(k)])
        story.append(_build_table(type_table, col_widths=[6 * cm, 3 * cm, 7 * cm]))
    else:
        story.append(Paragraph("Sem issues registradas.", normal_style))
    story.append(Spacer(1, 0.6 * cm))

    # Gráfico
    if chart_path and os.path.isfile(chart_path):
        story.append(Paragraph("Gráfico de Issues por Tipo", h_style))
        story.append(Spacer(1, 0.2 * cm))
        story.append(RLImage(chart_path, width=16 * cm, height=8 * cm))
        story.append(Spacer(1, 0.6 * cm))

    # Detalhes (amostra)
    story.append(Paragraph(f"Detalhes (primeiros {max_detail_rows} registros)", h_style))
    if issues_df is not None and not issues_df.empty:
        sample = issues_df.copy().head(max_detail_rows)
        # Selecionar colunas principais
        cols = [c for c in ["row", "column", "issue_type", "description", "expected", "found", "severity", "suggestion"] if c in sample.columns]  # noqa: E501
        # Truncar textos longos para caber no PDF
        def _trunc(x: str, n: int = 120) -> str:
            s = str(x)
            return s if len(s) <= n else s[: n - 1] + "…"
        sample = sample[cols].astype(str).applymap(lambda x: _trunc(x))
        detail_data = [cols] + sample.values.tolist()
        story.append(_build_table(detail_data))
    else:
        story.append(Paragraph("Sem detalhes para exibir.", normal_style))

    # Construir PDF
    doc.build(story)


# ===============================
# API pública e CLI
# ===============================

def generate_reports_from_dataframe(
    issues_df: pd.DataFrame,
    dataset_name: Optional[str] = None,
    rows_checked: Optional[int] = None,
    output_dir: str = "reports",
) -> Tuple[str, str]:
    """
    API pública: a partir de um DataFrame de issues, gera Excel e PDF e retorna os caminhos.
    """
    output_dir = ensure_output_dir(output_dir)

    # Normalizar, sugerir e sumarizar
    issues_df = normalize_issue_dataframe(issues_df)
    issues_df = attach_suggestions(issues_df)
    summary = summarize_issues(issues_df, dataset_name=dataset_name, rows_checked=rows_checked)

    # Nome de arquivos com timestamp
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_dataset = re.sub(r"[^a-zA-Z0-9_-]+", "_", summary["dataset_name"]) or "dataset"
    excel_path = os.path.join(output_dir, f"validacao_{safe_dataset}_{ts}.xlsx")
    pdf_path = os.path.join(output_dir, f"validacao_{safe_dataset}_{ts}.pdf")

    # Gráfico
    chart_path = make_issue_chart(summary.get("issues_by_type") or {}, output_dir, summary["dataset_name"])

    # Gerar relatórios
    generate_excel_report(issues_df, summary, excel_path, chart_path)
    generate_pdf_report(issues_df, summary, pdf_path, chart_path)

    return excel_path, pdf_path


def _infer_dataset_name_from_path(path: str) -> str:
    """Infere nome do dataset a partir do nome do arquivo."""
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name


def main(argv: Optional[List[str]] = None) -> int:
    """CLI para gerar relatórios a partir de CSV ou TXT."""
    parser = argparse.ArgumentParser(
        description=(
            "Gera relatórios Excel e PDF de validação/qualidade de dados a partir de CSV/TXT. "
            "Também pode ser usado como biblioteca para DataFrame."
        )
    )
    parser.add_argument("--csv", dest="csv_path", type=str, default=None, help="Caminho para o relatório CSV de issues")
    parser.add_argument("--txt", dest="txt_path", type=str, default=None, help="Caminho para o relatório TXT de issues")
    parser.add_argument("--encoding", dest="encoding", type=str, default="utf-8", help="Encoding do arquivo de entrada")
    parser.add_argument("--dataset-name", dest="dataset_name", type=str, default=None, help="Nome do dataset (opcional)")
    parser.add_argument("--rows-checked", dest="rows_checked", type=int, default=None, help="Número de linhas checadas (opcional)")
    parser.add_argument("--output-dir", dest="output_dir", type=str, default="reports", help="Diretório de saída (padrão: reports)")

    args = parser.parse_args(argv)

    if not args.csv_path and not args.txt_path:
        parser.error("Forneça --csv ou --txt como entrada do relatório de validação.")

    output_dir = ensure_output_dir(args.output_dir)

    # Carregar issues
    if args.csv_path:
        issues_df = parse_csv_report(args.csv_path, encoding=args.encoding)
        dataset_name = args.dataset_name or _infer_dataset_name_from_path(args.csv_path)
    else:
        issues_df = parse_text_report(args.txt_path, encoding=args.encoding)
        dataset_name = args.dataset_name or _infer_dataset_name_from_path(args.txt_path)

    # Gerar relatórios
    excel_path, pdf_path = generate_reports_from_dataframe(
        issues_df=issues_df,
        dataset_name=dataset_name,
        rows_checked=args.rows_checked,
        output_dir=output_dir,
    )

    print(f"Relatórios gerados:\n- Excel: {excel_path}\n- PDF:   {pdf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
