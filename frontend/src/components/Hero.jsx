import React from "react";
import { Shield, Users, TrendingUp } from "lucide-react";
import logoImg from "../assets/logo.png";

const Hero = () => {
  return (
    <section className="bg-gradient-to-br from-emerald-50 to-teal-50 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-4xl mx-auto">
          {/* Logo */}
          <img
            src={logoImg}
            alt="Brasil Transparente"
            className="h-24 md:h-32 mx-auto mb-8 object-contain"
          />

          {/* Box prata com efeito glass */}
          <div className="relative max-w-md mx-auto mb-8">
            {/* Sombra prateada suave */}
            <div className="absolute inset-0 bg-gradient-to-r from-gray-300/30 to-slate-300/30 rounded-2xl blur-xl" />
            {/* Cartão vidro prateado */}
            <div className="relative bg-white/60 backdrop-blur-md border border-gray-200/70 rounded-2xl px-6 py-4 shadow-sm">
              <p className="text-transparent bg-clip-text bg-gradient-to-r from-gray-500 to-slate-500 font-semibold text-lg md:text-xl tracking-tight">
                Dados públicos, decisões conscientes.
              </p>
            </div>
          </div>

          {/* Cards */}
          <div className="grid md:grid-cols-3 gap-6 text-left mt-10">
            <div className="flex items-start space-x-3">
              <Shield className="h-6 w-6 text-emerald-600 mt-1" />
              <div>
                <h3 className="font-semibold">Transparência Total</h3>
                <p className="text-sm text-gray-500">
                  Dados oficiais do governo em um só lugar
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Users className="h-6 w-6 text-teal-600 mt-1" />
              <div>
                <h3 className="font-semibold">Controle Social</h3>
                <p className="text-sm text-gray-500">
                  Ferramentas para fiscalizar seus representantes
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <TrendingUp className="h-6 w-6 text-emerald-700 mt-1" />
              <div>
                <h3 className="font-semibold">Índice IREP</h3>
                <p className="text-sm text-gray-500">
                  Compare a eficiência política de cada candidato
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
