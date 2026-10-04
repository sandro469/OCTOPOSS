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


def classificar_socket_orfao(socket, processos, servicos, timesync_logs):
    portas = re.findall(r":(\d+)(?:\s|$)", socket)

    if not portas:
        return "EVIDENCIA INSUFICIENTE", "Porta nao identificada"

    porta = portas[-1]

    if porta == "323":
        if (
            "systemd-timesyncd" in processos
            and "systemd-timesyncd.service" in servicos
            and "timesyncd" in timesync_logs
        ):
            return (
                "CORRELACAO PARCIAL",
                "Timesyncd confirmado, mas o socket usa porta 323 enquanto os logs indicam NTP na porta 123"
            )

    if porta == "53":
        if (
            "systemd-resolved" in processos
            and "systemd-resolved.service" in servicos
        ):
            return (
                "CORRELACAO PARCIAL",
                "Servico DNS confirmado, mas nao foi encontrado vinculo direto entre este socket e um PID"
            )

    return "EVIDENCIA INSUFICIENTE", "Nenhum vinculo direto encontrado"

def criar_relacao(tipo, evidencias, status, confianca, justificativa):
    return {
        "tipo": tipo,
        "evidencias": evidencias,
        "status": status,
        "confianca": confianca,
        "justificativa": justificativa
    }

def analisar_relacoes(relacoes):
    resumo = {
        "total": len(relacoes),
        "confirmadas": 0,
        "parciais": 0,
        "insuficientes": 0,
        "analises_concluidas": 0,
        "atencao": []
    }

    for relacao in relacoes:
        status = relacao["status"]

        if status == "CORRELACAO CONFIRMADA":
            resumo["confirmadas"] += 1

        elif status == "CORRELACAO PARCIAL":
            resumo["parciais"] += 1
            resumo["atencao"].append(relacao)

        elif status == "EVIDENCIA INSUFICIENTE":
            resumo["insuficientes"] += 1
            resumo["atencao"].append(relacao)

        elif status == "ANALISE CONCLUIDA":
            resumo["analises_concluidas"] += 1

    return resumo


