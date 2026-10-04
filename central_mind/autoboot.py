from .mind import CentralMind


class AutoBoot:
    def __init__(self):
        self.name = "AUTOboot"
        self.version = "V1"
        self.status = "ONLINE"
        self.mind = CentralMind()
        self.current_mission = None

    def status_info(self):
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status
        }

    def mind_status(self):
        return self.mind.status()

    def receive_mission(self, mission):
        self.current_mission = mission
        return self.current_mission

    def mission_status(self):
        if self.current_mission is None:
            return "NO_MISSION"

        return "READY"


if __name__ == "__main__":
    autoboot = AutoBoot()

    mission = {
        "source": "CENTRAL MIND",
        "target": "AUTOboot",
        "action": "aguardar_proxima_coordenada",
        "priority": "NORMAL"
    }

    autoboot.receive_mission(mission)

    print("🤖 AUTObOOT V1")
    print("=" * 20)
    print(f"status: {autoboot.status}")

    print("\n🧠 CENTRAL MIND")
    print("=" * 20)
    print(f"status: {autoboot.mind_status()['status']}")

    print("\n🎯 MISSÃO")
    print("=" * 20)
    print(f"action: {autoboot.current_mission['action']}")
    print(f"priority: {autoboot.current_mission['priority']}")

    print("\n🚦 AUTObOOT")
    print("=" * 20)
    print(f"mission_status: {autoboot.mission_status()}")
