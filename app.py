"""
app.py — BradescoAdvisor
Agente de Relacionamento Financeiro com IA Generativa
Bradesco GenAI & Dados Bootcamp — Projeto Final

Autor: Milene Caldeira
GitHub: github.com/MileneCaldeira
"""

import streamlit as st
import anthropic
import json
import time
from pathlib import Path

# Internal modules
import sys
sys.path.append(str(Path(__file__).parent))

from prompts.agent_prompts import SYSTEM_PROMPT, INTENT_CLASSIFIER_PROMPT, SIMULATION_PROMPT
from utils.financial_calculator import (
    calculate_loan_price,
    calculate_investment_compound,
    format_simulation_as_markdown,
    format_currency,
    calculate_cdi_percentage
)
from evaluation.metrics import AgentEvaluator


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BradescoAdvisor | Assistente Financeiro IA",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bradesco brand palette
BRADESCO_RED = "#CC092F"
BRADESCO_DARK = "#8B0000"
BRADESCO_LIGHT_RED = "#FF1744"

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{ font-family: 'Inter', sans-serif; }}
    
    .stApp {{ background-color: #0f0f0f; color: #f5f5f5; }}
    
    .bradesco-header {{
        background: linear-gradient(135deg, {BRADESCO_RED} 0%, {BRADESCO_DARK} 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    
    .bradesco-header h1 {{
        color: white;
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
    }}
    
    .bradesco-header p {{
        color: rgba(255,255,255,0.85);
        margin: 4px 0 0;
        font-size: 0.9rem;
    }}
    
    .metric-card {{
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-left: 4px solid {BRADESCO_RED};
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }}
    
    .metric-card h3 {{
        color: {BRADESCO_RED};
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 6px;
    }}
    
    .metric-card .value {{
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
    }}
    
    .chat-user {{
        background: #1e1e2e;
        border-left: 3px solid #6366f1;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }}
    
    .chat-assistant {{
        background: #1a1212;
        border-left: 3px solid {BRADESCO_RED};
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }}
    
    .intent-badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        background: {BRADESCO_RED}33;
        color: {BRADESCO_RED};
        border: 1px solid {BRADESCO_RED}66;
        margin-bottom: 6px;
    }}
    
    .stTextInput > div > div > input {{
        background: #1a1a1a;
        border: 1px solid #333;
        color: white;
        border-radius: 8px;
    }}
    
    .stButton > button {{
        background: {BRADESCO_RED};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.2s;
    }}
    
    .stButton > button:hover {{
        background: {BRADESCO_DARK};
        transform: translateY(-1px);
    }}
    
    .sidebar .stMarkdown {{
        color: #ccc;
    }}
    
    .quick-btn {{
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0;
        cursor: pointer;
        font-size: 0.85rem;
        color: #ccc;
        width: 100%;
        text-align: left;
    }}
    
    .quick-btn:hover {{
        border-color: {BRADESCO_RED};
        color: white;
    }}
    
    hr {{ border-color: #222; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD KNOWLEDGE BASE
# ─────────────────────────────────────────────
@st.cache_data
def load_knowledge_base():
    kb_path = Path(__file__).parent / "data" / "knowledge_base.json"
    with open(kb_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "evaluator" not in st.session_state:
    st.session_state.evaluator = AgentEvaluator()
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "show_metrics" not in st.session_state:
    st.session_state.show_metrics = False
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0


# ─────────────────────────────────────────────
# ANTHROPIC CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_client():
    return anthropic.Anthropic()


# ─────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────
def detect_intent(user_message: str, client: anthropic.Anthropic) -> dict:
    """Usa Claude para classificar intenção do usuário."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": INTENT_CLASSIFIER_PROMPT.format(user_message=user_message)
            }]
        )
        result_text = response.content[0].text.strip()
        # Limpa possíveis backticks do JSON
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        return json.loads(result_text)
    except Exception:
        return {"intencao": "OUTRO", "confianca": 0.5, "entidades": []}


# ─────────────────────────────────────────────
# SIMULATION HANDLER
# ─────────────────────────────────────────────
def handle_simulation(user_message: str) -> str | None:
    """
    Detecta pedidos de simulação e executa cálculo local antes de chamar a IA.
    Retorna markdown da simulação ou None se não for simulação detectável.
    """
    msg_lower = user_message.lower()

    # Detecta simulação de empréstimo
    if any(kw in msg_lower for kw in ["empréstimo", "emprestimo", "parcela", "financiamento", "crédito pessoal"]):
        # Tenta extrair valores com regex simples
        import re
        values = re.findall(r'r?\$?\s*([\d\.,]+)\s*(?:mil)?', msg_lower)
        months = re.findall(r'(\d+)\s*(?:meses|mes|parcelas)', msg_lower)

        if values and months:
            try:
                principal = float(values[0].replace(".", "").replace(",", "."))
                if "mil" in msg_lower:
                    principal *= 1000
                n_months = int(months[0])
                sim = calculate_loan_price(principal, 23.88, n_months)
                return format_simulation_as_markdown(sim)
            except Exception:
                pass

    # Detecta simulação de investimento
    if any(kw in msg_lower for kw in ["investir", "investimento", "rendimento", "aplicação", "cdb", "lci", "tesouro"]):
        import re
        values = re.findall(r'r?\$?\s*([\d\.,]+)\s*(?:mil)?', msg_lower)
        months = re.findall(r'(\d+)\s*(?:meses|mes|anos?)', msg_lower)

        if values and months:
            try:
                principal = float(values[0].replace(".", "").replace(",", "."))
                if "mil" in msg_lower:
                    principal *= 1000
                n = int(months[0])
                if "ano" in msg_lower:
                    n *= 12
                rate = calculate_cdi_percentage(10.65, 100)
                sim = calculate_investment_compound(principal, 0, rate, n)
                return format_simulation_as_markdown(sim)
            except Exception:
                pass

    return None


# ─────────────────────────────────────────────
# MAIN CHAT FUNCTION
# ─────────────────────────────────────────────
def chat_with_advisor(user_message: str, client: anthropic.Anthropic) -> tuple[str, str]:
    """
    Envia mensagem ao agente e retorna (response, intent).
    """
    kb = load_knowledge_base()
    kb_summary = json.dumps(kb, ensure_ascii=False, indent=2)[:3000]  # Limit tokens

    # Context window — últimas 6 mensagens
    recent_history = st.session_state.messages[-6:]
    context = "\n".join([
        f"{m['role'].upper()}: {m['content'][:200]}"
        for m in recent_history
    ])
    if st.session_state.user_name:
        context = f"Nome do cliente: {st.session_state.user_name}\n" + context

    system = SYSTEM_PROMPT.format(
        knowledge_base=kb_summary,
        conversation_context=context or "Início da conversa"
    )

    # Build messages for API
    api_messages = []
    for msg in st.session_state.messages[-8:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    api_messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system,
        messages=api_messages
    )

    assistant_text = response.content[0].text
    st.session_state.total_tokens += response.usage.input_tokens + response.usage.output_tokens

    return assistant_text


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0 20px;">
        <div style="font-size:3rem;">🏦</div>
        <div style="color:{BRADESCO_RED}; font-weight:700; font-size:1.1rem;">BradescoAdvisor</div>
        <div style="color:#888; font-size:0.75rem;">Powered by Claude AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # User name
    name_input = st.text_input("Seu nome (opcional)", placeholder="Ex: Ana Silva",
                                value=st.session_state.user_name)
    if name_input != st.session_state.user_name:
        st.session_state.user_name = name_input

    st.divider()

    # Quick access
    st.markdown("**💬 Perguntas rápidas**")
    quick_questions = [
        "Como abrir conta no Bradesco?",
        "Simule empréstimo de R$10.000 em 24 meses",
        "Qual o melhor investimento para iniciantes?",
        "Quais cartões de crédito o Bradesco oferece?",
        "Como fazer Pix pelo app?",
        "Simule investimento de R$5.000 por 12 meses",
    ]
    for q in quick_questions:
        if st.button(q, key=f"quick_{q[:20]}", use_container_width=True):
            st.session_state["quick_input"] = q

    st.divider()

    # Session stats
    st.markdown("**📊 Sessão atual**")
    turns = len(st.session_state.messages) // 2
    st.metric("Mensagens trocadas", turns)
    st.metric("Tokens utilizados", f"{st.session_state.total_tokens:,}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.messages = []
            st.session_state.evaluator = AgentEvaluator()
            st.session_state.total_tokens = 0
            st.rerun()
    with col2:
        if st.button("📈 Métricas", use_container_width=True):
            st.session_state.show_metrics = not st.session_state.show_metrics

    st.divider()
    st.markdown("""
    <div style="color:#555; font-size:0.7rem; text-align:center;">
        Projeto Final — Bradesco GenAI & Dados<br>
        Milene Caldeira • 2026
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="bradesco-header">
    <div style="font-size:2.5rem;">🏦</div>
    <div>
        <h1>BradescoAdvisor</h1>
        <p>Assistente Financeiro com IA Generativa · Relacionamento inteligente, seguro e personalizado</p>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI strip
col1, col2, col3, col4 = st.columns(4)
kb = load_knowledge_base()
rates = kb.get("taxas_referencia", {})
with col1:
    st.markdown(f"""<div class="metric-card"><h3>Selic</h3><div class="value">{rates.get('selic_atual','—')}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card"><h3>CDI</h3><div class="value">{rates.get('cdi_atual','—')}</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card"><h3>IPCA 12M</h3><div class="value">{rates.get('ipca_12m','—')}</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card"><h3>Atualização</h3><div class="value" style="font-size:0.95rem;">{rates.get('data_atualizacao','—')}</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# METRICS PANEL
# ─────────────────────────────────────────────
if st.session_state.show_metrics and st.session_state.messages:
    with st.expander("📊 Painel de Avaliação da Sessão", expanded=True):
        report = st.session_state.evaluator.export_evaluation_report()
        if "error" not in report:
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                score = report["quality_scores"]["avg_composite_score"]
                label = report["quality_scores"]["score_label"]
                st.metric("Score de Qualidade", f"{score:.2%}", label)
            with mc2:
                avg_rt = report["session_summary"]["avg_response_time_ms"]
                st.metric("Latência Média", f"{avg_rt:.0f}ms")
            with mc3:
                sims = report["session_summary"]["simulation_count"]
                st.metric("Simulações executadas", sims)

            st.markdown("**Distribuição de intenções:**")
            dist = report["intent_distribution"]
            if dist:
                for intent, count in dist.items():
                    st.progress(count / max(dist.values()), text=f"{intent}: {count}x")

            st.markdown("**Recomendações:**")
            for rec in report.get("recommendations", []):
                st.info(f"💡 {rec}")

# ─────────────────────────────────────────────
# CHAT DISPLAY
# ─────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        name_display = f", {st.session_state.user_name}" if st.session_state.user_name else ""
        st.markdown(f"""
        <div style="text-align:center; padding:40px 20px; color:#555;">
            <div style="font-size:3rem; margin-bottom:16px;">👋</div>
            <div style="font-size:1.2rem; color:#aaa; margin-bottom:8px;">
                Olá{name_display}! Sou o BradescoAdvisor.
            </div>
            <div style="font-size:0.9rem;">
                Posso te ajudar com investimentos, crédito, cartões, simulações e muito mais.<br>
                Use as sugestões ao lado ou me faça uma pergunta!
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong style="color:#818cf8;">👤 Você</strong><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                intent_display = msg.get("intent", "")
                badge = f'<span class="intent-badge">{intent_display}</span><br>' if intent_display else ""
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong style="color:{BRADESCO_RED};">🏦 BradescoAdvisor</strong><br>
                    {badge}
                """, unsafe_allow_html=True)
                st.markdown(msg["content"])
                st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUT AREA
# ─────────────────────────────────────────────
st.markdown("---")

# Handle quick button input
default_input = st.session_state.pop("quick_input", "")

with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([5, 1])
    with cols[0]:
        user_input = st.text_input(
            "Digite sua mensagem...",
            value=default_input,
            placeholder="Ex: Quero simular um empréstimo de R$15.000...",
            label_visibility="collapsed"
        )
    with cols[1]:
        submit = st.form_submit_button("Enviar →", use_container_width=True)

if submit and user_input.strip():
    client = get_client()
    start_time = time.time()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Detect intent
    with st.spinner("Analisando..."):
        intent_data = detect_intent(user_input, client)
        intent = intent_data.get("intencao", "OUTRO")

    # Check for local simulation
    sim_result = handle_simulation(user_input)

    # Build enriched message if simulation was detected
    enriched_message = user_input
    if sim_result:
        enriched_message = f"{user_input}\n\n[SIMULAÇÃO CALCULADA PELO SISTEMA]\n{sim_result}"

    # Get AI response
    with st.spinner("BradescoAdvisor está respondendo..."):
        response_text = chat_with_advisor(
            enriched_message if sim_result else user_input,
            client
        )

    elapsed_ms = (time.time() - start_time) * 1000

    # Log to evaluator
    st.session_state.evaluator.log_turn(
        user_msg=user_input,
        assistant_response=response_text,
        intent=intent,
        response_time_ms=elapsed_ms
    )

    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "intent": intent
    })

    st.rerun()