def main():
    relacoes = []


    print("=== OCTOPOSS - TENTACULOS DE EVIDENCIAS ===")
    print()

    processos = ler_evidencia("processes.txt")
    servicos = ler_evidencia("running_services.txt")
    sockets = ler_evidencia("network_sockets.txt")
    timesync_logs = ler_evidencia("timesync_logs.txt")

    processos_por_pid = extrair_processos(processos)

    confirmadas = 0
    parciais = 0
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
    relacoes.append(criar_relacao(
        "DNS",
        [
            "processes.txt",
            "running_services.txt",
            "network_sockets.txt"
        ],
        status,
        "ALTA" if dns_ok else "BAIXA",
        "systemd-resolved relacionado ao PID, servico e sockets DNS"
    ))
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
    relacoes.append(criar_relacao(
        "SINCRONIZACAO",
        [
            "processes.txt",
            "running_services.txt",
            "timesync_logs.txt"
        ],
        status,
        "ALTA" if time_ok else "BAIXA",
        "systemd-timesyncd relacionado ao PID, servico e log de sincronizacao"
    ))
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
    relacoes.append(criar_relacao(
        "PROCESSOS_SERVICOS",
        [
            "processes.txt",
            "running_services.txt"
        ],
        status,
        "ALTA" if len(mapeamentos) > 0 else "BAIXA",
        f"{len(mapeamentos)} mapeamento(s) de processo para servico encontrado(s)"
    ))
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
        pass
    else:
        insuficientes += 1

    print()
    print("Relacao: SOCKET -> PROCESSO -> PID")
    print("Status:", status)
    relacoes.append(criar_relacao(
        "SOCKETS",
        [
            "network_sockets.txt",
            "processes.txt"
        ],
        status,
        "ALTA" if len(sockets_analisados) > 0 else "BAIXA",
        f"{len(sockets_analisados)} socket(s) analisado(s), "
        f"{len(identificados)} com processo e "
        f"{len(sem_processo)} sem processo identificado"
    ))
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
    # CORRELACAO 05 - INVESTIGACAO DOS SOCKETS ORFAOS
    # ----------------------------------------------------------

    print("[CORRELACAO 05] INVESTIGACAO DOS SOCKETS ORFAOS")

    for item in sem_processo:
        status_orfao, motivo = classificar_socket_orfao(
            item["socket"],
            processos,
            servicos,
            timesync_logs
        )

        print()
        print("Socket:", item["socket"])
        print("Status:", status_orfao)
        print("Evidencia:", motivo)

        relacoes.append(criar_relacao(
            "SOCKET_ORFAO",
            [
                "network_sockets.txt",
                "processes.txt",
                "running_services.txt",
                "timesync_logs.txt"
            ],
            status_orfao,
            "MEDIA" if status_orfao == "CORRELACAO PARCIAL" else "BAIXA",
            motivo
        ))

        if status_orfao == "CORRELACAO PARCIAL":
            parciais += 1
        else:
            insuficientes += 1

        relatorio += [
            "[CORRELACAO 05] SOCKET ORFAO",
            f"Socket: {item['socket']}",
            f"Status: {status_orfao}",
            f"Evidencia: {motivo}",
            ""
        ]

    # ----------------------------------------------------------
    # MOTOR DE CORRELACAO
    # ----------------------------------------------------------

    motor = analisar_relacoes(relacoes)

    print("=== MOTOR DE CORRELACAO ===")
    print("Relacoes registradas:", motor["total"])
    print("Relacoes confirmadas:", motor["confirmadas"])
    print("Relacoes parciais:", motor["parciais"])
    print("Relacoes insuficientes:", motor["insuficientes"])
    print("Analises concluidas:", motor["analises_concluidas"])

    relatorio += [
        "",
        "=== MOTOR DE CORRELACAO ===",
        f"Relacoes registradas: {motor['total']}",
        f"Relacoes confirmadas: {motor['confirmadas']}",
        f"Relacoes parciais: {motor['parciais']}",
        f"Relacoes insuficientes: {motor['insuficientes']}",
        f"Analises concluidas: {motor['analises_concluidas']}",
        ""
    ]

    if motor["atencao"]:
        relatorio.append("RELACOES QUE EXIGEM ATENCAO:")

        for relacao in motor["atencao"]:
            relatorio += [
                f"- Tipo: {relacao['tipo']}",
                f"  Status: {relacao['status']}",
                f"  Confianca: {relacao['confianca']}",
                f"  Justificativa: {relacao['justificativa']}",
                ""
            ]
    else:
        relatorio.append("Nenhuma relacao exige atencao.")

    # ----------------------------------------------------------
    # INVESTIGACOES SUGERIDAS
    # ----------------------------------------------------------

    print("=== INVESTIGACOES SUGERIDAS ===")

    investigacoes = []

    if motor["atencao"]:
        for indice, relacao in enumerate(motor["atencao"], start=1):
            investigacao = {
                "id": f"INV-{indice:03d}",
                "tipo": relacao["tipo"],
                "status": "ABERTA",
                "confianca": relacao["confianca"],
                "justificativa": relacao["justificativa"]
            }

            investigacoes.append(investigacao)

            print(f"[{investigacao['id']}] {investigacao['tipo']}")
            print("Status:", investigacao["status"])
            print("Confianca:", investigacao["confianca"])
            print("Justificativa:", investigacao["justificativa"])
            print()
    else:
        print("Nenhuma investigacao sugerida.")

    relatorio += [
        "",
        "=== INVESTIGACOES SUGERIDAS ===",
        ""
    ]

    if investigacoes:
        for investigacao in investigacoes:
            relatorio += [
                f"[{investigacao['id']}] {investigacao['tipo']}",
                f"Status: {investigacao['status']}",
                f"Confianca: {investigacao['confianca']}",
                f"Justificativa: {investigacao['justificativa']}",
                ""
            ]
    else:
        relatorio.append("Nenhuma investigacao sugerida.")

    # ----------------------------------------------------------
    # RESUMO
    # ----------------------------------------------------------

    print("=== RESUMO DA ANALISE ===")
    print("Correlacoes analisadas: 5")
    print("Correlacoes confirmadas:", confirmadas)
    print("Correlacoes parciais:", parciais)
    print("Evidencias insuficientes:", insuficientes)

    relatorio += [
        "=== RESUMO DA ANALISE ===",
        "Correlacoes analisadas: 5",
        f"Correlacoes confirmadas: {confirmadas}",
        f"Correlacoes parciais: {parciais}",
        f"Evidencias insuficientes: {insuficientes}"
    ]

    saida = EVIDENCE / "correlation_report.txt"

    saida.write_text(
        "\n".join(relatorio) + "\n",
        encoding="utf-8"
    )

    return {
        "relacoes": relacoes,
        "motor": motor,
        "investigacoes": investigacoes
    }


if __name__ == "__main__":
    main()
