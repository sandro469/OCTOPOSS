from pathlib import Path
import re

BASE = Path(__file__).resolve().parent.parent
EVIDENCE = BASE / "evidence"


def ler_evidencia(nome):
    caminho = EVIDENCE / nome
    if not caminho.exists():
        return ""
    return caminho.read_text(encoding="utf-8")


def extrair_processos(processos):
    resultado = {}

    for linha in processos.splitlines():
        partes = linha.split(None, 10)

        if len(partes) < 11:
            continue

        try:
            pid = int(partes[1])
        except ValueError:
            continue

        resultado[pid] = partes[10]

    return resultado


def extrair_sockets_por_pid(sockets, pid):
    encontrados = []

    for linha in sockets.splitlines():
        if f"pid={pid}," in linha or f"pid={pid})" in linha:
            encontrados.append(linha.strip())

    return encontrados


def servico_existe(servicos, nome):
    return any(
        linha.strip().startswith(nome)
        for linha in servicos.splitlines()
    )


def nome_processo(comando):
    if not comando:
        return ""

    return Path(comando.split()[0]).name


def mapear_processos_servicos(processos_por_pid, servicos):
    mapeamentos = []

    for linha in servicos.splitlines():
        partes = linha.split()

        if len(partes) < 4:
            continue

        unidade = partes[0]

        if not unidade.endswith(".service"):
            continue

        estado = partes[2]
        subestado = partes[3]
        nome = unidade[:-8]

        for pid, comando in processos_por_pid.items():
            processo = nome_processo(comando)

            if processo == nome:
                mapeamentos.append({
                    "processo": processo,
                    "pid": pid,
                    "servico": unidade,
                    "estado": estado,
                    "subestado": subestado
                })

    return mapeamentos


def analisar_sockets(sockets):
    resultados = []

    for linha in sockets.splitlines():
        if not linha.startswith(("tcp ", "udp ")):
            continue

        pid = re.search(r"pid=(\d+)", linha)
        processo = re.search(r'\(\("([^"]+)"', linha)

        if pid and processo:
            resultados.append({
                "status": "IDENTIFICADO",
                "processo": processo.group(1),
                "pid": pid.group(1),
                "socket": linha.strip()
            })
        else:
            resultados.append({
                "status": "SEM_PROCESSO",
                "processo": None,
                "pid": None,
                "socket": linha.strip()
            })

    return resultados


