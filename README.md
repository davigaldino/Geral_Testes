## Exportar lista do SharePoint para CSV (via Microsoft Graph)

### Visão geral
Script em Python que autentica no Microsoft Graph, lê uma Lista do SharePoint e gera um CSV diário. Credenciais ficam em um arquivo `.env`, fora do código.

### Requisitos
- Python 3.9+
- App Registration no Entra ID com `CLIENT_ID` (obrigatório em qualquer método)
- Um método de autenticação:
  - username/password (para contas sem MFA) OU
  - client credentials (App Registration no Entra ID) com permissões de Graph para SharePoint Sites/Listas

### Configuração
1. Copie `.env.example` para `.env` e preencha:
```
AUTH_METHOD=username_password
SHAREPOINT_SITE_URL=https://escolatrabalhador4.sharepoint.com/sites/portalservicos
SHAREPOINT_LIST_TITLE=NomeDaLista
SHAREPOINT_USERNAME=usuario@seu-dominio.onmicrosoft.com
SHAREPOINT_PASSWORD=sua_senha_forte
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OUTPUT_PATH=output/sharepoint_lista_{date}.csv
# Opcional: FIELDS=Title,CampoInterno1,CampoInterno2
```
Para client credentials, defina `AUTH_METHOD=client_credentials` e forneça `CLIENT_ID` e `CLIENT_SECRET`.

Permissões sugeridas no Graph:
- Application (client credentials): `Sites.Read.All` (ou `Sites.ReadWrite.All`) + consentimento de admin
- Delegated (username/password/ROPC): `Sites.Read.All` (ou `Sites.ReadWrite.All`) — pode ser bloqueado por MFA

2. Instale dependências:
```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

### Uso
```
python sharepoint_export.py
```
Saída será criada em `output/` com data no nome.

#### Upload automático para SharePoint (opcional)
No `.env` defina:
```
UPLOAD_TO_SHAREPOINT=true
DEST_DRIVE_NAME=Documents
DEST_FOLDER_PATH=Exportacoes/Curadoria
DEST_FILE_NAME=lista_curadoria_{date}.csv
```
O script fará upload do CSV para a pasta indicada na document library do site.

### Teste rápido
1. Verifique o Python: `python -V`
2. Ative o venv e rode: `python sharepoint_export.py`
3. Confirme o CSV em `output/` e a contagem no terminal

### Agendamento diário (cron)
Abra o cron do usuário:
```
crontab -e
```
Exemplo para rodar às 06:00 todos os dias (ajuste caminhos):
```
0 6 * * * cd /caminho/para/workspace && . .venv/bin/activate && /usr/bin/python /caminho/para/workspace/sharepoint_export.py >> /caminho/para/workspace/output/cron.log 2>&1
```

### Windows (Task Scheduler)
1. Instale Python 3.9+ no Windows.
2. Crie uma venv (opcional, recomendado):
```
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```
3. Ajuste o `.env` com credenciais e habilite `UPLOAD_TO_SHAREPOINT=true` se quiser enviar o arquivo para a pasta do SharePoint.
4. Use o script PowerShell abaixo para execução e agendamento.

Crie `run_export.ps1`:
```
Param(
  [string]$ProjectDir = "$PSScriptRoot"
)
Set-Location $ProjectDir
if (Test-Path ".env") {
  Get-Content .env | ForEach-Object {
    if ($_ -match '^(?<k>[^#=]+)=(?<v>.*)$') {
      $k=$Matches['k'].Trim(); $v=$Matches['v']
      [System.Environment]::SetEnvironmentVariable($k,$v,"Process")
    }
  }
}
$python = Join-Path $ProjectDir ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) { $python = "python" }
& $python (Join-Path $ProjectDir "sharepoint_export.py")
```

Agendar no Task Scheduler:
- Action: `powershell.exe -ExecutionPolicy Bypass -File C:\caminho\para\projeto\run_export.ps1`
- Start in: `C:\caminho\para\projeto`
- Trigger diário às 06:00

### Agendamento com systemd (alternativa ao cron)
Crie `/etc/systemd/system/sharepoint-export.service`:
```
[Unit]
Description=Exporta lista do SharePoint para CSV
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/caminho/para/workspace
Environment=PYTHONUNBUFFERED=1
ExecStart=/caminho/para/workspace/.venv/bin/python /caminho/para/workspace/sharepoint_export.py
User=seu_usuario
Group=seu_grupo

[Install]
WantedBy=multi-user.target
```
Crie `/etc/systemd/system/sharepoint-export.timer`:
```
[Unit]
Description=Agendamento diário do export de SharePoint

[Timer]
OnCalendar=06:00
Persistent=true

[Install]
WantedBy=timers.target
```
Ative e inicie:
```
sudo systemctl daemon-reload
sudo systemctl enable --now sharepoint-export.timer
```

### Versão simples (usuário/senha dentro do script)
Arquivo: `sharepoint_export_simple.py`

1. Abra o arquivo e preencha no topo: `CLIENT_ID`, `SHAREPOINT_USERNAME`, `SHAREPOINT_PASSWORD`, `SHAREPOINT_SITE_URL`, `SHAREPOINT_LIST_TITLE`, e demais opções (upload, pasta, etc.).
2. Execute:
```
python sharepoint_export_simple.py
```
3. Para Windows, você pode agendar este arquivo no Task Scheduler da mesma forma (Action: `python C:\caminho\projeto\sharepoint_export_simple.py`).

Observação: esta variante guarda credenciais em texto claro; use apenas em ambientes controlados e restritos.

### Observações importantes
- Se sua conta usa MFA, use client credentials com permissões de aplicativo ou use um App com ROPC desaconselhado. Preferível client credentials.
- Para campos de pessoa, escolha FIELDS com o nome interno desejado (ex.: `Author`, `Editor`) ou adapte o script para expandir subpropriedades.
- O script exclui campos começando com `_` por padrão, a menos que `FIELDS` seja definido.
