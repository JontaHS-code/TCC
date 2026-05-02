// frontend/src/components/GastosResumo.jsx
import React, { useState, useEffect, useMemo } from "react";
import {
  Plus,
  Minus,
  Building2,
  BookOpen,
  Scale,
  ShieldCheck,
  CalendarDays,
  Loader2,
  AlertTriangle,
  DollarSign,
  Users,
  PieChart,
  TrendingUp,
  Search,
} from "lucide-react";

const formatCurrency = (value) => {
  if (value === undefined || value === null) return "—";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
};

const ExpandableSection = ({
  title,
  subtitle,
  children,
  defaultOpen = false,
  icon: Icon,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-200 rounded-xl mb-3 bg-white shadow-sm overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex justify-between items-center p-4 text-left hover:bg-gray-50"
      >
        <div className="flex items-center gap-3 min-w-0">
          {Icon && <Icon className="h-5 w-5 text-gray-400 flex-shrink-0" />}
          <div className="min-w-0">
            <span className="font-semibold text-gray-800 text-sm">{title}</span>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-0.5 truncate">
                {subtitle}
              </p>
            )}
          </div>
        </div>
        {isOpen ? (
          <Minus className="h-5 w-5 text-gray-400 flex-shrink-0" />
        ) : (
          <Plus className="h-5 w-5 text-gray-400 flex-shrink-0" />
        )}
      </button>
      {isOpen && (
        <div className="px-4 pb-4 border-t border-gray-100">{children}</div>
      )}
    </div>
  );
};

