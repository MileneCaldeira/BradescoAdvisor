"""
utils/financial_calculator.py
Módulo de simulações financeiras do BradescoAdvisor
"""

import math
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LoanSimulation:
    principal: float
    monthly_rate: float
    months: int
    monthly_payment: float
    total_paid: float
    total_interest: float
    schedule: List[dict]


@dataclass
class InvestmentSimulation:
    initial_value: float
    monthly_contribution: float
    annual_rate: float
    months: int
    final_amount: float
    total_invested: float
    total_return: float
    net_return_pct: float
    schedule: List[dict]


def calculate_loan_price(
    principal: float,
    annual_rate: float,
    months: int
) -> LoanSimulation:
    """
    Calcula simulação de empréstimo pela Tabela Price (parcelas fixas).
    
    Args:
        principal: Valor solicitado (R$)
        annual_rate: Taxa anual em % (ex: 23.88 para 23,88% a.a.)
        months: Prazo em meses
    
    Returns:
        LoanSimulation com todos os detalhes
    """
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    if monthly_rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                          ((1 + monthly_rate) ** months - 1)

    schedule = []
    balance = principal

    for month in range(1, months + 1):
        interest = balance * monthly_rate
        amortization = monthly_payment - interest
        balance -= amortization

        if month <= 3 or month == months:
            schedule.append({
                "mes": month,
                "parcela": round(monthly_payment, 2),
                "juros": round(interest, 2),
                "amortizacao": round(amortization, 2),
                "saldo_devedor": round(max(balance, 0), 2)
            })

    total_paid = monthly_payment * months
    total_interest = total_paid - principal

    return LoanSimulation(
        principal=principal,
        monthly_rate=monthly_rate * 100,
        months=months,
        monthly_payment=round(monthly_payment, 2),
        total_paid=round(total_paid, 2),
        total_interest=round(total_interest, 2),
        schedule=schedule
    )


def calculate_investment_compound(
    initial_value: float,
    monthly_contribution: float,
    annual_rate: float,
    months: int,
    ir_exempt: bool = False
) -> InvestmentSimulation:
    """
    Calcula projeção de investimento com aportes mensais e juros compostos.
    
    Args:
        initial_value: Valor inicial (R$)
        monthly_contribution: Aporte mensal (R$)
        annual_rate: Taxa anual em % (ex: 10.65 para CDI atual)
        months: Período em meses
        ir_exempt: True para LCI/LCA (isento de IR)
    
    Returns:
        InvestmentSimulation com projeção completa
    """
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    balance = initial_value
    total_invested = initial_value
    schedule = []

    for month in range(1, months + 1):
        interest_earned = balance * monthly_rate
        balance = balance + interest_earned + monthly_contribution

        if month > 1:
            total_invested += monthly_contribution

        if month <= 3 or month in [6, 12, 24, 36] or month == months:
            schedule.append({
                "mes": month,
                "saldo": round(balance, 2),
                "rendimento_mes": round(interest_earned, 2),
                "total_investido": round(total_invested, 2)
            })

    # IR calculation (regressivo para renda fixa)
    gross_return = balance - total_invested
    if not ir_exempt and months <= 6:
        ir_rate = 0.225
    elif not ir_exempt and months <= 12:
        ir_rate = 0.20
    elif not ir_exempt and months <= 24:
        ir_rate = 0.175
    elif not ir_exempt:
        ir_rate = 0.15
    else:
        ir_rate = 0.0

    ir_amount = gross_return * ir_rate
    net_return = gross_return - ir_amount
    final_net = total_invested + net_return
    net_return_pct = (net_return / total_invested) * 100

    return InvestmentSimulation(
        initial_value=initial_value,
        monthly_contribution=monthly_contribution,
        annual_rate=annual_rate,
        months=months,
        final_amount=round(final_net, 2),
        total_invested=round(total_invested, 2),
        total_return=round(net_return, 2),
        net_return_pct=round(net_return_pct, 2),
        schedule=schedule
    )


def calculate_cdi_percentage(
    cdi_annual: float = 10.65,
    product_rate_pct: float = 100.0
) -> float:
    """Retorna taxa anual equivalente a X% do CDI."""
    return cdi_annual * (product_rate_pct / 100)


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_simulation_as_markdown(sim: LoanSimulation | InvestmentSimulation) -> str:
    """Converte resultado de simulação para markdown formatado."""
    if isinstance(sim, LoanSimulation):
        rows = "\n".join([
            f"| {s['mes']}° | {format_currency(s['parcela'])} | "
            f"{format_currency(s['juros'])} | {format_currency(s['amortizacao'])} | "
            f"{format_currency(s['saldo_devedor'])} |"
            for s in sim.schedule
        ])
        return f"""
### 📊 Resultado da Simulação de Crédito

| Parâmetro | Valor |
|-----------|-------|
| Valor solicitado | {format_currency(sim.principal)} |
| Taxa mensal | {sim.monthly_rate:.4f}% a.m. |
| Prazo | {sim.months} meses |
| **Parcela mensal** | **{format_currency(sim.monthly_payment)}** |
| Total a pagar | {format_currency(sim.total_paid)} |
| Total em juros | {format_currency(sim.total_interest)} |

**Tabela de amortização (resumida):**

| Mês | Parcela | Juros | Amortização | Saldo Devedor |
|-----|---------|-------|-------------|---------------|
{rows}

> ⚠️ *Simulação com fins ilustrativos. A taxa final pode variar conforme análise de crédito.*
"""
    else:
        rows = "\n".join([
            f"| {s['mes']}° | {format_currency(s['saldo'])} | "
            f"{format_currency(s['rendimento_mes'])} | {format_currency(s['total_investido'])} |"
            for s in sim.schedule
        ])
        return f"""
### 📈 Resultado da Simulação de Investimento

| Parâmetro | Valor |
|-----------|-------|
| Investimento inicial | {format_currency(sim.initial_value)} |
| Aporte mensal | {format_currency(sim.monthly_contribution)} |
| Taxa anual | {sim.annual_rate:.2f}% a.a. |
| Período | {sim.months} meses |
| **Montante final (líquido)** | **{format_currency(sim.final_amount)}** |
| Total investido | {format_currency(sim.total_invested)} |
| Rendimento líquido | {format_currency(sim.total_return)} (+{sim.net_return_pct:.1f}%) |

**Evolução do patrimônio:**

| Mês | Saldo | Rendimento do mês | Total investido |
|-----|-------|-------------------|-----------------|
{rows}

> ⚠️ *Simulação com fins ilustrativos. Rentabilidade passada não garante resultados futuros.*
"""