def main():

    print("=== OCTOPOSS - TEIA DE EVIDENCIAS ===")
    print()

    processos = ler_evidencia("processes.txt")
    servicos = ler_evidencia("running_services.txt")
    sockets = ler_evidencia("network_sockets.txt")
    timesync_logs = ler_evidencia("timesync_logs.txt")

    processos_por_pid = extrair_processos(processos)

    confirmadas = 0
    insuficientes = 0

    relatorio = []

    # ----------------------------------------------------------
    # CORRELACAO 01 - DNS
    # ----------------------------------------------------------

    print("[CORRELACAO 01] DNS")

    dns_pid = None

    for pid, comando in processos_por_pid.items():
        if "systemd-resolved" in comando:
            dns_pid = pid
            break

    dns_servico = "systemd-resolved.service"
    dns_sockets = []

    if dns_pid is not None:
        dns_sockets = extrair_sockets_por_pid(
            sockets,
            dns_pid
        )

    print("Processo:", "systemd-resolved" if dns_pid else "NAO ENCONTRADO")
    print("PID:", dns_pid or "NAO ENCONTRADO")
    print("Servico:", dns_servico)
    print("Sockets DNS encontrados:")

    for socket in dns_sockets:
        print("-", socket)

    dns_ok = (
        dns_pid is not None
        and servico_existe(servicos, dns_servico)
        and len(dns_sockets) > 0
    )

    status = (
        "CORRELACAO CONFIRMADA"
        if dns_ok
        else "EVIDENCIA INSUFICIENTE"
    )

    if dns_ok:
        confirmadas += 1
    else:
        insuficientes += 1

    print("Relacao: PROCESSO -> PID -> SERVICO -> SOCKET -> PORTA")
    print("Status:", status)
    print()

    relatorio += [
        "[CORRELACAO 01] DNS",
        f"Processo: {'systemd-resolved' if dns_pid else 'NAO ENCONTRADO'}",
        f"PID: {dns_pid or 'NAO ENCONTRADO'}",
        f"Servico: {dns_servico}",
        "Sockets DNS encontrados:"
    ]

    relatorio += [f"- {x}" for x in dns_sockets]

    relatorio += [
        "Relacao: PROCESSO -> PID -> SERVICO -> SOCKET -> PORTA",
        f"Status: {status}",
        ""
    ]

    # ----------------------------------------------------------
    # CORRELACAO 02 - SINCRONIZACAO
    # ----------------------------------------------------------

    print("[CORRELACAO 02] SINCRONIZACAO DE TEMPO")

    time_pid = None

    for pid, comando in processos_por_pid.items():
        if "systemd-timesyncd" in comando:
            time_pid = pid
            break

    time_servico = "systemd-timesyncd.service"

    log_ok = (
        "NTP" in timesync_logs
        or "sincron" in timesync_logs.lower()
        or "clock" in timesync_logs.lower()
    )

    print("Processo:", "systemd-timesyncd" if time_pid else "NAO ENCONTRADO")
    print("PID:", time_pid or "NAO ENCONTRADO")
    print("Servico:", time_servico)

    if log_ok:
        print("Log de sincronizacao encontrado")
    else:
        print("Log de sincronizacao: NAO ENCONTRADO")

    time_ok = (
        time_pid is not None
        and servico_existe(servicos, time_servico)
        and log_ok
    )

    status = (
        "CORRELACAO CONFIRMADA"
        if time_ok
        else "EVIDENCIA INSUFICIENTE"
    )

    if time_ok:
        confirmadas += 1
    else:
        insuficientes += 1

    print("Relacao: PROCESSO -> PID -> SERVICO -> LOG")
    print("Status:", status)
    print()

    relatorio += [
        "[CORRELACAO 02] SINCRONIZACAO DE TEMPO",
        f"Processo: {'systemd-timesyncd' if time_pid else 'NAO ENCONTRADO'}",
        f"PID: {time_pid or 'NAO ENCONTRADO'}",
        f"Servico: {time_servico}",
        "Log de sincronizacao encontrado"
        if log_ok
        else "Log de sincronizacao: NAO ENCONTRADO",
        "Relacao: PROCESSO -> PID -> SERVICO -> LOG",
        f"Status: {status}",
        ""
    ]

    # ----------------------------------------------------------
    # CORRELACAO 03 - PROCESSOS -> SERVICOS
    # ----------------------------------------------------------

    print("[CORRELACAO 03] PROCESSOS -> SERVICOS")

    mapeamentos = mapear_processos_servicos(
        processos_por_pid,
        servicos
    )

    for item in mapeamentos:
        print(
            f"Processo: {item['processo']} | "
            f"PID: {item['pid']} | "
            f"Servico: {item['servico']} | "
            f"Estado: {item['estado']} | "
            f"Subestado: {item['subestado']}"
        )

    print("Mapeamentos encontrados:", len(mapeamentos))

    status = (
        "CORRELACAO CONFIRMADA"
        if mapeamentos
        else "EVIDENCIA INSUFICIENTE"
    )

    if mapeamentos:
        confirmadas += 1
    else:
        insuficientes += 1

    print("Relacao: PROCESSO -> PID -> SERVICO")
    print("Status:", status)
    print()

    relatorio += [
        "[CORRELACAO 03] PROCESSOS -> SERVICOS"
    ]

    for item in mapeamentos:
        relatorio.append(
            f"Processo: {item['processo']} | "
            f"PID: {item['pid']} | "
            f"Servico: {item['servico']} | "
            f"Estado: {item['estado']} | "
            f"Subestado: {item['subestado']}"
        )

    relatorio += [
        f"Mapeamentos encontrados: {len(mapeamentos)}",
        "Relacao: PROCESSO -> PID -> SERVICO",
        f"Status: {status}",
        ""
    ]

    # ----------------------------------------------------------
    # CORRELACAO 04 - SOCKETS
    # ----------------------------------------------------------

    print("[CORRELACAO 04] SOCKETS")

    sockets_analisados = analisar_sockets(sockets)

    identificados = [
        x for x in sockets_analisados
        if x["status"] == "IDENTIFICADO"
    ]

    sem_processo = [
        x for x in sockets_analisados
        if x["status"] == "SEM_PROCESSO"
    ]

    print("Sockets analisados:", len(sockets_analisados))
    print("Com processo identificado:", len(identificados))
    print("Sem processo identificado:", len(sem_processo))

    print()
    print("Sockets com processo:")

    for item in identificados:
        print(
            f"- Processo: {item['processo']} | "
            f"PID: {item['pid']}"
        )

    print()
    print("Sockets sem processo identificado:")

    for item in sem_processo:
        print("-", item["socket"])

    status = (
        "ANALISE CONCLUIDA"
        if sockets_analisados
        else "EVIDENCIA INSUFICIENTE"
    )

    if sockets_analisados:
        confirmadas += 1
    else:
        insuficientes += 1

    print()
    print("Relacao: SOCKET -> PROCESSO -> PID")
    print("Status:", status)
    print()

    relatorio += [
        "[CORRELACAO 04] SOCKETS",
        f"Sockets analisados: {len(sockets_analisados)}",
        f"Com processo identificado: {len(identificados)}",
        f"Sem processo identificado: {len(sem_processo)}",
        "",
        "Sockets com processo:"
    ]

    for item in identificados:
        relatorio.append(
            f"- Processo: {item['processo']} | "
            f"PID: {item['pid']} | "
            f"Socket: {item['socket']}"
        )

    relatorio += [
        "",
        "Sockets sem processo identificado:"
    ]

    for item in sem_processo:
        relatorio.append(f"- {item['socket']}")

    relatorio += [
        "",
        "Relacao: SOCKET -> PROCESSO -> PID",
        f"Status: {status}",
        ""
    ]

    # ----------------------------------------------------------
    # RESUMO
    # ----------------------------------------------------------

    print("=== RESUMO DA ANALISE ===")
    print("Correlacoes analisadas: 4")
    print("Correlacoes confirmadas:", confirmadas)
    print(
        "Correlacoes com evidencia insuficiente:",
        insuficientes
    )

    relatorio += [
        "=== RESUMO DA ANALISE ===",
        "Correlacoes analisadas: 4",
        f"Correlacoes confirmadas: {confirmadas}",
        f"Correlacoes com evidencia insuficiente: {insuficientes}"
    ]

    saida = EVIDENCE / "correlation_report.txt"

    saida.write_text(
        "\n".join(relatorio) + "\n",
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
