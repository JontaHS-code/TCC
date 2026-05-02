# backend/models.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, Boolean
from database import Base


class Politico(Base):
    __tablename__ = "politicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    partido = Column(String)
    uf = Column(String)
    cargo = Column(String)
    gasto_total = Column(Float, default=0.0)
    num_proposicoes = Column(Integer, default=0)
    presenca_percentual = Column(Float, default=0.0)
    irep_score = Column(Float, default=0.0)
    ultima_atualizacao = Column(DateTime)
    foto_url = Column(String, nullable=True)

    # Campos que você já tinha
    gasto_per_capita = Column(Float, nullable=True)
    ranking_estadual = Column(JSON, nullable=True)
    evolucao_gastos = Column(Float, nullable=True)
    palavras_chave = Column(JSON, nullable=True)
    trocas_partido = Column(Integer, default=0)

    # ===== NOVOS CAMPOS DE ANALYTICS =====
    benford_chi2 = Column(Float, nullable=True)
    benford_significativo = Column(Boolean, default=False)
    hhi = Column(Float, nullable=True)
    hhi_nivel = Column(String, nullable=True)          # BAIXO, MODERADO, ALTO, MUITO_ALTO
    pct_valores_redondos = Column(Float, nullable=True)
    top1_pct = Column(Float, nullable=True)            # % do maior fornecedor
    zscore_partido = Column(Float, nullable=True)
    zscore_estado = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_nivel = Column(String, nullable=True)          # CRÍTICO, ALTO, MÉDIO, BAIXO
    red_flags = Column(JSON, nullable=True)             # Lista de flags
    n_red_flags = Column(Integer, default=0)
    analytics_atualizado = Column(DateTime, nullable=True)  # Último cálculo


class DespesaAgregada(Base):
    __tablename__ = "despesas_agregadas"

    id = Column(Integer, primary_key=True, index=True)
    ano = Column(Integer, index=True)
    categoria = Column(String, index=True)
    valor = Column(Float)


class Proposicao(Base):
    __tablename__ = "proposicoes"

    id = Column(Integer, primary_key=True, index=True)
    politico_id = Column(Integer, index=True)
    titulo = Column(String)
    data_apresentacao = Column(Date)
    tipo = Column(String)


class VotacaoCache(Base):
    __tablename__ = "votacoes_cache"

    id = Column(String, primary_key=True, index=True)
    data = Column(Date)
    processada = Column(Boolean, default=False)


# ===== NOVA TABELA: Análises por categoria =====
class AnaliseCategoria(Base):
    """Cache de análises por categoria de gasto para cada político."""
    __tablename__ = "analises_categoria"

    id = Column(Integer, primary_key=True, index=True)
    politico_id = Column(Integer, index=True)
    categoria = Column(String, index=True)
    ano = Column(Integer, default=2025)
    gasto_total = Column(Float)
    n_transacoes = Column(Integer)
    benford_chi2 = Column(Float, nullable=True)
    benford_significativo = Column(Boolean, default=False)
    hhi = Column(Float, nullable=True)
    hhi_nivel = Column(String, nullable=True)
    pct_valores_redondos = Column(Float, nullable=True)
    top1_pct = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    red_flags = Column(JSON, nullable=True)
    atualizado_em = Column(DateTime)