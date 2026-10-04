from datetime import datetime


class CentralMemory:
    def __init__(self):
        self.created_at = datetime.now().isoformat()
        self.system = {}
        self.tentacles = {}
        self.evidence = []
        self.correlations = []
        self.investigations = []

    def register_system(self, system_data):
        self.system = system_data

    def register_tentacle(self, tentacle_data):
        self.tentacles[tentacle_data["name"]] = tentacle_data

    def register_evidence(self, evidence_data):
        self.evidence.append(evidence_data)

    def register_correlation(self, correlation_data):
        self.correlations.append(correlation_data)

    def register_investigation(self, investigation_data):
        self.investigations.append(investigation_data)

    def status(self):
        return {
            "created_at": self.created_at,
            "system": self.system,
            "tentacles": len(self.tentacles),
            "evidence": len(self.evidence),
            "correlations": len(self.correlations),
            "investigations": len(self.investigations)
        }


if __name__ == "__main__":
    memory = CentralMemory()

    print("🧠 OCTOPOSS CENTRAL MEMORY V1")
    print("=" * 32)

    estado = memory.status()

    for chave, valor in estado.items():
        print(f"{chave}: {valor}")
