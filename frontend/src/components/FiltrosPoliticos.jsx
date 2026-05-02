import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  SlidersHorizontal,
  ChevronDown,
  X,
  ArrowUpDown,
} from "lucide-react";
import api from "../services/api";

const ordenacoes = [
  { value: "irep_score-desc", label: "Maior IREP" },
  { value: "irep_score-asc", label: "Menor IREP" },
  { value: "gasto_total-desc", label: "Maiores Gastos" },
  { value: "gasto_total-asc", label: "Menores Gastos" },
  { value: "num_proposicoes-desc", label: "Mais Proposições" },
  { value: "num_proposicoes-asc", label: "Menos Proposições" },
  { value: "presenca_percentual-desc", label: "Maior Presença" },
  { value: "presenca_percentual-asc", label: "Menor Presença" },
  { value: "nome-asc", label: "Nome (A-Z)" },
  { value: "nome-desc", label: "Nome (Z-A)" },
];

const FiltrosPoliticos = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    nome: "",
    partido: "",
    uf: "",
    cargo: "",
    gastoMin: "",
    gastoMax: "",
    propsMin: "",
    propsMax: "",
    presencaMin: "",
    presencaMax: "",
    minIrep: 0,
    maxIrep: 100,
    ordenarPor: "irep_score-desc",
  });
  const [partidos, setPartidos] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    const fetchPartidos = async () => {
      try {
        const response = await api.get("/politicos/partidos");
        setPartidos(response.data);
      } catch (error) {
        console.error("Erro ao buscar partidos:", error);
      }
    };
    fetchPartidos();
  }, []);

  const buildBackendFilters = useCallback((currentFilters) => {
    const [ordenarPor, ordem] = currentFilters.ordenarPor.split("-");
    return {
      nome: currentFilters.nome || undefined,
      partido: currentFilters.partido || undefined,
      uf: currentFilters.uf || undefined,
      cargo: currentFilters.cargo || undefined,
      gasto_min: currentFilters.gastoMin
        ? parseFloat(currentFilters.gastoMin)
        : undefined,
      gasto_max: currentFilters.gastoMax
        ? parseFloat(currentFilters.gastoMax)
        : undefined,
      props_min: currentFilters.propsMin
        ? parseInt(currentFilters.propsMin)
        : undefined,
      props_max: currentFilters.propsMax
        ? parseInt(currentFilters.propsMax)
        : undefined,
      presenca_min: currentFilters.presencaMin
        ? parseFloat(currentFilters.presencaMin)
        : undefined,
      presenca_max: currentFilters.presencaMax
        ? parseFloat(currentFilters.presencaMax)
        : undefined,
      min_irep: currentFilters.minIrep > 0 ? currentFilters.minIrep : undefined,
      max_irep:
        currentFilters.maxIrep < 100 ? currentFilters.maxIrep : undefined,
      ordenar_por: ordenarPor,
      ordem: ordem,
    };
  }, []);

  const handleChange = (field, value) => {
    setFilters((prev) => {
      const newFilters = { ...prev, [field]: value };
      // Notifica o componente pai com o formato do backend
      onFilterChange(buildBackendFilters(newFilters));
      return newFilters;
    });
  };

  const clearFilters = () => {
    const empty = {
      nome: "",
      partido: "",
      uf: "",
      cargo: "",
      gastoMin: "",
      gastoMax: "",
      propsMin: "",
      propsMax: "",
      presencaMin: "",
      presencaMax: "",
      minIrep: 0,
      maxIrep: 100,
      ordenarPor: "irep_score-desc",
    };
    setFilters(empty);
    onFilterChange(buildBackendFilters(empty));
  };

  const hasActiveFilters = () => {
    return (
      filters.nome ||
      filters.partido ||
      filters.uf ||
      filters.cargo ||
      filters.gastoMin ||
      filters.gastoMax ||
      filters.propsMin ||
      filters.propsMax ||
      filters.presencaMin ||
      filters.presencaMax ||
      filters.minIrep > 0 ||
      filters.maxIrep < 100 ||
      filters.ordenarPor !== "irep_score-desc"
    );
  };

  // Sliders IREP com validação cruzada
  const handleMinIrepChange = (e) => {
    const val = parseInt(e.target.value);
    if (val <= filters.maxIrep) {
      handleChange("minIrep", val);
    }
  };
  const handleMaxIrepChange = (e) => {
    const val = parseInt(e.target.value);
    if (val >= filters.minIrep) {
      handleChange("maxIrep", val);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
      {/* Linha principal */}
      <div className="flex flex-wrap gap-3 items-end">
        {/* Busca por nome */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Nome
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Digite o nome..."
              value={filters.nome}
              onChange={(e) => handleChange("nome", e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 text-sm"
            />
          </div>
        </div>

        {/* Partido */}
        <div className="min-w-[150px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Partido
          </label>
          <select
            value={filters.partido}
            onChange={(e) => handleChange("partido", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 text-sm"
          >
            <option value="">Todos</option>
            {partidos.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        {/* UF */}
        <div className="min-w-[100px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Estado
          </label>
          <select
            value={filters.uf}
            onChange={(e) => handleChange("uf", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 text-sm"
          >
            <option value="">Todos</option>
            {[
              "AC",
              "AL",
              "AP",
              "AM",
              "BA",
              "CE",
              "DF",
              "ES",
              "GO",
              "MA",
              "MT",
              "MS",
              "MG",
              "PA",
              "PB",
              "PR",
              "PE",
              "PI",
              "RJ",
              "RN",
              "RS",
              "RO",
              "RR",
              "SC",
              "SP",
              "SE",
              "TO",
            ].map((uf) => (
              <option key={uf} value={uf}>
                {uf}
              </option>
            ))}
          </select>
        </div>

        {/* Ordenação */}
        <div className="min-w-[180px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            <ArrowUpDown className="inline h-3 w-3 mr-1" />
            Ordenar por
          </label>
          <select
            value={filters.ordenarPor}
            onChange={(e) => handleChange("ordenarPor", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 text-sm"
          >
            {ordenacoes.map((op) => (
              <option key={op.value} value={op.value}>
                {op.label}
              </option>
            ))}
          </select>
        </div>

        {/* Botão filtros avançados */}
        <div className="flex items-end pb-1">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center gap-2 px-4 py-2 border rounded-lg text-sm transition ${
              showAdvanced
                ? "bg-emerald-50 border-emerald-300 text-emerald-700"
                : "border-gray-300 hover:bg-gray-50 text-gray-600"
            }`}
          >
            <SlidersHorizontal className="h-4 w-4" />
            Filtros
            <ChevronDown
              className={`h-4 w-4 transition-transform ${showAdvanced ? "rotate-180" : ""}`}
            />
          </button>
        </div>

        {hasActiveFilters() && (
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-red-500 hover:text-red-700 text-sm flex items-center gap-1"
          >
            <X className="h-4 w-4" /> Limpar
          </button>
        )}
      </div>

      {/* Painel de filtros avançados */}
      {showAdvanced && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid md:grid-cols-3 gap-4">
            {/* Gastos */}
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">
                💰 Gastos (CEAP)
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Mínimo (R$)</label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.gastoMin}
                    onChange={(e) => handleChange("gastoMin", e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-200"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Máximo (R$)</label>
                  <input
                    type="number"
                    placeholder="∞"
                    value={filters.gastoMax}
                    onChange={(e) => handleChange("gastoMax", e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-200"
                  />
                </div>
              </div>
            </div>

            {/* Proposições */}
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">
                📋 Proposições
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Mínimo</label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.propsMin}
                    onChange={(e) => handleChange("propsMin", e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-200"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Máximo</label>
                  <input
                    type="number"
                    placeholder="∞"
                    value={filters.propsMax}
                    onChange={(e) => handleChange("propsMax", e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-200"
                  />
                </div>
              </div>
            </div>

            {/* Presença */}
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">
                📅 Presença (%)
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Mínimo</label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.presencaMin}
                    onChange={(e) =>
                      handleChange("presencaMin", e.target.value)
                    }
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-200"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Máximo</label>
                  <input
                    type="number"
                    placeholder="100"
                    value={filters.presencaMax}
                    onChange={(e) =>
                      handleChange("presencaMax", e.target.value)
                    }
                    className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-200"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Sliders IREP */}
          <div className="mt-4 bg-gray-50 rounded-lg p-3 border border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">
              🏆 IREP (pontuação)
            </h4>
            <div className="flex items-center gap-4">
              <span className="text-xs text-gray-500">0</span>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.minIrep}
                onChange={handleMinIrepChange}
                className="flex-1 h-1.5 bg-gray-200 rounded-full accent-emerald-600"
              />
              <span className="text-xs text-gray-500">100</span>
              <span className="text-sm font-medium text-emerald-700 w-20 text-right">
                {filters.minIrep} – {filters.maxIrep}
              </span>
            </div>
            <div className="flex items-center gap-4 mt-2">
              <span className="text-xs text-gray-500">0</span>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.maxIrep}
                onChange={handleMaxIrepChange}
                className="flex-1 h-1.5 bg-gray-200 rounded-full accent-emerald-600"
              />
              <span className="text-xs text-gray-500">100</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FiltrosPoliticos;
