// frontend/src/components/RiskBadge.jsx
import React, { useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Shield,
  ShieldX,
  Info,
  X,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  DollarSign,
  Hash,
  PieChart,
  Users,
  Building2,
  Calculator,
  Target,
  Scale,
} from "lucide-react";

// ===================== Configuração de níveis =====================
const configNiveis = {
  CRÍTICO: {
    icon: ShieldX,
    bg: "bg-red-50",
    text: "text-red-700",
    border: "border-red-200",
    dot: "bg-red-500",
    label: "Crítico",
    desc: "Múltiplas anomalias graves detectadas. Recomenda-se investigação detalhada dos gastos.",
    explicacao:
      "O Risco Crítico (≥ 0.75) indica que o deputado atingiu pontuação máxima em vários indicadores simultaneamente. " +
      "Isso significa: alta concentração de fornecedores (HHI > 2500), distribuição de valores fora do padrão Benford, " +
      "muitos valores redondos e/ou gastos muito acima dos colegas de partido/estado. Estatisticamente, é extremamente " +
      "improvável que tantas anomalias ocorram por acaso. Recomenda-se auditoria detalhada.",
  },
  ALTO: {
    icon: ShieldAlert,
    bg: "bg-orange-50",
    text: "text-orange-700",
    border: "border-orange-200",
    dot: "bg-orange-500",
    label: "Alto",
    desc: "Anomalias significativas em mais de um indicador. Merece atenção e monitoramento.",
    explicacao:
      "O Risco Alto (0.55 a 0.74) significa que pelo menos dois indicadores de anomalia foram acionados. " +
      "Não é prova de irregularidade — pode haver explicações legítimas (ex: contratos de aluguel mensal fixo). " +
      "Mas é um sinal de alerta que justifica verificação.",
  },
  MÉDIO: {
    icon: Shield,
    bg: "bg-yellow-50",
    text: "text-yellow-700",
    border: "border-yellow-200",
    dot: "bg-yellow-500",
    label: "Médio",
    desc: "Alguns indicadores fora do padrão. Pode ser variação natural ou amostra pequena.",
    explicacao:
      "O Risco Médio (0.35 a 0.54) geralmente indica que um indicador foi acionado, mas os demais estão normais. " +
      "Isso pode acontecer com deputados que têm poucas transações ou que concentram gastos em contratos legítimos. " +
      "Vale acompanhar, mas sem alarme.",
  },
  BAIXO: {
    icon: ShieldCheck,
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    border: "border-emerald-200",
    dot: "bg-emerald-500",
    label: "Baixo",
    desc: "Dentro dos padrões normais de gastos. Sem anomalias detectadas nos indicadores analisados.",
    explicacao:
      "O Risco Baixo (< 0.35) indica que nenhum indicador de anomalia foi acionado, ou que o volume de gastos é " +
      "muito pequeno para análise estatística confiável (spending cap). Isso não significa que os gastos são perfeitos.",
  },
};

// ===================== Status (para diagnóstico) =====================
const statusMap = {
  critico: {
    icon: AlertTriangle,
    color: "text-red-500 bg-red-100 border-red-200",
  },
  alto: {
    icon: TrendingUp,
    color: "text-orange-500 bg-orange-100 border-orange-200",
  },
  medio: {
    icon: Activity,
    color: "text-yellow-500 bg-yellow-100 border-yellow-200",
  },
  baixo: {
    icon: CheckCircle2,
    color: "text-emerald-500 bg-emerald-100 border-emerald-200",
  },
  info: {
    icon: HelpCircle,
    color: "text-blue-500 bg-blue-100 border-blue-200",
  },
  warning: {
    icon: AlertTriangle,
    color: "text-amber-500 bg-amber-100 border-amber-200",
  },
};

const StatusDot = ({ nivel }) => {
  const s = statusMap[nivel] || statusMap.info;
  return (
    <span
      className={`inline-flex items-center justify-center w-5 h-5 rounded-full border ${s.color} flex-shrink-0`}
    >
      <s.icon className="h-3 w-3" />
    </span>
  );
};

// ===================== Accordion Interno =====================
const Accordion = ({
  title,
  icon: TitleIcon,
  children,
  defaultOpen = false,
}) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden bg-white">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-2 p-3 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          {TitleIcon && (
            <TitleIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
          )}
          <span className="text-sm font-semibold text-gray-800 truncate">
            {title}
          </span>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-gray-400 flex-shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open && (
        <div className="px-3 pb-3 text-sm text-gray-600 space-y-3">
          {children}
        </div>
      )}
    </div>
  );
};

