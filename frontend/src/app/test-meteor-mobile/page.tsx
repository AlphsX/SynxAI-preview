"use client";

import React, { useState } from "react";
import { IdleMeteorAnimation } from "@/components/ui/idle-meteor-animation";

export default function TestMeteorMobile() {
  const [showMeteors, setShowMeteors] = useState(true);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      <div className="container mx-auto px-4 py-8 relative z-20">
        <h1 className="text-4xl font-bold text-white mb-8 text-center">
          Meteor Animation Test - Mobile Version
        </h1>
        
        <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Test Controls
          </h2>
          <button
            onClick={() => setShowMeteors(!showMeteors)}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            {showMeteors ? "Hide Meteors" : "Show Meteors"}
          </button>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Expected Behavior
          </h2>
          <ul className="text-white/80 space-y-2">
            <li>• Meteors should appear as streaking lights with visible tails</li>
            <li>• Animation should work smoothly on mobile devices</li>
            <li>• Meteors should not appear as just white dots</li>
            <li>• Gradient tails should be visible and not clipped</li>
            <li>• Animation should respect mobile viewport constraints</li>
          </ul>
        </div>
      </div>

      {/* Meteor Animation */}
      {showMeteors && <IdleMeteorAnimation showWelcome={true} />}
    </div>
  );
}