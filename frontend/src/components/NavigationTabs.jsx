import React from "react";
import { Banknote, Users, Trophy, MessageCircle } from "lucide-react";

const NavigationTabs = ({ activeTab, onTabChange }) => {
  const tabs = [
    {
      id: "gastos",
      label: "Gastos Públicos",
      icon: Banknote,
      description: "Executivo Federal",
    },
    {
      id: "politicos",
      label: "Políticos",
      icon: Users,
      description: "Deputados e Senadores",
    },
    {
      id: "ranking",
      label: "Ranking IREP",
      icon: Trophy,
      description: "Índice de Eficiência",
    },
    {
      id: "chat",
      label: "Chat Cidadão",
      icon: MessageCircle,
      description: "Tire suas dúvidas",
    },
  ];

  return (
    <div className="flex flex-wrap gap-1 border-b-2 border-gray-200 pb-1">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              group relative flex items-center gap-2 px-5 py-3 rounded-t-lg font-medium text-sm transition-all duration-200 ease-in-out
              ${
                isActive
                  ? "bg-white text-emerald-700 shadow-sm border border-b-0 border-gray-200 -mb-[2px]"
                  : "text-gray-500 hover:text-emerald-600 hover:bg-emerald-50/50"
              }
            `}
          >
            <Icon
              className={`h-5 w-5 transition-colors ${
                isActive
                  ? "text-emerald-600"
                  : "text-gray-400 group-hover:text-emerald-500"
              }`}
            />
            <div className="text-left">
              <span className="block leading-tight">{tab.label}</span>
              <span
                className={`block text-[10px] leading-tight ${
                  isActive ? "text-emerald-500" : "text-gray-400"
                }`}
              >
                {tab.description}
              </span>
            </div>
            {/* Barra inferior destacada para a aba ativa */}
            {isActive && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 rounded-full" />
            )}
          </button>
        );
      })}
    </div>
  );
};

export default NavigationTabs;
