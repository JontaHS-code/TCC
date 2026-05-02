// frontend/src/components/CardPolitico.jsx
import React, { useState } from "react";
import {
  DollarSign,
  FileText,
  Calendar,
  Award,
  Plus,
  Minus,
  Loader2,
  User,
  Info,
  TrendingUp,
  TrendingDown,
  Tag,
  Users,
  Repeat,
  MapPin,
  ShieldAlert,
} from "lucide-react";
import api from "../services/api";
import RiskBadge from "./RiskBadge";

const CardPolitico = ({ politico }) => {
  const [expandedSection, setExpandedSection] = useState(null);
  const [detalhesGastos, setDetalhesGastos] = useState([]);
  const [detalhesProposicoes, setDetalhesProposicoes] = useState([]);
  const [loadingGastos, setLoadingGastos] = useState(false);
  const [loadingProps, setLoadingProps] = useState(false);
  const [showMaisDetalhes, setShowMaisDetalhes] = useState(false);
  const [tooltipHover, setTooltipHover] = useState(null);

  // Analytics state
  const [analytics, setAnalytics] = useState(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  const fetchDetalhes = async (section) => {
    if (expandedSection === section) {
      setExpandedSection(null);
      return;
    }
    setExpandedSection(section);
    if (section === "gastos" && detalhesGastos.length === 0) {
      setLoadingGastos(true);
      try {
        const r = await api.get(`/politicos/${politico.id}/gastos`);
        setDetalhesGastos(r.data);
      } catch (e) {
      } finally {
        setLoadingGastos(false);
      }
    }
    if (section === "proposicoes" && detalhesProposicoes.length === 0) {
      setLoadingProps(true);
      try {
        const r = await api.get(`/politicos/${politico.id}/proposicoes`);
        setDetalhesProposicoes(r.data);
      } catch (e) {
      } finally {
        setLoadingProps(false);
      }
    }
  };

  const formatMoney = (v) => {
    if (!v && v !== 0) return "R$ 0";
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(v);
  };

  const getScoreColor = (s) => {
    if (s >= 80) return "text-emerald-700 bg-emerald-100 border-emerald-300";
    if (s >= 60) return "text-blue-700 bg-blue-100 border-blue-300";
    if (s >= 40) return "text-amber-700 bg-amber-100 border-amber-300";
    return "text-red-700 bg-red-100 border-red-300";
  };

  const getProgressColor = (s) => {
    if (s >= 80) return "bg-emerald-500";
    if (s >= 60) return "bg-blue-500";
    if (s >= 40) return "bg-amber-500";
    return "bg-red-500";
  };

  const getEficienciaTexto = (s) => {
    if (s >= 80) return "Excelente";
    if (s >= 60) return "Bom";
    if (s >= 40) return "Regular";
    return "Baixa";
  };

  const getPresencaColor = (p) => {
    if (p >= 90) return "text-emerald-700 bg-emerald-50 border-emerald-200";
    if (p >= 75) return "text-blue-700 bg-blue-50 border-blue-200";
    if (p >= 60) return "text-amber-700 bg-amber-50 border-amber-200";
    return "text-red-700 bg-red-50 border-red-200";
  };

  const score = politico.irep_score ?? 0;
  const presenca = politico.presenca_percentual ?? 0;

  const gastoPerCapita = politico.gasto_per_capita ?? null;
  const ranking = politico.ranking_estadual;
  const evolucao = politico.evolucao_gastos;
  const palavras = politico.palavras_chave ?? [];
  const trocas = politico.trocas_partido ?? 0;

  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden border border-gray-200">
      {/* Cabeçalho com foto */}
      <div className="bg-gradient-to-r from-gray-50 to-white p-4">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0 relative">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-400 via-teal-500 to-blue-600 p-0.5 shadow-md">
              {politico.foto_url ? (
                <img
                  src={politico.foto_url}
                  alt={politico.nome}
                  className="w-full h-full rounded-full object-cover border-2 border-white"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.style.display = "none";
                  }}
                />
              ) : (
                <div className="w-full h-full rounded-full bg-white flex items-center justify-center">
                  <User className="h-7 w-7 text-gray-500" />
                </div>
              )}
            </div>
            <div
              className={`absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full border-2 border-white ${
                score >= 80
                  ? "bg-emerald-500"
                  : score >= 60
                    ? "bg-blue-500"
                    : score >= 40
                      ? "bg-amber-500"
                      : "bg-red-500"
              }`}
            />
          </div>

          <div className="flex-grow min-w-0">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-gray-800 truncate">
                  {politico.nome || "Nome não disponível"}
                </h3>
                <div className="flex gap-2 mt-1">
                  <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full font-medium">
                    {politico.partido || "Sem partido"}
                  </span>
                  <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full font-medium">
                    {politico.uf || "?"}
                  </span>
                </div>
              </div>
              <div
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border font-bold text-sm ${getScoreColor(
                  score,
                )}`}
                title={`IREP: ${getEficienciaTexto(score)}`}
              >
                <Award className="h-4 w-4" />
                <span>{score.toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detalhes numéricos */}
      <div className="p-4 space-y-4">
        {/* Gastos */}
        <div className="border border-gray-100 rounded-lg p-3 hover:border-gray-200 transition-colors">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-gray-600">
              <DollarSign className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">Gastos CEAP</span>
              <div className="relative">
                <Info
                  className="h-3.5 w-3.5 text-gray-400 cursor-help hover:text-gray-600"
                  onMouseEnter={() => setTooltipHover("gastos")}
                  onMouseLeave={() => setTooltipHover(null)}
                />
                {tooltipHover === "gastos" && (
                  <div className="absolute z-20 bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-800 text-white text-xs rounded-lg p-2.5 w-56 shadow-lg pointer-events-none">
                    Cota para Exercício da Atividade Parlamentar: recurso mensal
                    para despesas de mandato.
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800" />
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-800">
                {formatMoney(politico.gasto_total)}
              </span>
              <button
                onClick={() => fetchDetalhes("gastos")}
                className="text-gray-400 hover:text-emerald-600"
              >
                {expandedSection === "gastos" ? (
                  <Minus className="h-4 w-4" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
          {expandedSection === "gastos" && (
            <div className="mt-3 pl-6 border-t border-gray-100 pt-3">
              {loadingGastos ? (
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Carregando...
                </div>
              ) : detalhesGastos.length > 0 ? (
                <div className="max-h-48 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
                  {detalhesGastos.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between text-sm py-1 border-b border-gray-50 last:border-0"
                    >
                      <span className="text-gray-600">{item.categoria}</span>
                      <span className="font-mono text-gray-800 font-medium">
                        {formatMoney(item.valor)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400 italic">
                  Nenhum gasto detalhado disponível.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Proposições */}
        <div className="border border-gray-100 rounded-lg p-3 hover:border-gray-200 transition-colors">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-gray-600">
              <FileText className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">Proposições</span>
              <div className="relative">
                <Info
                  className="h-3.5 w-3.5 text-gray-400 cursor-help hover:text-gray-600"
                  onMouseEnter={() => setTooltipHover("proposicoes")}
                  onMouseLeave={() => setTooltipHover(null)}
                />
                {tooltipHover === "proposicoes" && (
                  <div className="absolute z-20 bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-800 text-white text-xs rounded-lg p-2.5 w-56 shadow-lg pointer-events-none">
                    Projetos de lei, PECs, requerimentos e outras propostas de
                    autoria do deputado.
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800" />
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-800">
                {politico.num_proposicoes ?? 0}
              </span>
              <button
                onClick={() => fetchDetalhes("proposicoes")}
                className="text-gray-400 hover:text-emerald-600"
              >
                {expandedSection === "proposicoes" ? (
                  <Minus className="h-4 w-4" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
          {expandedSection === "proposicoes" && (
            <div className="mt-3 pl-6 border-t border-gray-100 pt-3">
              {loadingProps ? (
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Carregando...
                </div>
              ) : detalhesProposicoes.length > 0 ? (
                <>
                  <p className="text-xs text-gray-500 mb-2">
                    Exibindo {detalhesProposicoes.length} proposição(ões)
                  </p>
                  <div className="max-h-60 overflow-y-auto space-y-2.5 pr-1 custom-scrollbar">
                    {detalhesProposicoes.map((item, idx) => (
                      <div
                        key={idx}
                        className="text-sm border-l-2 border-emerald-200 pl-3"
                      >
                        <div className="flex justify-between items-start gap-2">
                          <span className="font-medium text-gray-700 text-xs bg-gray-100 px-2 py-0.5 rounded-full">
                            {item.tipo}
                          </span>
                          <span className="text-xs text-gray-400 whitespace-nowrap">
                            {item.data}
                          </span>
                        </div>
                        <p className="text-gray-600 mt-1 leading-relaxed">
                          {item.titulo}
                        </p>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-xs text-gray-400 italic">
                  Nenhuma proposição encontrada.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Presença */}
        <div className="border border-gray-100 rounded-lg p-3 hover:border-gray-200 transition-colors">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-gray-600">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">Presença</span>
              <div className="relative">
                <Info
                  className="h-3.5 w-3.5 text-gray-400 cursor-help hover:text-gray-600"
                  onMouseEnter={() => setTooltipHover("presenca")}
                  onMouseLeave={() => setTooltipHover(null)}
                />
                {tooltipHover === "presenca" && (
                  <div className="absolute z-20 bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-800 text-white text-xs rounded-lg p-2.5 w-56 shadow-lg pointer-events-none">
                    Percentual de presença em sessões deliberativas do plenário
                    da Câmara.
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800" />
                  </div>
                )}
              </div>
            </div>
            <span
              className={`text-sm font-bold px-3 py-1 rounded-full border ${getPresencaColor(
                presenca,
              )}`}
            >
              {presenca}%
            </span>
          </div>
        </div>

        {/* Botão "Mais detalhes" */}
        <button
          onClick={() => setShowMaisDetalhes(!showMaisDetalhes)}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 border-2 border-dashed border-emerald-300 rounded-xl text-sm font-medium text-emerald-700 bg-emerald-50/50 hover:bg-emerald-100 transition-all"
        >
          {showMaisDetalhes ? (
            <Minus className="h-4 w-4" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          {showMaisDetalhes ? "Menos detalhes" : "Mais detalhes"}
        </button>

        {/* Seções extras */}
        {showMaisDetalhes && (
          <div className="space-y-3 pt-1 animate-fadeIn">
            {gastoPerCapita != null && (
              <div className="border border-gray-100 rounded-lg p-3 bg-gray-50/50">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Gasto por Eleitor</span>
                </div>
                <p className="text-lg font-bold text-gray-800">
                  {formatMoney(gastoPerCapita)}
                </p>
                <p className="text-xs text-gray-500">
                  Estimativa com base nos votos recebidos
                </p>
              </div>
            )}

            {ranking != null && (
              <div className="border border-gray-100 rounded-lg p-3 bg-gray-50/50">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <MapPin className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">
                    Ranking em {politico.uf}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm mt-2">
                  <div>
                    <span className="text-gray-500">Gastos:</span>{" "}
                    <strong>{ranking.gastos}º</strong>
                  </div>
                  <div>
                    <span className="text-gray-500">Proposições:</span>{" "}
                    <strong>{ranking.proposicoes}º</strong>
                  </div>
                  <div>
                    <span className="text-gray-500">Presença:</span>{" "}
                    <strong>{ranking.presenca}º</strong>
                  </div>
                  <div>
                    <span className="text-gray-500">IREP:</span>{" "}
                    <strong>{ranking.irep}º</strong>
                  </div>
                </div>
              </div>
            )}

            {evolucao != null && (
              <div className="border border-gray-100 rounded-lg p-3 bg-gray-50/50">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  {evolucao >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-red-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-emerald-500" />
                  )}
                  <span className="text-sm font-medium">
                    Evolução vs. Média (3 anos)
                  </span>
                </div>
                <p
                  className={`text-lg font-bold ${
                    evolucao >= 0 ? "text-red-600" : "text-emerald-600"
                  }`}
                >
                  {evolucao >= 0 ? "+" : ""}
                  {evolucao.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500">
                  vs. média dos últimos 3 anos
                </p>
              </div>
            )}

            {palavras.length > 0 && (
              <div className="border border-gray-100 rounded-lg p-3 bg-gray-50/50">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Tag className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Áreas de Atuação</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {palavras.map((p, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full font-medium"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Trocas de partido */}
            <div className="border border-gray-100 rounded-lg p-3 bg-gray-50/50">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <Repeat className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Trocas de Partido</span>
              </div>
              <p className="text-lg font-bold text-gray-800">
                {trocas > 0 ? `${trocas} troca(s)` : "Nenhuma troca"}
              </p>
            </div>

            {/* ===== SEÇÃO DE ANALYTICS (MANTIDA DO SEU CÓDIGO ORIGINAL) ===== */}
            <div className="border border-gray-200 rounded-lg p-3 bg-gray-50/50">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-gray-600">
                  <ShieldAlert className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">
                    Análise de Anomalias
                  </span>
                </div>
                <button
                  onClick={async () => {
                    if (!analytics && !loadingAnalytics) {
                      setLoadingAnalytics(true);
                      try {
                        const { data } = await api.get(
                          `/analytics/politico/${politico.id}`,
                        );
                        setAnalytics(data);
                      } catch (e) {
                        console.error("Erro ao carregar analytics:", e);
                      } finally {
                        setLoadingAnalytics(false);
                      }
                    }
                  }}
                  className="text-xs text-emerald-600 hover:underline"
                >
                  {analytics ? "✓ Carregado" : "Carregar análise"}
                </button>
              </div>

              {loadingAnalytics ? (
                <div className="flex items-center gap-2 text-xs text-gray-400 py-2">
                  <Loader2 className="h-3 w-3 animate-spin" /> Calculando
                  métricas...
                </div>
              ) : analytics ? (
                <div className="space-y-3">
                  <RiskBadge
                    score={analytics.risk_score?.score}
                    nivel={analytics.risk_score?.nivel}
                    redFlags={analytics.risk_score?.red_flags || []}
                    hhi={analytics.hhi?.hhi}
                    benfordSignificativo={analytics.benford?.significativo}
                    pctRedondos={analytics.valores_redondos?.percentual}
                    top1Pct={analytics.hhi?.top1_pct}
                    zPartido={analytics.z_scores?.partido}
                    zEstado={analytics.z_scores?.estado}
                  />

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white rounded p-2 border border-gray-100">
                      <span className="text-gray-500">HHI</span>
                      <p className="font-bold text-gray-800">
                        {analytics.hhi?.hhi
                          ? analytics.hhi.hhi.toFixed(0)
                          : "—"}
                      </p>
                      <span className="text-gray-400">
                        {analytics.hhi?.nivel || "—"}
                      </span>
                    </div>
                    <div className="bg-white rounded p-2 border border-gray-100">
                      <span className="text-gray-500">Benford χ²</span>
                      <p
                        className={`font-bold ${
                          analytics.benford?.significativo
                            ? "text-red-600"
                            : "text-gray-800"
                        }`}
                      >
                        {analytics.benford?.chi2
                          ? analytics.benford.chi2.toFixed(1)
                          : "—"}
                      </p>
                      <span className="text-gray-400">
                        {analytics.benford?.significativo
                          ? "Suspeito"
                          : "Normal"}
                      </span>
                    </div>
                    <div className="bg-white rounded p-2 border border-gray-100">
                      <span className="text-gray-500">Valores Redondos</span>
                      <p
                        className={`font-bold ${
                          (analytics.valores_redondos?.percentual || 0) > 30
                            ? "text-red-600"
                            : "text-gray-800"
                        }`}
                      >
                        {analytics.valores_redondos?.percentual != null
                          ? `${analytics.valores_redondos.percentual}%`
                          : "—"}
                      </p>
                    </div>
                    <div className="bg-white rounded p-2 border border-gray-100">
                      <span className="text-gray-500">Top Fornecedor</span>
                      <p
                        className={`font-bold ${
                          (analytics.hhi?.top1_pct || 0) > 50
                            ? "text-red-600"
                            : "text-gray-800"
                        }`}
                      >
                        {analytics.hhi?.top1_pct != null
                          ? `${analytics.hhi.top1_pct}%`
                          : "—"}
                      </p>
                    </div>
                  </div>

                  {/* Z-scores */}
                  <div className="text-xs text-gray-500 bg-white rounded p-2 border border-gray-100">
                    <p>
                      Z-score Partido:{" "}
                      {analytics.z_scores?.partido != null
                        ? analytics.z_scores.partido.toFixed(2)
                        : "—"}
                    </p>
                    <p>
                      Z-score Estado:{" "}
                      {analytics.z_scores?.estado != null
                        ? analytics.z_scores.estado.toFixed(2)
                        : "—"}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-gray-400 italic py-2">
                  Clique para carregar as métricas de anomalias.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Barra IREP */}
        <div className="pt-2">
          <div className="flex justify-between items-center text-xs text-gray-500 mb-2">
            <span className="font-medium">
              Eficiência:{" "}
              <span className="text-gray-700">{getEficienciaTexto(score)}</span>
            </span>
            <span className="text-gray-400">
              {politico.ultima_atualizacao
                ? new Date(politico.ultima_atualizacao).toLocaleDateString(
                    "pt-BR",
                  )
                : "-"}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${getProgressColor(
                score,
              )}`}
              style={{ width: `${Math.min(100, score)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0</span>
            <span>100</span>
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
        .animate-fadeIn { animation: fadeIn 0.25s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
};

export default CardPolitico;
