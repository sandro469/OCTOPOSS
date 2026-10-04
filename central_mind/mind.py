from .memory import CentralMemory
from .message import MindMessage


class CentralMind:
    def __init__(self):
        self.name = "OCTOPOSS CENTRAL MIND"
        self.version = "V1"
        self.memory = CentralMemory()

        self.memory.register_system({
            "name": "OCTOPOSS",
            "role": "Defensive Cybersecurity Lab",
            "architecture": "Central Mind + Tentáculos de Evidências"
        })

    def register_tentacle(self, tentacle_data):
        self.memory.register_tentacle(tentacle_data)

    def register_evidence(self, evidence_data):
        self.memory.register_evidence(evidence_data)

    def register_correlation(self, correlation_data):
        self.memory.register_correlation(correlation_data)

    def register_investigation(self, investigation_data):
        self.memory.register_investigation(investigation_data)

    def receive_tentacle_message(self, message):
        self.receive_tentacle_result(message.to_dict())

    def receive_tentacle_result(self, result_data):
        self.memory.register_evidence({
            "source": result_data["tentacle"],
            "action": result_data["action"],
            "status": result_data["status"],
            "result": result_data["result"]
        })

        tentacle = self.memory.tentacles.get(result_data["tentacle"])

        if tentacle:
            tentacle["last_action"] = result_data["action"]
            tentacle["last_status"] = result_data["status"]
            tentacle["last_result"] = result_data["result"]

        if result_data["status"] == "ERROR":
            self.register_investigation({
                "source": result_data["tentacle"],
                "action": result_data["action"],
                "reason": result_data["result"],
                "status": "PENDING"
            })

    def update_investigation(self, index, status, result):
        if 0 <= index < len(self.memory.investigations):
            investigation = self.memory.investigations[index]
            investigation["status"] = status
            investigation["result"] = result
            return True

        return False

    def register_correlation_from_investigation(self, investigation_index):
        if 0 <= investigation_index < len(self.memory.investigations):
            investigation = self.memory.investigations[investigation_index]

            correlation = {
                "source": investigation["source"],
                "action": investigation["action"],
                "investigation_status": investigation["status"],
                "relation": "Tentáculo relacionado à investigação",
                "confidence": "HIGH"
            }

            self.register_correlation(correlation)
            return True

        return False

    def status(self):
        return {
            "name": self.name,
            "version": self.version,
            "status": "ONLINE",
            "memory": self.memory.status()
        }


if __name__ == "__main__":
    mind = CentralMind()

    print("🧠 OCTOPOSS CENTRAL MIND")
    print("=" * 30)

    tentaculos = [
        {
            "name": "coleta_evidencias",
            "type": "evidence_collection",
            "status": "ONLINE",
            "description": "Coleta de evidências"
        },
        {
            "name": "analise_processos",
            "type": "process_analysis",
            "status": "ONLINE",
            "description": "Análise de processos"
        },
        {
            "name": "analise_rede",
            "type": "network_analysis",
            "status": "ONLINE",
            "description": "Análise de rede"
        }
    ]

    for tentaculo in tentaculos:
        mind.register_tentacle(tentaculo)

    resultados = [
        {
            "tentacle": "coleta_evidencias",
            "action": "coleta_inicial",
            "status": "SUCCESS",
            "result": "Evidências coletadas"
        },
        {
            "tentacle": "analise_processos",
            "action": "analise_processos",
            "status": "SUCCESS",
            "result": "Processos analisados"
        },
        {
            "tentacle": "analise_rede",
            "action": "analise_sockets",
            "status": "SUCCESS",
            "result": "Sockets analisados"
        }
    ]

    for resultado in resultados:
        mind.receive_tentacle_result(resultado)

    estado = mind.status()

    print(f"status: {estado['status']}")
    print(f"tentacles: {estado['memory']['tentacles']}")
    print(f"evidence: {estado['memory']['evidence']}")
    print(f"correlations: {estado['memory']['correlations']}")
    print(f"investigations: {estado['memory']['investigations']}")

    print("\nevidence:")

    for evidencia in mind.memory.evidence:
        print(f"  {evidencia}")

    print("\ntentacles:")

    for nome, dados in mind.memory.tentacles.items():
        print(f"  {nome}:")
        print(f"    last_action: {dados.get('last_action')}")
        print(f"    last_status: {dados.get('last_status')}")
        print(f"    last_result: {dados.get('last_result')}")
