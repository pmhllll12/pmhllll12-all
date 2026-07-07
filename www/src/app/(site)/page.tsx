"use client";

import { useState } from "react";
import Hero from "@/components/Hero";
import HeroPredictionPanel from "@/components/HeroPredictionPanel";
import WorldCupGroupsSection from "@/components/WorldCupGroupsSection";
import WorldCupTeamsSection from "@/components/WorldCupTeamsSection";
import WorldCupStatsSection from "@/components/WorldCupStatsSection";
import GeminiChat from "@/components/GeminiChat";
import "./home.css";

export default function Home() {
  const [geminiPreset, setGeminiPreset] = useState<{
    key: number;
    text: string;
  } | null>(null);

  return (
    <div className="relative flex-1 w-full overflow-x-hidden overflow-y-visible bg-bg-0">
      <div className="home-bg" aria-hidden />
      <main className="home-grid relative z-[1] grid w-full max-w-[1400px] mx-auto items-start box-border gap-3 1200:gap-[24px_32px] pt-2 1200:pt-0 pb-7 1200:pb-8 px-[clamp(12px,4vw,20px)] 1200:px-[clamp(12px,4vw,24px)]">
        <div className="home-grid-hero min-w-0 w-full">
          <Hero
            showPrediction={false}
            onGeminiPreset={(text) =>
              setGeminiPreset({ key: Date.now(), text })
            }
          />
        </div>
        <div className="home-grid-chat relative z-[2] flex items-start justify-center w-full min-w-0 box-border 1200:pt-12">
          <GeminiChat
            preset={geminiPreset}
            onPresetConsumed={() => setGeminiPreset(null)}
          />
        </div>
        <div className="home-grid-prediction min-w-0 w-full max-w-full">
          <HeroPredictionPanel
            onAiPreset={(text) => setGeminiPreset({ key: Date.now(), text })}
          />
        </div>
        <div className="home-grid-sections min-w-0 w-full flex flex-col gap-0">
          <WorldCupGroupsSection />
          <WorldCupTeamsSection />
          <WorldCupStatsSection />
        </div>
      </main>
    </div>
  );
}
