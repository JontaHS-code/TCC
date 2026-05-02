import React, { useState } from "react";
import { Menu, X, Building2 } from "lucide-react";

const Header = ({ activeTab, onTabChange }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { id: "gastos", label: "Gastos Públicos" },
    { id: "politicos", label: "Políticos" },
    { id: "ranking", label: "Ranking IREP" },
    { id: "chat", label: "Chat Cidadão" },
  ];

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-3">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <Building2 className="h-8 w-8 text-emerald-600" />
            <span className="text-xl font-bold text-gray-800">
              Transparência <span className="text-emerald-600">Pública</span>
            </span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange?.(item.id);
                  setMobileOpen(false);
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === item.id
                    ? "bg-emerald-100 text-emerald-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-emerald-600"
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* Mobile toggle */}
          <button
            className="md:hidden text-gray-600 hover:text-emerald-600 transition"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <nav className="md:hidden pb-3 border-t border-gray-100 pt-2 flex flex-col space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange?.(item.id);
                  setMobileOpen(false);
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors text-left ${
                  activeTab === item.id
                    ? "bg-emerald-100 text-emerald-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-emerald-600"
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
