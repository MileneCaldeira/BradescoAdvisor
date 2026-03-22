"""
evaluation/metrics.py
Módulo de avaliação e métricas do BradescoAdvisor — Etapa 5
Avalia qualidade das respostas do agente com métricas objetivas e heurísticas.
"""

import re
import json
import time
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ConversationTurn:
    user_message: str
    assistant_response: str
    intent: str
    response_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    rating: Optional[int] = None  # 1-5 stars (opcional, dado pelo usuário)


@dataclass
class SessionMetrics:
    session_id: str
    start_time: str
    total_turns: int
    avg_response_time_ms: float
    intent_distribution: dict
    satisfaction_scores: List[int]
    topics_covered: List[str]
    simulation_count: int
    avg_satisfaction: Optional[float]


class AgentEvaluator:
    """
    Avalia a qualidade das respostas do agente com métricas automáticas.
    """

    QUALITY_KEYWORDS = {
        "clarity": ["portanto", "ou seja", "em outras palavras", "resumindo", "em resumo"],
        "helpfulness": ["você pode", "é possível", "recomendo", "sugiro", "para isso"],
        "safety": ["disclaimer", "consulte", "fale com", "gerente", "sujeito a análise"],
        "personalization": ["no seu caso", "para você", "com base no que você disse"]
    }

    FINANCIAL_TERMS = [
        "cdi", "selic", "ipca", "cdb", "lci", "lca", "pix", "ted", "doc",
        "parcela", "taxa", "juros", "rendimento", "investimento", "empréstimo",
        "financiamento", "anuidade", "limite", "fatura", "cartão"
    ]

    def __init__(self):
        self.conversation_log: List[ConversationTurn] = []
        self.session_start = datetime.now().isoformat()
        self.session_id = f"session_{int(time.time())}"

    def log_turn(self, user_msg: str, assistant_response: str,
                 intent: str, response_time_ms: float, rating: Optional[int] = None):
        """Registra um turno da conversa com métricas."""
        turn = ConversationTurn(
            user_message=user_msg,
            assistant_response=assistant_response,
            intent=intent,
            response_time_ms=response_time_ms,
            rating=rating
        )
        self.conversation_log.append(turn)

    def score_response(self, response: str) -> dict:
        """
        Avalia automaticamente uma resposta com múltiplas dimensões.
        
        Returns:
            dict com scores de 0-1 por dimensão
        """
        response_lower = response.lower()
        scores = {}

        # 1. Clarity Score — uso de estrutura e marcadores de clareza
        clarity_hits = sum(1 for kw in self.QUALITY_KEYWORDS["clarity"] if kw in response_lower)
        has_markdown = bool(re.search(r'#{1,3}|[\*\-]|\|', response))
        scores["clarity"] = min(1.0, (clarity_hits * 0.2) + (0.3 if has_markdown else 0) + 0.3)

        # 2. Completeness Score — resposta com tamanho adequado
        word_count = len(response.split())
        if word_count < 20:
            scores["completeness"] = 0.3
        elif word_count < 50:
            scores["completeness"] = 0.6
        elif word_count <= 300:
            scores["completeness"] = 1.0
        else:
            scores["completeness"] = 0.8  # muito longa perde ponto

        # 3. Domain Relevance — termos financeiros presentes
        domain_hits = sum(1 for term in self.FINANCIAL_TERMS if term in response_lower)
        scores["domain_relevance"] = min(1.0, domain_hits * 0.15)

        # 4. Safety Score — disclaimers e orientação responsável
        safety_hits = sum(1 for kw in self.QUALITY_KEYWORDS["safety"] if kw in response_lower)
        scores["safety_compliance"] = min(1.0, 0.5 + safety_hits * 0.25)

        # 5. Helpfulness — orientação acionável
        help_hits = sum(1 for kw in self.QUALITY_KEYWORDS["helpfulness"] if kw in response_lower)
        scores["helpfulness"] = min(1.0, 0.4 + help_hits * 0.2)

        # Composite Score
        weights = {
            "clarity": 0.25,
            "completeness": 0.20,
            "domain_relevance": 0.25,
            "safety_compliance": 0.15,
            "helpfulness": 0.15
        }
        scores["composite"] = round(
            sum(scores[k] * weights[k] for k in weights), 3
        )

        return scores

    def get_intent_distribution(self) -> dict:
        """Retorna distribuição de intenções na sessão."""
        distribution = {}
        for turn in self.conversation_log:
            distribution[turn.intent] = distribution.get(turn.intent, 0) + 1
        return distribution

    def get_session_metrics(self) -> SessionMetrics:
        """Compila todas as métricas da sessão."""
        if not self.conversation_log:
            return None

        ratings = [t.rating for t in self.conversation_log if t.rating is not None]
        response_times = [t.response_time_ms for t in self.conversation_log]
        simulations = sum(1 for t in self.conversation_log if t.intent == "SIMULACAO")

        # Tópicos detectados
        all_text = " ".join([t.user_message for t in self.conversation_log]).lower()
        topics = []
        topic_map = {
            "investimentos": ["investimento", "cdb", "lci", "tesouro", "renda fixa"],
            "crédito": ["empréstimo", "parcela", "financiamento", "crédito"],
            "cartão": ["cartão", "limite", "fatura", "anuidade"],
            "conta": ["conta", "pix", "transferência", "saldo"],
            "seguro": ["seguro", "proteção"]
        }
        for topic, keywords in topic_map.items():
            if any(kw in all_text for kw in keywords):
                topics.append(topic)

        return SessionMetrics(
            session_id=self.session_id,
            start_time=self.session_start,
            total_turns=len(self.conversation_log),
            avg_response_time_ms=round(sum(response_times) / len(response_times), 1),
            intent_distribution=self.get_intent_distribution(),
            satisfaction_scores=ratings,
            topics_covered=topics,
            simulation_count=simulations,
            avg_satisfaction=round(sum(ratings) / len(ratings), 2) if ratings else None
        )

    def export_evaluation_report(self) -> dict:
        """Gera relatório completo de avaliação da sessão."""
        metrics = self.get_session_metrics()
        if not metrics:
            return {"error": "Nenhuma conversa registrada"}

        # Score automático das respostas
        auto_scores = [
            self.score_response(t.assistant_response)
            for t in self.conversation_log
        ]
        avg_composite = round(
            sum(s["composite"] for s in auto_scores) / len(auto_scores), 3
        )

        return {
            "session_summary": {
                "session_id": metrics.session_id,
                "total_turns": metrics.total_turns,
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "simulation_count": metrics.simulation_count,
                "topics_covered": metrics.topics_covered
            },
            "quality_scores": {
                "avg_composite_score": avg_composite,
                "score_label": (
                    "Excelente" if avg_composite >= 0.8 else
                    "Bom" if avg_composite >= 0.6 else
                    "Regular" if avg_composite >= 0.4 else "Necessita melhoria"
                ),
                "per_turn": auto_scores
            },
            "user_satisfaction": {
                "avg_rating": metrics.avg_satisfaction,
                "ratings_collected": len(metrics.satisfaction_scores),
                "ratings": metrics.satisfaction_scores
            },
            "intent_distribution": metrics.intent_distribution,
            "recommendations": self._generate_recommendations(avg_composite, metrics)
        }

    def _generate_recommendations(self, score: float, metrics: SessionMetrics) -> List[str]:
        """Gera recomendações de melhoria baseadas nas métricas."""
        recs = []
        if score < 0.6:
            recs.append("Revisar prompts do sistema para aumentar clareza das respostas")
        if metrics.avg_response_time_ms and metrics.avg_response_time_ms > 5000:
            recs.append("Otimizar latência — considerar cache para perguntas frequentes")
        if metrics.simulation_count == 0:
            recs.append("Proativamente oferecer simulações financeiras nas conversas")
        if not metrics.topics_covered:
            recs.append("Ampliar cobertura de tópicos na base de conhecimento")
        if not recs:
            recs.append("Performance dentro do esperado. Continuar monitorando.")
        return recs
