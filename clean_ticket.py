#!/usr/bin/env python3
"""
Utility to clean helpdesk ticket responses and extract only the meaningful answer text.

Usage examples:

  python3 clean_ticket.py --text "CONCLUSÃO: CAROLINE CONCEICAO 01/07/2025 10:04 SENHA ENVIADA VIA TEAMS TICKET CRIADO POR X EM: 7/1/2025 8:31 AM"

  python3 clean_ticket.py --file sample_input.txt --show-score

This script applies a set of regex-based heuristics that remove metadata like
agent names, timestamps, and creation/audit trails such as "TICKET CRIADO POR ...".
It then returns the most likely response body.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass


DATE_RE = r"\b\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}\b"
TIME_RE = r"\b\d{1,2}:\d{2}(?:\s?(?:AM|PM))?\b"


@dataclass
class CleanResult:
    cleaned_text: str
    quality_score: int | None = None


def _normalize_whitespace(text: str) -> str:
    # Normalize newlines and collapse multiple spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _looks_like_name_timestamp_line(line: str) -> bool:
    # Heuristic: uppercase name(s) followed by a date and time
    if not re.search(DATE_RE, line):
        return False
    if not re.search(TIME_RE, line):
        return False
    # Many uppercase letters/spaces until a date
    return bool(re.search(r"^[A-ZÁÉÍÓÚÃÕÇ ]{3,}\s+" + DATE_RE, line))


def clean_ticket_response(raw_text: str) -> str:
    """Return only the likely human response message.

    The function is conservative and aims to remove:
    - Leading agent headers (name + date/time)
    - Labels like "CONCLUSÃO:", "RESPOSTA:", etc.
    - Creation/audit tails like "TICKET CRIADO POR ... EM: <data> <hora>"
    - Naked date/time tokens left inside the sentence
    """

    if not raw_text:
        return ""

    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove anything after creation trail phrases (often appended automatically)
    text = re.sub(
        r"\b(?:TICKET|CHAMADO)\s+CRIADO[\s\S]*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Split into lines to filter headers
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    kept_lines: list[str] = []
    for ln in lines:
        # Drop lines that look like agent header with timestamps
        if _looks_like_name_timestamp_line(ln):
            continue

        # Remove common labels at the beginning
        ln = re.sub(r"\bCONCLUS[ÃA]O[:\-]?\s*", "", ln, flags=re.IGNORECASE)
        ln = re.sub(r"\bRESPOSTA[:\-]?\s*", "", ln, flags=re.IGNORECASE)
        ln = re.sub(r"\bATUALIZA(?:C|Ç)[AÃ]O[:\-]?\s*", "", ln, flags=re.IGNORECASE)

        # Trim trailing "EM: <date> <time>" fragments if present
        ln = re.sub(
            rf"\bEM[: ]+{DATE_RE}(?:\s+{TIME_RE})?\b",
            "",
            ln,
            flags=re.IGNORECASE,
        )

        # Remove orphan date/time tokens inside the sentence
        ln = re.sub(DATE_RE, "", ln)
        ln = re.sub(TIME_RE, "", ln, flags=re.IGNORECASE)

        # Remove trailing creator attributions like "POR <NAME>" when left alone
        ln = re.sub(r"\bPOR\s+[A-ZÁÉÍÓÚÃÕÇ ]{3,}$", "", ln, flags=re.IGNORECASE)

        # Cleanup leftover punctuation and spacing
        ln = re.sub(r"\s{2,}", " ", ln).strip(" -,:;.")
        if ln:
            kept_lines.append(ln)

    if not kept_lines:
        return ""

    candidate_text = " ".join(kept_lines)

    # Prefer the longest sentence that does not contain audit words
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", candidate_text) if s.strip()]
    if sentences:
        filtered = [s for s in sentences if not re.search(r"\b(CRIADO|ABERTO|LOG|AUDIT)\b", s, re.IGNORECASE)]
        if filtered:
            candidate_text = max(filtered, key=len)
        else:
            candidate_text = max(sentences, key=len)

    return _normalize_whitespace(candidate_text)


def score_quality_pt(text: str) -> int:
    """Return a very simple quality score (0-100) for a Portuguese response.

    This is a placeholder scoring function with naive heuristics:
    - Penalize messages that are extremely short or all-caps
    - Reward messages that include common action verbs
    - Clamp to [0, 100]
    """
    if not text:
        return 0

    score = 50

    # Action verbs common in ticket resolutions
    verbs = [
        "enviado",
        "enviada",
        "liberado",
        "liberada",
        "resolvido",
        "corrigido",
        "ajustado",
        "realizado",
        "configurado",
        "orientado",
        "feito",
        "concluido",
        "concluida",
        "concluído",
        "concluída",
    ]

    if any(re.search(rf"\b{v}\b", text, flags=re.IGNORECASE) for v in verbs):
        score += 15

    # Length heuristics
    if len(text) < 10:
        score -= 25
    elif len(text) < 25:
        score -= 10
    elif len(text) > 200:
        score -= 10

    # All caps penalty if most characters are uppercase letters
    letters = re.findall(r"[A-Za-zÁÉÍÓÚÃÕÇ]", text)
    uppers = [c for c in letters if c.isupper()]
    if letters and (len(uppers) / max(1, len(letters))) > 0.85:
        score -= 15

    # Excessive punctuation
    if text.count("!") >= 3:
        score -= 10

    return max(0, min(100, score))


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Clean ticket response text and optionally score it.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", type=str, help="Raw text to clean")
    src.add_argument("--file", type=str, help="Path to a file containing raw text")
    parser.add_argument("--show-score", action="store_true", help="Print a simple quality score (0-100)")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = args.text

    cleaned = clean_ticket_response(raw)
    print(cleaned)

    if args.show_score:
        print(f"\n[score] {score_quality_pt(cleaned)}")


if __name__ == "__main__":
    run_cli()

