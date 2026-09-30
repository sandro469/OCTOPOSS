from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent
UI = BASE / "ui"
EVIDENCE = BASE / "evidence"


class OctopossHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def do_GET(self):

        if self.path == "/api/inventory":
            self.enviar_arquivo(EVIDENCE / "system_inventory.txt")
            return

        if self.path == "/api/report":
            self.enviar_arquivo(EVIDENCE / "correlation_report.txt")
            return

        if self.path == "/api/dashboard":
            processos = max(
                0,
                len((EVIDENCE / "processes.txt").read_text(encoding="utf-8").splitlines()) - 1
            )

            servicos = max(
                0,
                len((EVIDENCE / "running_services.txt").read_text(encoding="utf-8").splitlines()) - 1
            )

            rede = max(
                0,
                len((EVIDENCE / "network_sockets.txt").read_text(encoding="utf-8").splitlines()) - 1
            )

            auth = len(
                (EVIDENCE / "recent_logs.txt").read_text(encoding="utf-8").splitlines()
            )

            self.enviar_json({
                "processos": processos,
                "servicos": servicos,
                "rede": rede,
                "auth": auth
            })
            return

        if self.path == "/api/evidence":
            arquivos = sorted(
                arquivo.name
                for arquivo in EVIDENCE.glob("*.txt")
            )

            self.enviar_json({
                "total": len(arquivos),
                "arquivos": arquivos
            })
            return

        if self.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def enviar_arquivo(self, caminho):
        if not caminho.exists():
            self.send_error(404, "Evidencia nao encontrada")
            return

        conteudo = caminho.read_text(encoding="utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(conteudo.encode("utf-8"))

    def enviar_json(self, dados):
        conteudo = json.dumps(
            dados,
            ensure_ascii=False,
            indent=2
        )

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(conteudo.encode("utf-8"))

    def log_message(self, formato, *args):
        print("[OCTOPOSS]", formato % args)


PORTA = 3000

print("🐙 OCTOPOSS SERVER")
print("=" * 30)
print(f"UI: http://127.0.0.1:{PORTA}")
print(f"Pasta UI: {UI}")
print("Servidor local ativo.")
print("Pressione CTRL+C para encerrar.")

servidor = HTTPServer(("127.0.0.1", PORTA), OctopossHandler)
servidor.serve_forever()
