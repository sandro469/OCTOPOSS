console.log("🐙 OCTOPOSS UI carregada.");
console.log("🕷️ Teia de Evidências operacional.");

async function carregarEvidencias() {
    try {
        const resposta = await fetch("/api/evidence");
        const dados = await resposta.json();

        console.log("📡 Evidências recebidas:", dados);

        const elemento = document.querySelector("#total-evidencias");

        if (elemento) {
            elemento.textContent = dados.total;
        }
    } catch (erro) {
        console.error("❌ Erro ao carregar evidências:", erro);
    }
}

async function carregarInventario() {
    try {
        const resposta = await fetch("/api/inventory");
        const texto = await resposta.text();

        console.log("🖥️ Inventário recebido:");
        console.log(texto);
    } catch (erro) {
        console.error("❌ Erro ao carregar inventário:", erro);
    }
}

carregarEvidencias();
carregarInventario();
