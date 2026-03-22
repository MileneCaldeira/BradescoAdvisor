Documentação do Agente — BradescoAdvisor
Etapa 1: Documentação Técnica e Funcional
---
1. Visão Geral do Agente
Nome: BradescoAdvisor  
Versão: 1.0  
Data: Março 2026  
Projeto: Bootcamp Bradesco GenAI & Dados — Projeto Final
O BradescoAdvisor é um agente conversacional baseado em IA Generativa projetado para o relacionamento financeiro digital com clientes do Banco Bradesco. Sua função principal é democratizar o acesso a informações financeiras, oferecendo respostas claras, personalizadas e responsáveis sobre produtos, serviços e simulações.
---
2. Objetivos do Agente
Objetivo Principal
Ser o primeiro ponto de contato digital para clientes com dúvidas financeiras, reduzindo a fricção no relacionamento banco-cliente e aumentando o engajamento com os produtos Bradesco.
Objetivos Secundários
Educar clientes sobre produtos de investimento e crédito
Executar simulações financeiras com transparência
Identificar oportunidades de cross-sell por meio da conversa
Coletar dados de qualidade para melhoria contínua do serviço
---
3. Casos de Uso
#	Caso de Uso	Intenção	Exemplo de Prompt
1	FAQ de produto	FAQ	"Qual a diferença entre CDB e LCI?"
2	Simulação de empréstimo	SIMULACAO	"Simule R$20.000 em 36 meses"
3	Simulação de investimento	SIMULACAO	"Quanto rende R$10.000 no CDB por 1 ano?"
4	Abertura de conta	FAQ	"Como abro conta no Bradesco?"
5	Orientação de produto	PRODUTO	"Qual cartão é melhor para eu acumular pontos?"
6	Suporte a problema	RECLAMACAO	"Perdi meu cartão, o que faço?"
7	Negociação de dívida	FAQ	"Como renegociar minha dívida?"
---
4. Arquitetura do Agente
```
┌─────────────────────────────────────────────────────┐
│                  INTERFACE (Streamlit)               │
│  ┌─────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Input  │  │  Quick Btns  │  │  Metrics Panel │  │
│  └────┬────┘  └──────────────┘  └────────────────┘  │
└───────┼─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              CAMADA DE ORQUESTRAÇÃO (app.py)         │
│                                                      │
│  1. Intent Detection ──→ Claude API (lightweight)   │
│  2. Simulation Check ──→ Local Python Calculator    │
│  3. Context Builder  ──→ Knowledge Base + History   │
│  4. Main Chat        ──→ Claude API (full response) │
│  5. Metrics Logging  ──→ AgentEvaluator             │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│               CAMADAS DE SUPORTE                     │
│                                                      │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │  knowledge_base  │  │   financial_calculator   │ │
│  │  .json           │  │   (Price, Compostos, IR) │ │
│  └──────────────────┘  └──────────────────────────┘ │
│                                                      │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │  agent_prompts   │  │   evaluation/metrics     │ │
│  │  (3 prompts)     │  │   (5 dimensões)          │ │
│  └──────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```
---
5. Modelo de IA
Atributo	Valor
Provedor	Anthropic
Modelo	claude-sonnet-4-20250514
Max tokens output	1500
Temperature	Padrão (balanced)
Context window	200k tokens
Estratégia de contexto:
System prompt: identidade + base de conhecimento (top 3000 chars) + regras
Histórico: últimas 8 mensagens para continuidade sem overhead excessivo
Intent classification: chamada separada e leve (max 200 tokens)
---
6. Guardrails e Responsabilidade
O agente SEMPRE:
Inclui disclaimers em simulações financeiras
Orienta o cliente a falar com gerente para decisões complexas
Responde em português brasileiro
Usa o nome do cliente quando fornecido
O agente NUNCA:
Garante retornos de investimento
Solicita senhas ou dados sensíveis
Promete aprovação de crédito
Critica concorrentes
Inventa produtos ou taxas
---
7. Limitações Conhecidas
Limitação	Impacto	Mitigação
Não acessa dados reais do cliente	Não personaliza por saldo ou histórico	Orienta para canal autenticado
Base de conhecimento estática	Produtos/taxas podem desatualizar	JSON editável sem alterar código
Sem persistência entre sessões	Histórico se perde ao fechar	Mensagem de boas-vindas contextualizada
Simulações com taxas médias	Não reflete taxa personalizada	Disclaimer explícito em toda simulação
---
8. Métricas de Sucesso
Métrica	Meta
Score de qualidade composto	≥ 0.70
Latência média de resposta	< 5.000ms
Cobertura de intenções detectadas	≥ 90%
Satisfação do usuário (quando coletada)	≥ 4.0/5.0
Taxa de respostas com disclaimer	100% em simulações
---
Documento gerado para o Bootcamp Bradesco GenAI & Dados — Projeto Final · 2026
