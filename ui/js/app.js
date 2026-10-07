console.log("🐙 OCTOPOSS UI carregada.");
console.log("🕷️ Tentáculos de Evidências operacional.");

async function carregarDashboard() {
    try {
        const resposta = await fetch("/api/dashboard");
        const dados = await resposta.json();

        console.log("📊 Dashboard recebido:", dados);

        const processos = document.querySelector("#total-processos");
        const servicos = document.querySelector("#total-servicos");
        const rede = document.querySelector("#total-rede");
        const auth = document.querySelector("#total-auth");

        if (processos) processos.textContent = dados.processos;
        if (servicos) servicos.textContent = dados.servicos;
        if (rede) rede.textContent = String(dados.rede).padStart(2, "0");
        if (auth) auth.textContent = dados.auth;
    } catch (erro) {
        console.error("❌ Erro ao carregar dashboard:", erro);
    }
}

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

carregarDashboard();
carregarEvidencias();
carregarInventario();
