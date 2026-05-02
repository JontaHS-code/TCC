import React, { useState } from "react";
import Header from "../components/Header";
import Hero from "../components/Hero";
import NavigationTabs from "../components/NavigationTabs";
import GastosResumo from "../components/GastosResumo";
import PoliticosList from "../components/PoliticosList";
import RankingIREP from "../components/RankingIREP";
import ChatInterface from "../components/ChatInterface";

const Home = () => {
  const [activeTab, setActiveTab] = useState("gastos");

  const renderContent = () => {
    switch (activeTab) {
      case "gastos":
        return <GastosResumo />;
      case "politicos":
        return <PoliticosList />;
      case "ranking":
        return <RankingIREP />;
      case "chat":
        return <ChatInterface />;
      default:
        return <GastosResumo />;
    }
  };

  return (
    <div className="min-h-screen">
      <Header />
      <Hero />
      <div className="container mx-auto px-4 py-8">
        <NavigationTabs activeTab={activeTab} onTabChange={setActiveTab} />
        <div className="mt-6">{renderContent()}</div>
      </div>
    </div>
  );
};

export default Home;
