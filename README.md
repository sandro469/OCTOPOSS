# 🐙 OCTOPOSS

## Blue Team Evidence Center

O **OCTOPOSS** é um laboratório defensivo de Cibersegurança desenvolvido para **coletar, organizar, correlacionar e investigar evidências de um sistema**.

O projeto segue uma abordagem **Evidence First**: uma anomalia não é automaticamente tratada como ameaça. Primeiro são coletadas evidências, depois realizadas correlações e, quando necessário, abertas investigações.

---

## 🎯 Objetivo

Criar uma estrutura prática de **Blue Team** capaz de transformar dados técnicos do sistema em informações úteis para análise e investigação.

O fluxo principal do OCTOPOSS é:

```text
EVIDÊNCIA
   ↓
CORRELAÇÃO
   ↓
CLASSIFICAÇÃO
   ↓
INVESTIGAÇÃO
   ↓
RELATÓRIO
```

---

## 🐙 Tentáculos de Evidências

O OCTOPOSS organiza diferentes fontes de informação para permitir uma visão conjunta do ambiente.

Entre as evidências analisadas estão:

- Processos em execução
- Serviços ativos
- Sockets e conexões de rede
- Logs
- Autenticação
- Usuários
- Informações do sistema
- Relações entre processos, serviços e rede

A ideia central é **não analisar cada evidência isoladamente**, mas procurar relações entre elas.

---

## 🧠 Central Mind

O projeto possui um núcleo denominado **Central Mind**, responsável por receber informações produzidas pelos componentes do OCTOPOSS e manter o estado das correlações e investigações.

Estrutura principal:

```text
central_mind/
├── __init__.py
├── autoboot.py
├── memory.py
├── message.py
└── mind.py
```

A comunicação com o núcleo é realizada através da ponte:

```text
scripts/octoposs_central_bridge.py
```

---

## 🔎 Correlação e Investigação

O mecanismo de correlação analisa relações entre:

- Processos
- Serviços
- Sockets
- DNS
- Sincronização de horário
- Logs relacionados

O **correlator v07** representa a versão final utilizada no projeto.

Quando uma relação não possui evidências suficientes para uma conclusão, o OCTOPOSS mantém a classificação como insuficiente ou parcial e pode gerar uma investigação para análise posterior.

Isso evita transformar automaticamente um comportamento desconhecido em um falso positivo.

---

## 🖥️ Evidence Center

O projeto possui uma interface web para visualização das informações coletadas.

O servidor disponibiliza APIs para:

```text
/api/inventory
/api/report
/api/evidence
/api/dashboard
```

O dashboard apresenta informações consolidadas sobre o ambiente e os resultados das análises.

---

## ⚙️ Execução

No diretório do projeto:

```bash
cd ~/OCTOPOSS
python3 scripts/octoposs_server.py
```

O servidor disponibiliza o Evidence Center na porta `3000`.

---

## 📁 Estrutura principal

```text
OCTOPOSS/
├── central_mind/
├── evidence/
├── evidence_backup/
├── logs/
├── reports/
├── scripts/
│   ├── octoposs_collector.py
│   ├── octoposs_correlator_v07.py
│   ├── octoposs_central_bridge.py
│   ├── octoposs_inventory.py
│   └── octoposs_server.py
└── ui/
    ├── index.html
    ├── css/
    └── js/
```

---

## 🛡️ Tecnologias

- Python
- JavaScript
- HTML5
- CSS3
- Linux / WSL
- Git
- GitHub
- APIs REST
- Análise de logs
- Correlação de evidências
- Conceitos de Blue Team

---

## 🧪 Princípio do projeto

O OCTOPOSS foi desenvolvido com foco em uma investigação defensiva simples e objetiva:

> **Evidência antes da conclusão.**

O objetivo não é apenas detectar algo diferente, mas **entender o que aconteceu, relacionar os dados disponíveis e registrar o resultado da investigação**.

---

## 🚀 Evolução

O OCTOPOSS faz parte de uma trilogia de projetos de segurança:

```text
🐍 VENOM
Observação da aplicação
        ↓
🐙 OCTOPOSS
Correlação e investigação de evidências
        ↓
🐆 LINCE
Patrulha e análise de transporte/rede
```

Cada projeto possui uma função diferente dentro da arquitetura, evitando a duplicação de responsabilidades.

---

## 📌 Status

**Projeto concluído e validado.**

O OCTOPOSS representa a evolução do estudo prático de **Blue Team, coleta de evidências, correlação, investigação e análise defensiva**.
