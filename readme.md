<div align="center">

<img src="https://img.shields.io/badge/Bradesco-CC092F?style=for-the-badge&logoColor=white" alt="Bradesco"/>
<img src="https://img.shields.io/badge/GenAI_%26_Dados-Bootcamp-CC092F?style=for-the-badge" alt="Bootcamp"/>
<img src="https://img.shields.io/badge/Projeto_Final-2026-111111?style=for-the-badge" alt="Projeto Final"/>

<br/><br/>

# 🏦 BradescoAdvisor

### Agente de Relacionamento Financeiro com IA Generativa

*Respostas contextualizadas · Simulações reais · Experiência personalizada*

<br/>

[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Anthropic](https://img.shields.io/badge/Claude_API-191919?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

</div>

---

## Visão Geral

O **BradescoAdvisor** é um assistente financeiro inteligente construído com IA Generativa para transformar o relacionamento digital entre o Bradesco e seus clientes. Em vez de FAQs estáticos e longas filas de atendimento, o agente oferece respostas contextualizadas, simulações financeiras com cálculos reais e uma experiência personalizada — disponível 24h.

**Resultado de negócio:** redução do volume de atendimento humano para dúvidas frequentes, com UX clara, segura e escalável.

---

## Funcionalidades

| | Funcionalidade | Descrição |
|---|---|---|
| 🧠 | **FAQ Inteligente** | Respostas contextualizadas sobre produtos, serviços e processos Bradesco |
| 📊 | **Simulações Financeiras** | Empréstimos (Tabela Price) e investimentos (juros compostos + IR regressivo) |
| 💬 | **Memória de Contexto** | Mantém o histórico da conversa para respostas cada vez mais personalizadas |
| 🔐 | **Guardrails de Segurança** | Disclaimers automáticos, sem captação de dados sensíveis |
| 📈 | **Avaliação Contínua** | Score de qualidade em 5 dimensões com relatório automático de métricas |

---

## Estrutura do Projeto

```
bradesco-advisor/
│
├── 📄 app.py                           # Etapa 4 — Aplicação funcional (Streamlit)
│
├── 📁 data/
│   └── knowledge_base.json            # Etapa 2 — Base de conhecimento estruturada
│
├── 📁 prompts/
│   └── agent_prompts.py               # Etapa 3 — Prompts do agente
│
├── 📁 utils/
│   └── financial_calculator.py        # Etapa 4 — Engine de simulações financeiras
│
├── 📁 evaluation/
│   └── metrics.py                     # Etapa 5 — Avaliação e métricas de qualidade
│
├── 📁 docs/
│   ├── agent_documentation.md         # Etapa 1 — Documentação técnica do agente
│   └── pitch.html                     # Etapa 6 — Pitch deck de entrega
│
├── requirements.txt
└── README.md
```

---

## As 6 Etapas do Desafio

<details>
<summary><strong>Etapa 1 — Documentação do Agente</strong></summary>
<br/>

Especificação técnica completa: objetivos, arquitetura de componentes, casos de uso, guardrails de segurança, limitações conhecidas e métricas de sucesso. Serve como contrato técnico do que o agente deve e não deve fazer.

📄 `docs/agent_documentation.md`

</details>

<details>
<summary><strong>Etapa 2 — Base de Conhecimento</strong></summary>
<br/>

JSON hierárquico com dados estruturados sobre os principais produtos Bradesco (contas, cartões, investimentos, crédito, seguros), FAQ com 8 perguntas frequentes e taxas de mercado (Selic, CDI, IPCA). Injetada dinamicamente no system prompt.

📄 `data/knowledge_base.json`

</details>

<details>
<summary><strong>Etapa 3 — Prompts do Agente</strong></summary>
<br/>

Três prompts engenheirados para comportamentos distintos:

- **`SYSTEM_PROMPT`** — identidade, tom, base de conhecimento e guardrails
- **`INTENT_CLASSIFIER_PROMPT`** — classifica intenção em JSON estruturado (`FAQ`, `SIMULACAO`, `PRODUTO`, `RECLAMACAO`)
- **`SIMULATION_PROMPT`** — chain-of-thought para simulações com cálculos transparentes

📄 `prompts/agent_prompts.py`

</details>

<details>
<summary><strong>Etapa 4 — Aplicação Funcional</strong></summary>
<br/>

App Streamlit completo com identidade visual Bradesco, chat persistente, KPI strip com taxas de mercado, botões de acesso rápido e painel de métricas inline. Engine local de simulações financeiras (sem custo de API) com Tabela Price, juros compostos e IR regressivo.

📄 `app.py` · `utils/financial_calculator.py`

</details>

<details>
<summary><strong>Etapa 5 — Avaliação e Métricas</strong></summary>
<br/>

Sistema de avaliação automática com 5 dimensões ponderadas:

| Dimensão | Peso | O que mede |
|---|---|---|
| Clarity | 25% | Estrutura, markdown e marcadores de clareza |
| Domain Relevance | 25% | Uso de terminologia financeira |
| Completeness | 20% | Tamanho adequado da resposta |
| Helpfulness | 15% | Orientações acionáveis ao cliente |
| Safety Compliance | 15% | Disclaimers e responsabilidade |

Gera relatório com score composto, distribuição de intenções e recomendações de melhoria.

📄 `evaluation/metrics.py`

</details>

<details>
<summary><strong>Etapa 6 — Pitch e Entrega</strong></summary>
<br/>

Pitch deck em HTML com identidade visual Bradesco cobrindo problema, solução, arquitetura técnica, métricas e stack. README com posicionamento sênior e estrutura clara para avaliação.

📄 `docs/pitch.html`

</details>

---

## Arquitetura

```
Usuário → Streamlit UI
              ↓
     [Intent Detection]  →  Claude API  (max 200 tokens)
              ↓
   [Simulation Engine]   →  Python local (sem latência)
              ↓
    [Context Builder]    →  KB (3.000 chars) + histórico (8 msgs)
              ↓
      [Main Chat]        →  Claude API  (max 1.500 tokens)
              ↓
  [Metrics Logging]      →  AgentEvaluator (5 dimensões)
              ↓
         Resposta + Badge de intenção + Painel de métricas
```

---

## Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/MileneCaldeira/bradesco-advisor
cd bradesco-advisor

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure a API Key
export ANTHROPIC_API_KEY="sua-chave-aqui"

# 4. Execute
streamlit run app.py
```

---

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-191919?style=flat-square&logo=anthropic&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)

---

<div align="center">

**Milene Caldeira**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/milene-caldeira/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/MileneCaldeira)
[![Portfolio](https://img.shields.io/badge/Portfolio-CC092F?style=flat-square&logo=googlechrome&logoColor=white)](https://milenecaldeira.github.io)
[![Email](https://img.shields.io/badge/Email-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:mcaldeira.tech@gmail.com)

*Bootcamp Bradesco GenAI & Dados · Projeto Final · 2026*

</div>
