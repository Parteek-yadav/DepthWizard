// frontend/src/components/ProfileChart.tsx
import React from 'react';
import { TrendingUp } from 'lucide-react';

interface ProfileChartProps {
  histogram?: Array<{ bin_start: number; bin_end: number; count: number }>;
  elevationUnit: string;
}

export const ProfileChart: React.FC<ProfileChartProps> = ({ histogram, elevationUnit }) => {
  if (!histogram || histogram.length === 0) return null;

  const maxCount = Math.max(...histogram.map(h => h.count), 1);

  return (
    <div className=\"p-3 rounded-lg bg-space-900/90 border border-space-800 text-xs shadow-md select-none\">
      <div className=\"flex items-center justify-between mb-2\">
        <div className=\"flex items-center space-x-1.5 text-slate-300 font-semibold text-[11px]\">
          <TrendingUp className=\"w-3.5 h-3.5 text-isro-sky\" />
          <span>Elevation Distribution (Hypsometric Histogram)</span>
        </div>
        <span className=\"text-[10px] text-slate-500 font-mono\">Unit: {elevationUnit}</span>
      </div>

      <div className=\"h-24 flex items-end space-x-1 pt-3 pb-1 px-1 bg-space-950 rounded border border-space-800\">
        {histogram.map((bin, idx) => {
          const heightPercent = (bin.count / maxCount) * 100;
          return (
            <div
              key={idx}
              className=\"flex-1 bg-gradient-to-t from-isro-blue to-isro-sky hover:from-sky-400 hover:to-emerald-300 rounded-t transition-all relative group cursor-pointer\"
              style={{ height: ${Math.max(heightPercent, 4)}% }}
            >
              {/* Tooltip */}
              <div className=\"absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block bg-space-850 border border-space-700 text-[10px] px-1.5 py-0.5 rounded shadow-lg whitespace-nowrap z-30 font-mono text-white\">
                {bin.bin_start} - {bin.bin_end}: {bin.count} px
              </div>
            </div>
          );
        })}
      </div>

      <div className=\"flex justify-between text-[10px] text-slate-400 font-mono mt-1 px-1\">
        <span>{histogram[0].bin_start}</span>
        <span>{histogram[Math.floor(histogram.length / 2)].bin_start}</span>
        <span>{histogram[histogram.length - 1].bin_end}</span>
      </div>
    </div>
  );
};
