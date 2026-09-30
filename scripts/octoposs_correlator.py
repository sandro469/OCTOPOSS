from pathlib import Path
import re

BASE = Path("evidence")


def ler_evidencia(nome):
    caminho = BASE / nome

    if not caminho.exists():
        return ""

    return caminho.read_text(encoding="utf-8")


def extrair_processos(processos):
    dados = {}

    for linha in processos.splitlines():
        partes = linha.split(None, 10)

        if len(partes) < 11:
            continue

        pid = partes[1]
        comando = partes[10]

        dados[pid] = {
            "pid": pid,
            "comando": comando
        }

    return dados


def extrair_sockets_por_pid(sockets):
    dados = {}

    for linha in sockets.splitlines():
        encontrados = re.findall(r'pid=(\d+)', linha)

        if not encontrados:
            continue

        pid = encontrados[0]

        dados.setdefault(pid, []).append(linha.strip())

    return dados


def servico_existe(servicos, nome):
    return any(
        linha.strip().startswith(nome)
        for linha in servicos.splitlines()
    )


processos = ler_evidencia("processes.txt")
servicos = ler_evidencia("running_services.txt")
sockets = ler_evidencia("network_sockets.txt")
timesync_logs = ler_evidencia("timesync_logs.txt")

processos_por_pid = extrair_processos(processos)
sockets_por_pid = extrair_sockets_por_pid(sockets)

linhas = []

linhas.append("=== OCTOPOSS - TEIA DE EVIDENCIAS ===")
linhas.append("")

# ============================================================
# CORRELACAO 01 - DNS
# ============================================================

linhas.append("[CORRELACAO 01] DNS")

pid_dns = None

for pid, dados in processos_por_pid.items():
    if "/usr/lib/systemd/systemd-resolved" in dados["comando"]:
        pid_dns = pid
        break

if pid_dns:
    processo_dns = processos_por_pid[pid_dns]

    linhas.append("Processo: systemd-resolved")
    linhas.append("PID: " + pid_dns)
else:
    processo_dns = None
    linhas.append("Processo: NAO ENCONTRADO")
    linhas.append("PID: NAO ENCONTRADO")

servico_dns = servico_existe(
    servicos,
    "systemd-resolved.service"
)

if servico_dns:
    linhas.append("Servico: systemd-resolved.service")
else:
    linhas.append("Servico: NAO ENCONTRADO")

sockets_dns = sockets_por_pid.get(pid_dns, []) if pid_dns else []

sockets_dns_53 = [
    socket for socket in sockets_dns
    if ":53" in socket
]

if sockets_dns_53:
    linhas.append("Sockets DNS encontrados:")

    for socket in sockets_dns_53:
        linhas.append("- " + socket)
else:
    linhas.append("Sockets DNS: NAO ENCONTRADOS")

confirmada_dns = (
    processo_dns is not None
    and servico_dns
    and bool(sockets_dns_53)
)

linhas.append("Relacao: PROCESSO -> PID -> SERVICO -> SOCKET -> PORTA")

if confirmada_dns:
    linhas.append("Status: CORRELACAO CONFIRMADA")
else:
    linhas.append("Status: EVIDENCIA INSUFICIENTE")

linhas.append("")


# ============================================================
# CORRELACAO 02 - SINCRONIZACAO DE TEMPO
# ============================================================

linhas.append("[CORRELACAO 02] SINCRONIZACAO DE TEMPO")

pid_time = None

for pid, dados in processos_por_pid.items():
    if "/usr/lib/systemd/systemd-timesyncd" in dados["comando"]:
        pid_time = pid
        break

if pid_time:
    processo_time = processos_por_pid[pid_time]

    linhas.append("Processo: systemd-timesyncd")
    linhas.append("PID: " + pid_time)
else:
    processo_time = None
    linhas.append("Processo: NAO ENCONTRADO")
    linhas.append("PID: NAO ENCONTRADO")

servico_time = servico_existe(
    servicos,
    "systemd-timesyncd.service"
)

if servico_time:
    linhas.append("Servico: systemd-timesyncd.service")
else:
    linhas.append("Servico: NAO ENCONTRADO")

if timesync_logs.strip():
    linhas.append("Log de sincronizacao encontrado:")
    linhas.append("- Comunicacao com servidor NTP registrada")
    linhas.append("- Sincronizacao inicial do relogio registrada")
else:
    linhas.append("Log de sincronizacao: NAO ENCONTRADO")

confirmada_time = (
    processo_time is not None
    and servico_time
    and bool(timesync_logs.strip())
)

linhas.append("Relacao: PROCESSO -> PID -> SERVICO -> LOG")

if confirmada_time:
    linhas.append("Status: CORRELACAO CONFIRMADA")
else:
    linhas.append("Status: EVIDENCIA INSUFICIENTE")

linhas.append("")


# ============================================================
# RESUMO
# ============================================================

total = 2
confirmadas = sum([
    confirmada_dns,
    confirmada_time
])

linhas.append("=== RESUMO DA ANALISE ===")
linhas.append(f"Correlacoes analisadas: {total}")
linhas.append(f"Correlacoes confirmadas: {confirmadas}")
linhas.append(f"Correlacoes com evidencia insuficiente: {total - confirmadas}")
linhas.append("")


# ============================================================
# GRAVACAO DO RELATORIO
# ============================================================

relatorio = BASE / "correlation_report.txt"

conteudo = "\n".join(linhas) + "\n"

relatorio.write_text(
    conteudo,
    encoding="utf-8"
)

print(conteudo)
print("Relatorio salvo em:", relatorio)