// ===================== Card de explicação =====================
const ExplainCard = ({ icon: Icon, title, formula, children }) => (
  <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
    <div className="flex items-center gap-2 mb-2">
      <div className="w-8 h-8 rounded-lg bg-white border border-gray-200 flex items-center justify-center flex-shrink-0">
        <Icon className="h-4 w-4 text-indigo-500" />
      </div>
      <div>
        <p className="font-semibold text-gray-800 text-xs">{title}</p>
        {formula && (
          <p className="text-[10px] text-gray-400 font-mono">{formula}</p>
        )}
      </div>
    </div>
    <div className="text-xs text-gray-600 space-y-1.5">{children}</div>
  </div>
);

// ===================== Formatação =====================
const formatMoney = (v) => {
  if (v == null) return "—";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(v);
};

// ===================== COMPONENTE PRINCIPAL =====================
const RiskBadge = ({
  score,
  nivel,
  redFlags = [],
  hhi,
  benfordChi2,
  benfordSignificativo,
  pctRedondos,
  top1Pct,
  zPartido,
  zEstado,
  nTransacoes,
  gastoTotal,
}) => {
  const cfg = configNiveis[nivel] || configNiveis.BAIXO;
  const { icon: Icon, bg, text, border, dot, label, desc } = cfg;
  const [open, setOpen] = useState(false);

  const diagnosticos = [];

  // ── HHI ──
  if (hhi != null) {
    if (hhi > 5000)
      diagnosticos.push({
        nivel: "critico",
        titulo: "Concentração Extrema de Fornecedores",
        texto: `HHI de ${hhi.toFixed(0)} — praticamente todo o valor vai para um único fornecedor. Isso pode indicar falta de cotação de preços.`,
      });
    else if (hhi > 2500)
      diagnosticos.push({
        nivel: "alto",
        titulo: "Concentração Alta",
        texto: `HHI de ${hhi.toFixed(0)} — gastos bastante concentrados. Pode ser legítimo (ex: contrato de aluguel), mas merece verificação.`,
      });
    else if (hhi > 1500)
      diagnosticos.push({
        nivel: "medio",
        titulo: "Concentração Moderada",
        texto: `HHI de ${hhi.toFixed(0)} — diversificação razoável de fornecedores.`,
      });
    else
      diagnosticos.push({
        nivel: "baixo",
        titulo: "Fornecedores Diversificados",
        texto: `HHI de ${hhi.toFixed(0)} — gastos bem distribuídos entre diferentes fornecedores.`,
      });
  }

  // ── Benford ──
  if (benfordChi2 != null) {
    if (benfordSignificativo) {
      diagnosticos.push({
        nivel: "critico",
        titulo: "Padrão Anômalo nos Valores",
        texto: `χ² = ${Number(benfordChi2).toFixed(1)} — os primeiros dígitos dos valores não seguem o padrão natural. Em dados reais, o dígito 1 aparece em ~30% dos casos. Quando isso não acontece, pode indicar valores inventados.`,
      });
    } else {
      diagnosticos.push({
        nivel: "baixo",
        titulo: "Distribuição Normal",
        texto: `χ² = ${Number(benfordChi2).toFixed(1)} — a distribuição dos primeiros dígitos segue o padrão natural esperado.`,
      });
    }
  } else {
    diagnosticos.push({
      nivel: "warning",
      titulo: "Amostra Insuficiente",
      texto: `Apenas ${nTransacoes || "?"} transações disponíveis (mínimo: 50). A análise de Benford não pôde ser calculada. O score de risco pode estar subestimado por falta de dados.`,
    });
  }

  // ── Valores Redondos ──
  if (pctRedondos != null) {
    if (pctRedondos > 50)
      diagnosticos.push({
        nivel: "critico",
        titulo: "Excesso de Valores Redondos",
        texto: `${pctRedondos}% dos valores são múltiplos de R$ 100, 500 ou 1.000. No mundo real, quase toda transação tem centavos (impostos, taxas). Isso sugere valores arbitrados.`,
      });
    else if (pctRedondos > 30)
      diagnosticos.push({
        nivel: "alto",
        titulo: "Valores Redondos Elevados",
        texto: `${pctRedondos}% de valores redondos — acima dos 20-30% esperados.`,
      });
    else
      diagnosticos.push({
        nivel: "baixo",
        titulo: "Valores com Centavos",
        texto: `${pctRedondos}% de valores redondos — a maioria tem centavos, como esperado.`,
      });
  }

  // ── Fornecedor Dominante ──
  if (top1Pct != null) {
    if (top1Pct > 75)
      diagnosticos.push({
        nivel: "critico",
        titulo: "Dependência Quase Total",
        texto: `${top1Pct}% dos gastos em um único CNPJ. De cada R$ 100, R$ ${top1Pct.toFixed(0)} vão para a mesma empresa.`,
      });
    else if (top1Pct > 50)
      diagnosticos.push({
        nivel: "alto",
        titulo: "Fornecedor Predominante",
        texto: `${top1Pct}% no principal fornecedor — mais da metade do orçamento.`,
      });
    else
      diagnosticos.push({
        nivel: "baixo",
        titulo: "Boa Distribuição",
        texto: `${top1Pct}% no principal fornecedor — distribuição saudável.`,
      });
  }

  // ── Z-scores ──
  if (zPartido != null && zPartido > 2)
    diagnosticos.push({
      nivel: "alto",
      titulo: "Gasto Acima dos Colegas de Partido",
      texto: `${zPartido.toFixed(1)} desvios-padrão acima da média. Gasta mais que ~95% dos colegas.`,
    });
  if (zEstado != null && zEstado > 2)
    diagnosticos.push({
      nivel: "alto",
      titulo: "Gasto Acima dos Colegas de Estado",
      texto: `${zEstado.toFixed(1)} desvios-padrão acima da média do estado.`,
    });

  if (diagnosticos.length === 0) {
    diagnosticos.push({
      nivel: "info",
      titulo: "Aguardando Dados",
      texto:
        "Clique em 'Carregar análise' para consultar a API e gerar o diagnóstico.",
    });
  }

  return (
    <>
      {/* Badge clicável */}
      <button
        onClick={() => setOpen(true)}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border ${bg} ${border} hover:shadow-md transition-all text-left group`}
      >
        <span
          className={`w-8 h-8 rounded-full ${bg} border ${border} flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform`}
        >
          <Icon className={`h-4 w-4 ${text}`} />
        </span>
        <div className="flex-grow min-w-0">
          <p className={`text-sm font-bold ${text}`}>Risco {label}</p>
          <p className="text-xs text-gray-500 truncate">
            Score {score?.toFixed(2) || "—"} • {redFlags.length} alerta(s)
          </p>
        </div>
        <Info className="h-4 w-4 text-gray-400 group-hover:text-gray-600 flex-shrink-0" />
      </button>

      {/* Modal */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center bg-gray-900/60 backdrop-blur-sm p-4 pt-12 overflow-y-auto"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-lg w-full animate-fadeIn ring-1 ring-gray-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Cabeçalho */}
            <div className="sticky top-0 bg-white rounded-t-2xl border-b border-gray-100 px-5 py-4 flex items-center justify-between gap-3 z-10">
              <div className="flex items-center gap-3">
                <span
                  className={`w-10 h-10 rounded-xl ${bg} border ${border} flex items-center justify-center`}
                >
                  <Icon className={`h-5 w-5 ${text}`} />
                </span>
                <div>
                  <h3 className="font-bold text-gray-900">Análise de Risco</h3>
                  <p className="text-sm text-gray-500">
                    Nível {label} • Score {score?.toFixed(3) || "—"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Conteúdo */}
            <div className="px-5 py-4 space-y-3 max-h-[70vh] overflow-y-auto">
              {/* Descrição do nível */}
              <div className={`p-3 rounded-xl ${bg} border ${border}`}>
                <p className={`text-sm font-medium ${text}`}>{desc}</p>
              </div>

              {/* Alertas de amostra pequena */}
              {benfordChi2 == null && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-amber-800 text-xs">
                      Análise Limitada
                    </p>
                    <p className="text-amber-700 text-xs mt-0.5">
                      Apenas <strong>{nTransacoes || "?"} transações</strong>{" "}
                      disponíveis. O mínimo para análise confiável é 50. O score
                      pode estar <strong>subestimado</strong>.
                    </p>
                  </div>
                </div>
              )}

              {gastoTotal != null && gastoTotal < 100000 && (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 flex items-start gap-2">
                  <Info className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-blue-800 text-xs">
                      Spending Cap Ativado
                    </p>
                    <p className="text-blue-700 text-xs mt-0.5">
                      Gasto total de {formatMoney(gastoTotal)} (abaixo de R$ 100
                      mil). Score limitado automaticamente.
                    </p>
                  </div>
                </div>
              )}

              {/* Diagnóstico */}
              <Accordion
                title="Diagnóstico Automático"
                icon={Activity}
                defaultOpen={true}
              >
                {diagnosticos.map((d, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 p-2.5 rounded-xl bg-gray-50 border border-gray-100"
                  >
                    <StatusDot nivel={d.nivel} />
                    <div>
                      <p className="font-semibold text-gray-800 text-xs">
                        {d.titulo}
                      </p>
                      <p className="text-gray-600 text-xs mt-0.5 leading-relaxed">
                        {d.texto}
                      </p>
                    </div>
                  </div>
                ))}
              </Accordion>

              {/* Como é calculado */}
              <Accordion title="Como o Score é Calculado?" icon={Calculator}>
                <p className="text-xs text-gray-600">
                  O Risk Score (0 a 1) combina indicadores de anomalia. Quanto
                  mais próximo de 1, mais sinais de alerta.
                </p>
                <p className="text-xs font-mono text-center bg-gray-100 rounded-lg p-2">
                  Score = Base (HHI) + Penalidades
                </p>

                <ExplainCard
                  icon={Building2}
                  title="Base: HHI (Concentração)"
                  formula="> 3000 = 0.90 | > 2500 = 0.70 | > 1500 = 0.40 | ≤ 1500 = 0.20"
                >
                  <p>
                    Mede se os gastos estão concentrados em poucos fornecedores.
                    Quanto mais pulverizado, melhor.
                  </p>
                </ExplainCard>

                <ExplainCard
                  icon={Hash}
                  title="+0.15: Benford"
                  formula="χ² > 15.51 (p < 0.05)"
                >
                  <p>
                    Em dados reais, o dígito 1 aparece em ~30% dos valores.
                    Desvios sugerem números inventados.
                  </p>
                </ExplainCard>

                <ExplainCard
                  icon={DollarSign}
                  title="+0.10: Valores Redondos"
                  formula="> 20% dos valores"
                >
                  <p>
                    Valores reais têm centavos. Muitos valores "cheios" sugerem
                    números arbitrados.
                  </p>
                </ExplainCard>

                <ExplainCard
                  icon={PieChart}
                  title="+0.10: Fornecedor Dominante"
                  formula="> 50% em um CNPJ"
                >
                  <p>Mais da metade do orçamento em uma única empresa.</p>
                </ExplainCard>

                <ExplainCard
                  icon={Users}
                  title="+0.08 cada: Z-score"
                  formula="> 2.0 vs partido/estado"
                >
                  <p>
                    Gasta muito mais que os colegas do mesmo partido ou estado.
                  </p>
                </ExplainCard>

                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3">
                  <p className="font-semibold text-amber-800 text-xs">
                    Spending Cap
                  </p>
                  <p className="text-amber-700 text-xs mt-0.5">
                    Para amostras pequenas: &lt; R$ 100k → máx 0.34 | &lt; R$
                    200k → máx 0.54 | &lt; R$ 400k → máx 0.74
                  </p>
                </div>
              </Accordion>

              {/* Red Flags */}
              {redFlags.length > 0 && (
                <Accordion
                  title={`Alertas (${redFlags.length})`}
                  icon={AlertTriangle}
                >
                  {redFlags.map((f, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 text-xs text-red-700 bg-red-50 rounded-lg p-2.5 border border-red-200"
                    >
                      <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </div>
                  ))}
                </Accordion>
              )}
            </div>

            {/* Rodapé */}
            <div className="px-5 py-3 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
              <p className="text-[10px] text-gray-400 text-center">
                Análise estatística. Não constitui prova de irregularidade.
                Presunção de inocência se aplica.
              </p>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
        .animate-fadeIn { animation: fadeIn 0.2s ease-out; }
      `}</style>
    </>
  );
};

export default RiskBadge;
