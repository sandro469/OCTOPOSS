from pathlib import Path
import subprocess
from datetime import datetime

BASE = Path("evidence")


def coletar_comando(comando, arquivo):
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    caminho = BASE / arquivo
    caminho.write_text(resultado.stdout, encoding="utf-8")

    print(f"[OK] {arquivo}")


print("🐙 OCTOPOSS - COLETOR DE EVIDÊNCIAS")
print("=" * 40)
print("Início:", datetime.now().astimezone().isoformat())
print()

BASE.mkdir(exist_ok=True)

# 1. PROCESSOS
coletar_comando(
    ["ps", "aux"],
    "processes.txt"
)

# 2. SERVIÇOS ATIVOS
coletar_comando(
    [
        "systemctl",
        "list-units",
        "--type=service",
        "--state=running"
    ],
    "running_services.txt"
)

# 3. SOCKETS DE REDE
coletar_comando(
    ["ss", "-tulnp"],
    "network_sockets.txt"
)

print()
print("🐙 COLETA CONCLUÍDA.")
print("Evidências atualizadas em:", BASE)

# 4. LOGS DE SINCRONIZACAO DE TEMPO
coletar_comando(
    [
        "journalctl",
        "-u",
        "systemd-timesyncd.service",
        "--no-pager",
        "-n",
        "20"
    ],
    "timesync_logs.txt"
)

# 5. LOGS DE AUTENTICACAO
coletar_comando(
    [
        "journalctl",
        "--no-pager",
        "-n",
        "50"
    ],
    "auth_logs.txt"
)
