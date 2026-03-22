🏦 BradescoAdvisor — Agente de Relacionamento Financeiro com IA Generativa
> **Projeto Final · Bootcamp Bradesco GenAI & Dados**  
> Assistente conversacional inteligente para o relacionamento financeiro com clientes do Bradesco, construído com IA Generativa, Python e boas práticas de engenharia de dados.
---
🎯 Visão Geral
O BradescoAdvisor é um agente financeiro baseado em IA Generativa capaz de:
Responder FAQs inteligentes sobre produtos e serviços Bradesco
Executar simulações financeiras (empréstimos, investimentos) com cálculos reais
Explicar produtos com linguagem acessível e personalizada
Manter contexto e memória ao longo da conversa
Avaliar a qualidade das respostas com métricas objetivas
Resultado de negócio: Redução do volume de atendimento humano para dúvidas frequentes, com experiência de usuário personalizada e segura.
---
🗂️ Estrutura do Projeto (6 Etapas)
```
bradesco-advisor/
│
├── app.py                          ← Etapa 4: Aplicação funcional (Streamlit)
│
├── data/
│   └── knowledge_base.json        ← Etapa 2: Base de Conhecimento
│
├── prompts/
│   └── agent_prompts.py           ← Etapa 3: Prompts do Agente
│
├── utils/
│   └── financial_calculator.py    ← Etapa 4: Simulações financeiras
│
├── evaluation/
│   └── metrics.py                 ← Etapa 5: Avaliação e Métricas
│
├── docs/
│   └── agent_documentation.md     ← Etapa 1: Documentação do Agente
│
├── requirements.txt
└── README.md
```
---
🧠 Etapa 1 — Documentação do Agente
Atributo	Descrição
Nome	BradescoAdvisor
Objetivo	Relacionamento financeiro digital com IA Generativa
Modelo	Claude Sonnet (Anthropic API)
Linguagem	Python 3.11+
Interface	Streamlit Web App
Domínio	Serviços financeiros — Banco Bradesco
Capacidades	FAQ, Simulação, Orientação, Contextualização
Limitações	Não aprova crédito, não acessa dados reais do cliente, não substitui gerente
Casos de uso principais:
Cliente quer entender diferença entre CDB e Tesouro Direto
Cliente quer simular parcelas de um empréstimo
Cliente tem dúvida sobre como bloquear cartão
Cliente quer saber qual investimento se adequa ao seu perfil
---
📚 Etapa 2 — Base de Conhecimento
A base de conhecimento (`data/knowledge_base.json`) estrutura informações sobre:
Produtos: Conta corrente, cartões de crédito, investimentos, crédito, seguros
FAQ: 8 perguntas frequentes com respostas detalhadas
Taxas de referência: Selic, CDI, IPCA atualizados
Estratégia de estruturação:
JSON hierárquico para fácil consulta programática
Dados agnósticos de tempo (atualizáveis sem alterar o código)
Injetado dinamicamente no system prompt da IA
---
🎭 Etapa 3 — Prompts do Agente
Três prompts engenheirados para comportamentos específicos:
Prompt	Finalidade
`SYSTEM_PROMPT`	Identidade, regras, base de conhecimento e tom do agente
`INTENT_CLASSIFIER_PROMPT`	Classificação de intenção em JSON estruturado
`SIMULATION_PROMPT`	Execução de simulações financeiras explicadas
Técnicas aplicadas:
Role prompting com identidade definida
Output format specification (JSON para classificação)
Chain-of-thought para simulações (mostrar cálculos)
Guardrails explícitos (o que SEMPRE e NUNCA fazer)
---
⚙️ Etapa 4 — Aplicação Funcional
Arquitetura
```
Usuário → Streamlit UI
         ↓
    Intent Detection (Claude API)
         ↓
    Simulation Engine (Local Python)    ← para cálculos matemáticos
         ↓
    BradescoAdvisor (Claude API)        ← com knowledge base + contexto
         ↓
    Response + Metrics Logging
```
Funcionalidades da Interface
🔴 Header com identidade visual Bradesco
📊 KPI strip com taxas de mercado em tempo real
💬 Chat persistente com histórico da sessão
⚡ Botões de acesso rápido às perguntas mais comuns
👤 Personalização por nome do cliente
📈 Painel de métricas de qualidade (toggle)
---
📊 Etapa 5 — Avaliação e Métricas
O módulo `evaluation/metrics.py` implementa avaliação em 5 dimensões:
Métrica	Peso	O que mede
Clarity	25%	Estrutura e marcadores de clareza
Domain Relevance	25%	Uso de terminologia financeira
Completeness	20%	Tamanho adequado da resposta
Helpfulness	15%	Orientações acionáveis

Safety Compliance	15%	Disclaimers e responsabilidade
Saída do relatório:
```json
{
  "quality_scores": {"avg_composite_score": 0.78, "score_label": "Bom"},
  "user_satisfaction": {"avg_rating": 4.2},
  "intent_distribution": {"FAQ": 5, "SIMULACAO": 2},
  "recommendations": ["..."]
}
```
---
🚀 Como Executar
```bash
# 1. Clone o repositório
git clone https://github.com/MileneCaldeira/bradesco-advisor
cd bradesco-advisor

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure a API Key
export ANTHROPIC_API_KEY="sua-chave-aqui"

# 4. Execute o app
streamlit run app.py
```
---
🛠️ Stack Tecnológica
Tecnologia	Uso
Python 3.11	Linguagem principal
Anthropic Claude API	Motor de IA Generativa
Streamlit	Interface web interativa
JSON	Base de conhecimento estruturada
Dataclasses	Modelagem de dados tipada
---
💡 Destaques Técnicos
Sem dependências de terceiros para simulações — cálculos financeiros implementados do zero (Price, juros compostos, IR regressivo)
Classificação de intenção desacoplada — intent detection antes do chat principal permite logging e métricas granulares
Context window management — trunca histórico para otimizar tokens sem perder continuidade
Avaliação automática — métricas heurísticas independentes do modelo, auditáveis e reproduzíveis
---
👩‍💻 Autora
Milene Caldeira — Data Analyst & BI Professional  
📧 mcaldeira.tech@gmail.com  
🔗 linkedin.com/in/milene-caldeira  
🌐 milenecaldeira.github.io  
💻 github.com/MileneCaldeira
---
Projeto desenvolvido no Bootcamp Bradesco GenAI & Dados · 2026
