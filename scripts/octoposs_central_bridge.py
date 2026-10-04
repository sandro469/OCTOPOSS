from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent
SCRIPTS = BASE / "scripts"

sys.path.insert(0, str(BASE))
sys.path.insert(0, str(SCRIPTS))

from central_mind.mind import CentralMind
import octoposs_correlator_v07 as correlator


def executar_correlator():
    return correlator.main()


def obter_resultados():
    return executar_correlator()


def enviar_correlacoes(mind, resultados):
    for relacao in resultados["relacoes"]:
        mind.register_correlation(relacao)


def enviar_investigacoes(mind, resultados):
    for investigacao in resultados["investigacoes"]:
        mind.register_investigation(investigacao)


def registrar_tentaculo_correlacao(mind):
    mind.register_tentacle({
        "name": "TENTACULO_CORRELACAO_V07",
        "type": "correlation_engine",
        "status": "ONLINE",
        "description": "Motor de correlacao dos Tentaculos de Evidencias"
    })
