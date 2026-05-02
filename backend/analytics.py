# backend/analytics.py
"""
Módulo de análise de gastos parlamentares.
Implementa técnicas de detecção de anomalias:
- Lei de Benford
- Índice Herfindahl-Hirschman (HHI)
- Valores redondos
- Z-score vs pares
- Risk scoring combinado
"""

import math
import re
from collections import Counter, defaultdict
from typing import Optional, Dict, List, Any, Tuple


# ============================================================
# LEI DE BENFORD
# ============================================================

def benford_esperado() -> Dict[int, float]:
    """Distribuição esperada pela Lei de Benford (dígitos 1-9)."""
    return {d: math.log10(1 + 1/d) for d in range(1, 10)}


def extrair_primeiro_digito(valor: float) -> Optional[int]:
    """Extrai o primeiro dígito significativo de um valor monetário."""
    if valor is None or valor <= 0:
        return None
    str_valor = str(abs(valor)).replace('.', '').replace(',', '').lstrip('0')
    if not str_valor:
        return None
    return int(str_valor[0])


def analise_benford(valores: List[float]) -> Dict[str, Any]:
    """
    Análise completa de conformidade com a Lei de Benford.
    
    Args:
        valores: Lista de valores das transações
    
    Returns:
        Dict com chi2, p_valor, significativo, desvios por dígito
    """
    digitos = [extrair_primeiro_digito(v) for v in valores if v and v > 0]
    digitos = [d for d in digitos if d is not None]
    n = len(digitos)
    
    if n < 50:
        return {'erro': 'Amostra insuficiente (mínimo 50 transações)', 'n_valores': n}
    
    contagem = Counter(digitos)
    esperado = benford_esperado()
    
    observado = [contagem.get(d, 0) for d in range(1, 10)]
    esperado_abs = [esperado[d] * n for d in range(1, 10)]
    
    # Chi-quadrado manual
    chi2 = sum(
        ((obs - esp) ** 2) / esp if esp > 0 else 0
        for obs, esp in zip(observado, esperado_abs)
    )
    
    # p-valor aproximado (8 graus de liberdade)
    # Usamos threshold chi² = 15.51 para significância (p < 0.05, 8 gl)
    significativo = chi2 > 15.51
    
    # Desvios por dígito
    freq_observada = {d: contagem.get(d, 0) / n for d in range(1, 10)}
    desvios = {}
    for d in range(1, 10):
        obs_pct = freq_observada[d] * 100
        esp_pct = esperado[d] * 100
        desvios[d] = {
            'observado': round(obs_pct, 1),
            'esperado': round(esp_pct, 1),
            'desvio': round(obs_pct - esp_pct, 1)
        }
    
    return {
        'chi2': round(chi2, 2),
        'significativo': significativo,
        'n_valores': n,
        'desvios': desvios,
        'p_valor_aproximado': '< 0.05' if significativo else '>= 0.05'
    }


# ============================================================
# ÍNDICE HERFINDAHL-HIRSCHMAN (HHI)
# ============================================================

def calcular_hhi(participacoes: List[float]) -> float:
    """
    Calcula o HHI (0 a 10.000).
    
    Args:
        participacoes: Lista de frações (0 a 1) de cada fornecedor
    
    Returns:
        float: HHI
    """
    return sum(p**2 for p in participacoes) * 10000


def interpretar_hhi(hhi: float) -> str:
    """Interpreta o nível de concentração do HHI."""
    if hhi < 1500:
        return 'BAIXO'
    elif hhi < 2500:
        return 'MODERADO'
    elif hhi < 5000:
        return 'ALTO'
    else:
        return 'MUITO_ALTO'


