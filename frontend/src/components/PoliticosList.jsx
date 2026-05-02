import React, { useState, useEffect, useRef } from "react";
import { Loader2, Search } from "lucide-react";
import FiltrosPoliticos from "./FiltrosPoliticos";
import CardPolitico from "./CardPolitico";
import api from "../services/api";

const PoliticosList = () => {
  const [politicos, setPoliticos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    ordenar_por: "irep_score",
    ordem: "desc",
  });
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(
      () => {
        const fetchPoliticos = async () => {
          setLoading(true);
          try {
            const params = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
              if (value !== undefined && value !== "" && value !== null) {
                params.append(key, value);
              }
            });
            // ⚠️ Não envia limite – o backend retorna todos
            const response = await api.get(`/politicos/?${params.toString()}`);
            setPoliticos(response.data);
          } catch (error) {
            console.error("Erro ao buscar políticos:", error);
            setPoliticos([]);
          } finally {
            setLoading(false);
          }
        };
        fetchPoliticos();
      },
      filters.nome ? 400 : 0,
    );

    return () => clearTimeout(timeoutRef.current);
  }, [filters]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  return (
    <div>
      <FiltrosPoliticos onFilterChange={handleFilterChange} />

      {loading ? (
        <div className="flex items-center justify-center py-16 text-gray-500 gap-3">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Buscando políticos...</span>
        </div>
      ) : politicos.length === 0 ? (
        <div className="flex flex-col items-center py-16 text-gray-400 gap-3">
          <Search className="h-10 w-10" />
          <p className="font-medium">Nenhum político encontrado</p>
          <p className="text-sm">Tente ajustar os filtros.</p>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            {politicos.length} político(s) encontrado(s)
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {politicos.map((politico) => (
              <CardPolitico key={politico.id} politico={politico} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default PoliticosList;
