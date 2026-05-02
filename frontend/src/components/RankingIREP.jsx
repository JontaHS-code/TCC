import React, { useState, useEffect } from "react";
import { Trophy, Medal, Loader2, Info } from "lucide-react";
import api from "../services/api";
import CardPolitico from "./CardPolitico";

const RankingIREP = () => {
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRanking = async () => {
      try {
        const response = await api.get("/ranking/irep?limit=50");
        setRanking(response.data);
      } catch (error) {
        console.error("Erro ao buscar ranking:", error);
        setRanking([]);
      } finally {
        setLoading(false);
      }
    };
    fetchRanking();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-gray-500 gap-3">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="font-medium">Carregando ranking IREP...</span>
      </div>
    );
  }

  const getMedalIcon = (index) => {
    if (index === 0) return <Medal className="h-5 w-5 text-yellow-500" />;
    if (index === 1) return <Medal className="h-5 w-5 text-gray-400" />;
    if (index === 2) return <Medal className="h-5 w-5 text-amber-600" />;
    return (
      <span className="text-sm font-bold text-gray-400 w-5 text-center">
        {index + 1}
      </span>
    );
  };

  return (
    <div>
      {/* Box explicativa */}
      <div className="mb-6 p-5 bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl shadow-sm">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <Trophy className="h-5 w-5 text-emerald-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">
              Índice de Relevância e Eficiência Política (IREP)
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed mb-3">
              O IREP varia de <strong className="text-gray-800">0 a 100</strong>{" "}
              e combina três pilares:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
              <div className="bg-white rounded-lg px-3 py-2 border border-gray-200">
                <span className="font-semibold text-emerald-700">40%</span>
                <span className="text-gray-600 ml-1">
                  Produtividade legislativa
                </span>
              </div>
              <div className="bg-white rounded-lg px-3 py-2 border border-gray-200">
                <span className="font-semibold text-emerald-700">30%</span>
                <span className="text-gray-600 ml-1">Eficiência de gastos</span>
              </div>
              <div className="bg-white rounded-lg px-3 py-2 border border-gray-200">
                <span className="font-semibold text-emerald-700">30%</span>
                <span className="text-gray-600 ml-1">Assiduidade</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Top 3 destacados */}
      {ranking.length >= 3 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {ranking.slice(0, 3).map((politico, idx) => (
            <div
              key={politico.id}
              className={`relative bg-white rounded-xl border-2 p-4 ${
                idx === 0
                  ? "border-yellow-400 shadow-md"
                  : idx === 1
                    ? "border-gray-300"
                    : "border-amber-500"
              }`}
            >
              <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center shadow-sm">
                {getMedalIcon(idx)}
              </div>
              <CardPolitico politico={politico} />
            </div>
          ))}
        </div>
      )}

      {/* Lista completa */}
      <div className="space-y-4">
        {ranking.slice(0).map((politico, idx) => (
          <div key={politico.id} className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mt-4 font-bold text-sm text-gray-600">
              {idx + 1}
            </div>
            <div className="flex-1">
              <CardPolitico politico={politico} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RankingIREP;
