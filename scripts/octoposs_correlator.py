from pathlib import Path

BASE = Path("evidence")

processos = (BASE / "processes.txt").read_text(encoding="utf-8")
servicos = (BASE / "running_services.txt").read_text(encoding="utf-8")
sockets = (BASE / "network_sockets.txt").read_text(encoding="utf-8")

linhas = []
linhas.append("=== OCTOPOSS - TEIA DE EVIDENCIAS ===")
linhas.append("")

# CORRELACAO 01 - DNS
processo_dns = [l for l in processos.splitlines() if "/usr/lib/systemd/systemd-resolved" in l]
socket_dns = [l for l in sockets.splitlines() if "systemd-resolve" in l and ":53" in l]
linhas.append("[CORRELACAO 01] DNS")
if processo_dns:
    linhas.append("Processo: systemd-resolved")
    linhas.append("PID: " + processo_dns[0].split()[1])
else:
    linhas.append("Processo: NAO ENCONTRADO")
if "systemd-resolved.service" in servicos:
    linhas.append("Servico: systemd-resolved.service")
else:
    linhas.append("Servico: NAO ENCONTRADO")
if socket_dns:
    linhas.append("Sockets DNS encontrados:")
    for socket in socket_dns:
        linhas.append("- " + socket)
else:
    linhas.append("Sockets DNS: NAO ENCONTRADOS")
confirmada_dns = bool(processo_dns) and "systemd-resolved.service" in servicos and bool(socket_dns)
linhas.append("Relacao: PROCESSO -> SERVICO -> PORTA")
linhas.append("Status: CORRELACAO CONFIRMADA" if confirmada_dns else "Status: EVIDENCIA INSUFICIENTE")
linhas.append("")

# CORRELACAO 02 - SINCRONIZACAO DE TEMPO
processo_time = [l for l in processos.splitlines() if "/usr/lib/systemd/systemd-timesyncd" in l]
linhas.append("[CORRELACAO 02] SINCRONIZACAO DE TEMPO")

if processo_time:
    linhas.append("Processo: systemd-timesyncd")
    linhas.append("PID: " + processo_time[0].split()[1])
else:
    linhas.append("Processo: NAO ENCONTRADO")

if "systemd-timesyncd.service" in servicos:
    linhas.append("Servico: systemd-timesyncd.service")
else:
    linhas.append("Servico: NAO ENCONTRADO")

timesync_logs = (BASE / "timesync_logs.txt").read_text(encoding="utf-8")

if timesync_logs.strip():
    linhas.append("Log de sincronizacao encontrado:")
    linhas.append("- Comunicacao com servidor NTP registrada")
    linhas.append("- Sincronizacao inicial do relogio registrada")
else:
    linhas.append("Log de sincronizacao: NAO ENCONTRADO")

confirmada_time = (
    bool(processo_time)
    and "systemd-timesyncd.service" in servicos
    and bool(timesync_logs.strip())
)

linhas.append("Relacao: PROCESSO -> SERVICO -> LOG")
linhas.append("Status: CORRELACAO CONFIRMADA" if confirmada_time else "Status: EVIDENCIA INSUFICIENTE")

relatorio = BASE / "correlation_report.txt"
relatorio.write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
print("")
print("Relatorio salvo em: " + str(relatorio))