const PowerSection = ({
  poder,
  cor,
  icone: Icon,
  valor,
  loading,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const colorMap = {
    verde: {
      bg: "from-emerald-600 to-teal-500",
      light: "text-emerald-100",
      iconBg: "text-emerald-200",
    },
    azul: {
      bg: "from-blue-600 to-blue-500",
      light: "text-blue-100",
      iconBg: "text-blue-200",
    },
    amarelo: {
      bg: "from-yellow-500 to-amber-500",
      light: "text-yellow-100",
      iconBg: "text-yellow-200",
    },
    cinza: {
      bg: "from-slate-600 to-slate-500",
      light: "text-slate-100",
      iconBg: "text-slate-200",
    },
  };
  const estilo = colorMap[cor] || colorMap.verde;

  return (
    <div className="rounded-xl shadow-lg mb-4 overflow-hidden">
      <div className={`bg-gradient-to-r ${estilo.bg} text-white p-5`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Icon className={`h-8 w-8 ${estilo.iconBg}`} />
            <div>
              <p className={`text-sm ${estilo.light}`}>{poder}</p>
              <div className="flex items-baseline gap-2 mt-1">
                <span className={`text-sm ${estilo.light}`}>
                  Total executado (pago):
                </span>
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin text-white" />
                ) : (
                  <span className="text-xl font-bold">
                    {valor !== undefined ? formatCurrency(valor) : "—"}
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 rounded-full hover:bg-white/20"
          >
            {isOpen ? (
              <Minus className="h-6 w-6" />
            ) : (
              <Plus className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>
      {isOpen && (
        <div className="bg-white border-t border-gray-100 p-5 space-y-3 text-sm text-gray-700 animate-fadeIn">
          {children}
        </div>
      )}
    </div>
  );
};

// ===================== COMPONENTE PRINCIPAL =====================
export default function GastosResumo() {
  const [executivo, setExecutivo] = useState(null);
  const [csvData, setCsvData] = useState([]);
  const [loadingExec, setLoadingExec] = useState(true);
  const [loadingCsv, setLoadingCsv] = useState(true);
  const [erroExec, setErroExec] = useState(null);
  const [busca, setBusca] = useState("");

  // EXECUTIVO
  useEffect(() => {
    fetch("http://127.0.0.1:8000/gastos/resumo-detalhado?ano=2025")
      .then((r) => r.json())
      .then((d) => {
        setExecutivo(d);
        setLoadingExec(false);
      })
      .catch((e) => {
        setErroExec(e.message);
        setLoadingExec(false);
      });
  }, []);

  // CSV - CORRIGIDO (APENAS 2025)
  useEffect(() => {
    console.log("🟢 useEffect CSV iniciado");

    fetch("/despesas_2023_2026.csv")
      .then((r) => r.text())
      .then((texto) => {
        console.log("📄 CSV carregado:", texto.length, "bytes");

        const linhas = texto.split("\n");

        const idxNome = 0; // txNomeParlamentar
        const idxDescricao = 9; // txtDescricao
        const idxValor = 19; // vlrLiquido
        const idxAno = 21; // numAno

        const agrupado = {};
        let processadas = 0;
        let filtradasAno = 0;

        for (let i = 1; i < linhas.length; i++) {
          const linha = linhas[i].trim();
          if (!linha) continue;

          const cols = linha.split(",");
          if (cols.length < 22) continue;

          // FILTRA APENAS 2025
          const ano = parseInt(cols[idxAno]) || 0;
          if (ano !== 2025) {
            filtradasAno++;
            continue;
          }

          const nome = cols[idxNome]?.trim();
          const cat = cols[idxDescricao]?.trim();
          const valor = parseFloat(cols[idxValor]) || 0;

          if (!nome || valor <= 0) continue;
          if (nome.includes("LID.") || nome.includes("LIDERANÇA")) continue;

          processadas++;
          if (!agrupado[nome]) agrupado[nome] = { total: 0, categorias: {} };
          agrupado[nome].total += valor;
          agrupado[nome].categorias[cat] =
            (agrupado[nome].categorias[cat] || 0) + valor;
        }

        console.log("📊 Transações 2025:", processadas);
        console.log("📊 Filtradas (outros anos):", filtradasAno);

        const resultado = Object.entries(agrupado).map(([nome, info]) => ({
          nome,
          total: info.total,
          categorias: Object.entries(info.categorias)
            .map(([cat, val]) => ({ categoria: cat, valor: val }))
            .sort((a, b) => b.valor - a.valor),
        }));
        resultado.sort((a, b) => b.total - a.total);

        console.log("✅ Deputados em 2025:", resultado.length);

        setCsvData(resultado);
        setLoadingCsv(false);
      })
      .catch((err) => {
        console.error("❌ Erro CSV:", err);
        setLoadingCsv(false);
      });
  }, []);

  // AGREGAÇÕES
  const {
    totalGeral,
    totalDeputados,
    mediaGeral,
    maiorGasto,
    topCategorias,
    topDeputados,
    deputadosFiltrados,
  } = useMemo(() => {
    const totalGeral = csvData.reduce((acc, d) => acc + d.total, 0);
    const totalDeputados = csvData.length;
    const mediaGeral = totalDeputados > 0 ? totalGeral / totalDeputados : 0;
    const maiorGasto = csvData[0] || null;

    const catMap = {};
    csvData.forEach((d) => {
      d.categorias.forEach((c) => {
        catMap[c.categoria] = (catMap[c.categoria] || 0) + c.valor;
      });
    });
    const topCategorias = Object.entries(catMap)
      .map(([cat, val]) => ({ categoria: cat, valor: val }))
      .sort((a, b) => b.valor - a.valor);

    const topDeputados = csvData.slice(0, 10);
    const buscaLower = busca.toLowerCase();
    const deputadosFiltrados = buscaLower
      ? csvData.filter((d) => d.nome.toLowerCase().includes(buscaLower))
      : csvData;

    return {
      totalGeral,
      totalDeputados,
      mediaGeral,
      maiorGasto,
      topCategorias,
      topDeputados,
      deputadosFiltrados,
    };
  }, [csvData, busca]);

  if (loadingExec || loadingCsv) {
    return (
      <div className="flex justify-center py-12 text-gray-500 gap-3">
        <Loader2 className="h-6 w-6 animate-spin" /> Carregando...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-700 to-teal-600 bg-clip-text text-transparent">
          Orçamento 2025
        </h1>
        <p className="text-sm text-gray-500 mt-2">
          Visão consolidada dos poderes da União
        </p>
      </div>

      {/* EXECUTIVO */}
      <PowerSection
        poder="Poder Executivo Federal"
        cor="verde"
        icone={Building2}
        valor={executivo?.total}
        loading={loadingExec}
      >
        {executivo?.categorias?.map((cat) => (
          <ExpandableSection
            key={cat.nome}
            title={cat.nome}
            subtitle={`${cat.itens.length} órgãos • ${formatCurrency(cat.valor)}`}
          >
            <div className="overflow-x-auto max-h-80 overflow-y-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-100 sticky top-0">
                    <th className="p-2 text-left">Órgão</th>
                    <th className="p-2 text-right">Pago</th>
                  </tr>
                </thead>
                <tbody>
                  {cat.itens.map((org, idx) => (
                    <tr
                      key={idx}
                      className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                    >
                      <td className="p-2">{org.nome}</td>
                      <td className="p-2 text-right text-emerald-700 font-semibold">
                        {formatCurrency(org.valor)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ExpandableSection>
        ))}
      </PowerSection>

      {/* LEGISLATIVO */}
      <PowerSection
        poder="Poder Legislativo"
        cor="azul"
        icone={BookOpen}
        valor={totalGeral}
        loading={loadingCsv}
      >
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          <div className="bg-blue-50 rounded-xl p-3">
            <DollarSign className="h-4 w-4 text-blue-500 mb-1" />
            <p className="text-xs text-blue-600">Total CEAP</p>
            <p className="text-lg font-bold text-blue-800">
              {formatCurrency(totalGeral)}
            </p>
          </div>
          <div className="bg-emerald-50 rounded-xl p-3">
            <Users className="h-4 w-4 text-emerald-500 mb-1" />
            <p className="text-xs text-emerald-600">Deputados</p>
            <p className="text-lg font-bold text-emerald-800">
              {totalDeputados}
            </p>
          </div>
          <div className="bg-indigo-50 rounded-xl p-3">
            <TrendingUp className="h-4 w-4 text-indigo-500 mb-1" />
            <p className="text-xs text-indigo-600">Média</p>
            <p className="text-lg font-bold text-indigo-800">
              {formatCurrency(mediaGeral)}
            </p>
          </div>
          <div className="bg-amber-50 rounded-xl p-3">
            <PieChart className="h-4 w-4 text-amber-500 mb-1" />
            <p className="text-xs text-amber-600">Maior</p>
            <p className="text-sm font-bold text-amber-800 truncate">
              {maiorGasto?.nome || "—"}
            </p>
          </div>
        </div>

        <ExpandableSection
          title="Categorias de Gasto"
          subtitle={`${topCategorias.length} categorias`}
          icon={PieChart}
        >
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 sticky top-0">
                  <th className="p-2 text-left">Categoria</th>
                  <th className="p-2 text-right">Valor</th>
                </tr>
              </thead>
              <tbody>
                {topCategorias.map((c, idx) => (
                  <tr
                    key={idx}
                    className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="p-2 text-xs">{c.categoria}</td>
                    <td className="p-2 text-right text-xs font-mono">
                      {formatCurrency(c.valor)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ExpandableSection>

        <ExpandableSection title="Top 10 Deputados" icon={Users}>
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 sticky top-0">
                  <th className="p-2">#</th>
                  <th className="p-2 text-left">Deputado</th>
                  <th className="p-2 text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {topDeputados.map((d, idx) => (
                  <tr
                    key={idx}
                    className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="p-2 text-gray-400 font-bold">{idx + 1}</td>
                    <td className="p-2 text-xs">{d.nome}</td>
                    <td className="p-2 text-right text-xs text-emerald-700 font-semibold">
                      {formatCurrency(d.total)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ExpandableSection>

        <ExpandableSection
          title="Todos os Deputados"
          subtitle={`${deputadosFiltrados.length} deputados`}
          icon={Users}
        >
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm"
            />
          </div>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {deputadosFiltrados.map((dep, idx) => (
              <ExpandableSection
                key={idx}
                title={dep.nome}
                subtitle={`${formatCurrency(dep.total)} • ${dep.categorias.length} categorias`}
              >
                <div className="overflow-x-auto max-h-60 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-50 sticky top-0">
                        <th className="p-2 text-left">Categoria</th>
                        <th className="p-2 text-right">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dep.categorias.map((cat, cIdx) => (
                        <tr
                          key={cIdx}
                          className={cIdx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                        >
                          <td className="p-1.5 text-xs">{cat.categoria}</td>
                          <td className="p-1.5 text-right text-xs font-mono">
                            {formatCurrency(cat.valor)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ExpandableSection>
            ))}
          </div>
        </ExpandableSection>
      </PowerSection>

      <PowerSection poder="Poder Judiciário" cor="amarelo" icone={Scale}>
        <p className="text-sm text-gray-600">Dados via CNJ.</p>
      </PowerSection>
      <PowerSection poder="Órgãos Autônomos" cor="cinza" icone={ShieldCheck}>
        <p className="text-sm text-gray-600">TCU, MPF, DPU.</p>
      </PowerSection>

      <div className="text-center text-sm text-gray-400 pt-2">
        <CalendarDays className="h-4 w-4 inline mr-1" />
        Fonte: Dados Abertos da Câmara • CEAP 2025
      </div>
    </div>
  );
}