def analise_concentracao(transacoes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Análise de concentração de fornecedores.
    
    Args:
        transacoes: Lista de dicts com 'fornecedor' (CNPJ) e 'valor'
    
    Returns:
        Dict com HHI, nível, top fornecedores, etc.
    """
    total = sum(t['valor'] for t in transacoes)
    if total <= 0:
        return {'erro': 'Sem gastos', 'hhi': 0, 'nivel': 'INDETERMINADO'}
    
    por_fornecedor = defaultdict(float)
    for t in transacoes:
        cnpj = re.sub(r'\D', '', str(t.get('fornecedor', '')))
        por_fornecedor[cnpj] += t['valor']
    
    ordenado = sorted(por_fornecedor.items(), key=lambda x: x[1], reverse=True)
    participacoes = [v / total for _, v in ordenado]
    
    hhi = calcular_hhi(participacoes)
    
    return {
        'hhi': round(hhi, 2),
        'nivel': interpretar_hhi(hhi),
        'n_fornecedores': len(ordenado),
        'top1_pct': round(participacoes[0] * 100, 1) if participacoes else 0,
        'top3_pct': round(sum(participacoes[:3]) * 100, 1) if len(participacoes) >= 3 else 100,
        'top5_pct': round(sum(participacoes[:5]) * 100, 1) if len(participacoes) >= 5 else 100,
        'total_gasto': total,
        'top_fornecedores': [
            {'cnpj': cnpj, 'valor': round(valor, 2), 'participacao': round(valor/total*100, 1)}
            for cnpj, valor in ordenado[:10]
        ]
    }


# ============================================================
# VALORES REDONDOS
# ============================================================

def eh_valor_redondo(valor: float, divisores: List[int] = [1000, 500, 100]) -> bool:
    """
    Verifica se o valor é suspeitamente redondo.
    
    Args:
        valor: Valor da transação
        divisores: Faixas para considerar redondo
    
    Returns:
        bool: True se o valor é múltiplo dos divisores
    """
    if valor is None or valor <= 0:
        return False
    return any(valor % d == 0 for d in divisores)


def pct_valores_redondos(valores: List[float]) -> Dict[str, Any]:
    """
    Calcula percentual de valores redondos.
    
    Returns:
        Dict com percentual, threshold, status
    """
    if not valores:
        return {'percentual': 0, 'status': 'SEM_DADOS'}
    
    validos = [v for v in valores if v and v > 0]
    if not validos:
        return {'percentual': 0, 'status': 'SEM_DADOS'}
    
    n_redondos = sum(1 for v in validos if eh_valor_redondo(v))
    pct = (n_redondos / len(validos)) * 100
    
    if pct > 50:
        status = 'EXTREMO'
    elif pct > 30:
        status = 'ALTO'
    elif pct > 20:
        status = 'MODERADO'
    else:
        status = 'NORMAL'
    
    return {
        'percentual': round(pct, 1),
        'n_redondos': n_redondos,
        'n_total': len(validos),
        'status': status,
        'threshold': 30
    }


# ============================================================
# Z-SCORE vs PARES
# ============================================================

def calcular_zscore(valor: float, valores_referencia: List[float]) -> Optional[float]:
    """
    Calcula Z-score: quantos desvios-padrão o valor está da média.
    
    Returns:
        float ou None se não houver referência suficiente
    """
    if len(valores_referencia) < 3:
        return None
    
    media = sum(valores_referencia) / len(valores_referencia)
    variancia = sum((v - media) ** 2 for v in valores_referencia) / len(valores_referencia)
    std = math.sqrt(variancia)
    
    if std == 0:
        return 0
    
    return (valor - media) / std


# ============================================================
# RISK SCORING
# ============================================================

def calcular_risk_score(
    hhi: float,
    benford_significativo: bool,
    pct_redondos: float,
    top1_pct: float,
    z_score_partido: Optional[float],
    z_score_estado: Optional[float],
    gasto_total: float,
    n_transacoes: int
) -> Dict[str, Any]:
    """
    Calcula o Risk Score combinado (0 a 1).
    
    Fórmula: min(Base_HHI + Penalidades, 1.0) com spending cap
    
    Returns:
        Dict com score, nível, componentes
    """
    
    def score_hhi(h):
        if h is None:
            return 0.20
        elif h > 3000:
            return 0.90
        elif h > 2500:
            return 0.70
        elif h > 1500:
            return 0.40
        else:
            return 0.20
    
    def penalidade_benford(sig):
        return 0.15 if sig else 0
    
    def penalidade_redondos(pct):
        return 0.10 if pct and pct > 20 else 0
    
    def penalidade_dominante(pct):
        return 0.10 if pct and pct > 50 else 0
    
    def penalidade_zscore(z):
        return 0.08 if z and z > 2.0 else 0
    
    # Componentes
    base = score_hhi(hhi)
    pen_b = penalidade_benford(benford_significativo)
    pen_r = penalidade_redondos(pct_redondos)
    pen_d = penalidade_dominante(top1_pct)
    pen_zp = penalidade_zscore(z_score_partido)
    pen_ze = penalidade_zscore(z_score_estado)
    
    # Score bruto
    score_bruto = min(base + pen_b + pen_r + pen_d + pen_zp + pen_ze, 1.0)
    
    # Nível
    if score_bruto >= 0.75:
        nivel = 'CRÍTICO'
    elif score_bruto >= 0.55:
        nivel = 'ALTO'
    elif score_bruto >= 0.35:
        nivel = 'MÉDIO'
    else:
        nivel = 'BAIXO'
    
    # Spending cap (evita falsos positivos em amostras pequenas)
    score_final = score_bruto
    if gasto_total < 100_000:
        score_final = min(score_bruto, 0.34)
        nivel = 'BAIXO'
    elif gasto_total < 200_000 and nivel in ['CRÍTICO', 'ALTO']:
        score_final = min(score_bruto, 0.54)
        nivel = 'MÉDIO'
    elif gasto_total < 400_000 and nivel == 'CRÍTICO':
        score_final = min(score_bruto, 0.74)
        nivel = 'ALTO'
    
    # Red flags
    red_flags = []
    if hhi and hhi > 2500:
        red_flags.append('Concentração ALTA')
    if benford_significativo:
        red_flags.append('Benford significativo')
    if pct_redondos and pct_redondos > 30:
        red_flags.append(f'Valores redondos {pct_redondos:.0f}%')
    if top1_pct and top1_pct > 50:
        red_flags.append(f'Fornecedor dominante ({top1_pct:.0f}%)')
    
    return {
        'score': round(score_final, 3),
        'score_bruto': round(score_bruto, 3),
        'nivel': nivel,
        'componentes': {
            'base_hhi': base,
            'penalidade_benford': pen_b,
            'penalidade_redondos': pen_r,
            'penalidade_dominante': pen_d,
            'penalidade_z_partido': pen_zp,
            'penalidade_z_estado': pen_ze
        },
        'red_flags': red_flags,
        'n_red_flags': len(red_flags)
    }


# ============================================================
# ANÁLISE COMPLETA DE UM DEPUTADO
# ============================================================

def analisar_deputado_completo(
    transacoes: List[Dict[str, Any]],
    gastos_partido: List[float],
    gastos_estado: List[float],
    nome: str = ""
) -> Dict[str, Any]:
    """
    Análise completa combinando todas as técnicas.
    
    Args:
        transacoes: Lista de dicts com 'valor', 'fornecedor', 'categoria'
        gastos_partido: Lista de gastos totais de deputados do mesmo partido
        gastos_estado: Lista de gastos totais de deputados do mesmo estado
        nome: Nome do deputado (para logging)
    
    Returns:
        Dict com todas as métricas e scores
    """
    valores = [t['valor'] for t in transacoes if t.get('valor')]
    gasto_total = sum(valores)
    n_transacoes = len(valores)
    
    # Benford
    benford = analise_benford(valores)
    
    # HHI
    hhi_result = analise_concentracao(transacoes)
    
    # Valores redondos
    redondos = pct_valores_redondos(valores)
    
    # Z-scores
    z_partido = calcular_zscore(gasto_total, gastos_partido) if gastos_partido else None
    z_estado = calcular_zscore(gasto_total, gastos_estado) if gastos_estado else None
    
    # Risk Score
    risk = calcular_risk_score(
        hhi=hhi_result.get('hhi', 0),
        benford_significativo=benford.get('significativo', False),
        pct_redondos=redondos.get('percentual', 0),
        top1_pct=hhi_result.get('top1_pct', 0),
        z_score_partido=z_partido,
        z_score_estado=z_estado,
        gasto_total=gasto_total,
        n_transacoes=n_transacoes
    )
    
    return {
        'nome': nome,
        'gasto_total': round(gasto_total, 2),
        'n_transacoes': n_transacoes,
        'benford': benford,
        'hhi': hhi_result,
        'valores_redondos': redondos,
        'z_scores': {
            'partido': round(z_partido, 2) if z_partido is not None else None,
            'estado': round(z_estado, 2) if z_estado is not None else None
        },
        'risk_score': risk
    }