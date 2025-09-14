#!/usr/bin/env python3
import csv
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# =======================
# CONFIGURAÇÕES SIMPLES
# =======================
# Preencha as variáveis abaixo e execute este script diretamente.
# Observação de segurança: este método armazena usuário e senha em texto claro.
# Use apenas em ambientes controlados.

CLIENT_ID = "PREENCHA_CLIENT_ID"
SHAREPOINT_USERNAME = "usuario@seu-dominio.onmicrosoft.com"
SHAREPOINT_PASSWORD = "sua_senha_forte"

SHAREPOINT_SITE_URL = "https://escolatrabalhador4.sharepoint.com/sites/portalservicos"
SHAREPOINT_LIST_TITLE = "reposta_curadoria"

# Suporta {date} no formato YYYYMMDD
OUTPUT_PATH = "output/sharepoint_lista_{date}.csv"

# Lista opcional de campos internos para exportar (ex.: ["Title", "Created", "Modified"]).
# Se vazio/None, exporta todos os campos não-sistêmicos.
FIELDS: Optional[List[str]] = None

# Upload para pasta no SharePoint (biblioteca de documentos)
UPLOAD_TO_SHAREPOINT = True
DEST_DRIVE_NAME = "Documents"  # nome da library
DEST_FOLDER_PATH = "Exportacoes/Curadoria"  # pastas serão criadas se não existirem
DEST_FILE_NAME = "lista_curadoria_{date}.csv"


def get_graph_token_with_password(tenant: str, client_id: str, username: str, password: str) -> str:
    import requests

    token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    resp = requests.post(token_url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def extract_tenant_from_site(site_url: str) -> str:
    host = site_url.split("//")[-1].split("/")[0]
    tenant = host.split(".")[0]
    return f"{tenant}.onmicrosoft.com"


def graph_get(url: str, token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    import requests

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def graph_post(url: str, token: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
    import requests

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=json_body, timeout=60)
    resp.raise_for_status()
    return resp.json()


def graph_put_bytes(url: str, token: str, content_bytes: bytes, content_type: str = "application/octet-stream") -> Dict[str, Any]:
    import requests

    headers = {"Authorization": f"Bearer {token}", "Content-Type": content_type}
    resp = requests.put(url, headers=headers, data=content_bytes, timeout=300)
    resp.raise_for_status()
    return resp.json()


def resolve_site_and_list_ids(site_url: str, list_title: str, token: str) -> Dict[str, str]:
    parts = site_url.split("//", 1)[-1]
    hostname, path = parts.split("/", 1)
    path = "/" + path
    site_info = graph_get(f"https://graph.microsoft.com/v1.0/sites/{hostname}:%7Bpath%7D".replace("%7Bpath%7D", path), token)
    site_id = site_info["id"]

    lists_resp = graph_get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists", token)
    list_id = None
    for item in lists_resp.get("value", []):
        if item.get("displayName") == list_title:
            list_id = item.get("id")
            break
    if not list_id:
        print(f"Lista '{list_title}' não encontrada no site.", file=sys.stderr)
        sys.exit(3)
    return {"site_id": site_id, "list_id": list_id}


def fetch_list_items(site_id: str, list_id: str, token: str, selected_fields: Optional[List[str]]) -> List[Dict[str, Any]]:
    base_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items"
    params = {"expand": "fields"}
    items: List[Dict[str, Any]] = []
    while True:
        data = graph_get(base_url, token, params=params)
        for entry in data.get("value", []):
            fields = entry.get("fields", {})
            if selected_fields:
                row = {key: fields.get(key) for key in selected_fields}
            else:
                row = {k: v for k, v in fields.items() if not k.startswith("_")}
            items.append(row)
        next_link = data.get("@odata.nextLink")
        if not next_link:
            break
        base_url = next_link
        params = None
    return items


def write_csv(rows: List[Dict[str, Any]], output_path: str) -> None:
    if not rows:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            pass
        return

    headers: List[str] = list(rows[0].keys())
    for r in rows[1:]:
        for k in r.keys():
            if k not in headers:
                headers.append(k)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("; ".join(v) if isinstance(v, list) else v) for k, v in r.items()})


def get_drive_id_for_site(site_id: str, token: str, preferred_drive_name: Optional[str]) -> str:
    if not preferred_drive_name or preferred_drive_name.strip() == "" or preferred_drive_name.strip().lower() == "documents":
        data = graph_get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive", token)
        return data["id"]
    drives = graph_get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives", token)
    for dr in drives.get("value", []):
        if dr.get("name", "").lower() == preferred_drive_name.strip().lower():
            return dr["id"]
    data = graph_get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive", token)
    return data["id"]


def try_get_drive_item_by_path(drive_id: str, path: str, token: str) -> Optional[Dict[str, Any]]:
    import requests
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:{'/' + path if path else ''}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=60)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def ensure_folder_path_exists(drive_id: str, folder_path: str, token: str) -> Dict[str, Any]:
    normalized = folder_path.strip("/")
    if normalized == "":
        return graph_get(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root", token)
    existing = try_get_drive_item_by_path(drive_id, normalized, token)
    if existing is not None:
        return existing
    parts = normalized.split("/")
    parent_id = graph_get(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root", token)["id"]
    current_path: List[str] = []
    for part in parts:
        current_path.append(part)
        sub_path = "/".join(current_path)
        found = try_get_drive_item_by_path(drive_id, sub_path, token)
        if found is None:
            created = graph_post(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_id}/children", token, {
                "name": part,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "retain",
            })
            parent_id = created["id"]
        else:
            parent_id = found["id"]
    return graph_get(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_id}", token)


def upload_csv_to_sharepoint(site_id: str, token: str, local_path: str, drive_name: Optional[str], folder_path: Optional[str], dest_file_name: Optional[str]) -> Dict[str, Any]:
    drive_id = get_drive_id_for_site(site_id, token, drive_name)
    folder_item = ensure_folder_path_exists(drive_id, folder_path or "", token)
    file_name = dest_file_name or os.path.basename(local_path)
    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_item['id']}:/" + file_name + ":/content"
    with open(local_path, "rb") as fh:
        content = fh.read()
    return graph_put_bytes(upload_url, token, content, content_type="text/csv")


def main() -> None:
    tenant = extract_tenant_from_site(SHAREPOINT_SITE_URL)

    try:
        token = get_graph_token_with_password(tenant, CLIENT_ID, SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
    except Exception as e:
        print(f"Falha ao obter token (username/password). Verifique CLIENT_ID, usuário/senha e políticas ROPC/MFA. Detalhes: {e}", file=sys.stderr)
        sys.exit(2)

    ids = resolve_site_and_list_ids(SHAREPOINT_SITE_URL, SHAREPOINT_LIST_TITLE, token)
    rows = fetch_list_items(ids["site_id"], ids["list_id"], token, FIELDS)

    date_str = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_PATH.replace("{date}", date_str)
    write_csv(rows, output_path)
    print(f"Exportado {len(rows)} registros para {output_path}")

    if UPLOAD_TO_SHAREPOINT:
        dest_name = (DEST_FILE_NAME or os.path.basename(output_path)).replace("{date}", date_str)
        uploaded = upload_csv_to_sharepoint(ids["site_id"], token, output_path, DEST_DRIVE_NAME, DEST_FOLDER_PATH, dest_name)
        print(f"Upload concluído em SharePoint: {uploaded.get('webUrl', '')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrompido.", file=sys.stderr)
        sys.exit(130)
