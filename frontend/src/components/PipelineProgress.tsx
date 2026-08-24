// frontend/src/components/PipelineProgress.tsx
import React from 'react';
import { CheckCircle2, ArrowRight, Activity, Cpu, Mountain, Eye } from 'lucide-react';

interface PipelineProgressProps {
  currentStage: number; // 0 to 5
}

export const PipelineProgress: React.FC<PipelineProgressProps> = ({ currentStage }) => {
  const stages = [
    { label: 'Optical RGB', icon: Eye },
    { label: 'Depth Backbone', icon: Cpu },
    { label: 'DEM / GCP Calibration', icon: Activity },
    { label: 'DSM Elevation', icon: Mountain },
    { label: '3D Flythrough', icon: CheckCircle2 }
  ];

  return (
    <div className=\"h-10 bg-space-950/80 border-b border-space-800/80 px-6 flex items-center justify-between text-xs shrink-0 overflow-x-auto select-none\">
      <div className=\"flex items-center space-x-3 w-full justify-around\">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isActive = idx === currentStage;
          const isDone = idx < currentStage;

          return (
            <React.Fragment key={stage.label}>
              <div className={lex items-center space-x-1.5 }>
                <Icon className=\"w-3.5 h-3.5\" />
                <span>{stage.label}</span>
              </div>

              {idx < stages.length - 1 && (
                <ArrowRight className={w-3 h-3 } />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
