// frontend/src/components/CalibrationReport.tsx
import React from 'react';
import { CalibrationMetrics } from '../types';
import { CheckCircle, Activity, Crosshair, Scale } from 'lucide-react';

interface CalibrationReportProps {
  metrics?: CalibrationMetrics | null;
  isGeoreferenced: boolean;
}

export const CalibrationReport: React.FC<CalibrationReportProps> = ({ metrics, isGeoreferenced }) => {
  if (!isGeoreferenced || !metrics) {
    return (
      <div className=\"p-4 rounded-lg bg-space-900 border border-space-800 text-xs\">
        <div className=\"flex items-center space-x-2 text-sky-400 font-semibold mb-2\">
          <Activity className=\"w-4 h-4\" />
          <span>Elevation Calibration Status</span>
        </div>
        <p className=\"text-slate-400 leading-relaxed text-[11px]\">
          Non-georeferenced optical image. Elevation is computed as <strong>Relative Depth (rDSM)</strong> normalized in [0.0, 1.0]. No metric physical scale is asserted.
        </p>
      </div>
    );
  }

  return (
    <div className=\"p-4 rounded-lg bg-space-900/90 border border-emerald-800/40 text-xs shadow-lg\">
      <div className=\"flex items-center justify-between mb-3 border-b border-space-800 pb-2\">
        <div className=\"flex items-center space-x-2 text-emerald-400 font-semibold\">
          <CheckCircle className=\"w-4 h-4\" />
          <span>Calibrated Absolute DSM (Meters)</span>
        </div>
        <span className=\"text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-700 text-emerald-300\">
          Huber Robust M-Estimation
        </span>
      </div>

      <div className=\"grid grid-cols-2 gap-2 mb-3\">
        <div className=\"p-2 rounded bg-space-950 border border-space-800\">
          <div className=\"text-[10px] text-slate-400\">Mean Abs Error (MAE)</div>
          <div className=\"text-sm font-bold font-mono text-emerald-300\">{metrics.mae_meters} m</div>
        </div>

        <div className=\"p-2 rounded bg-space-950 border border-space-800\">
          <div className=\"text-[10px] text-slate-400\">RMSE</div>
          <div className=\"text-sm font-bold font-mono text-emerald-300\">{metrics.rmse_meters} m</div>
        </div>

        <div className=\"p-2 rounded bg-space-950 border border-space-800\">
          <div className=\"text-[10px] text-slate-400\">Pearson Corr (r)</div>
          <div className=\"text-sm font-bold font-mono text-isro-sky\">{metrics.pearson_r}</div>
        </div>

        <div className=\"p-2 rounded bg-space-950 border border-space-800\">
          <div className=\"text-[10px] text-slate-400\">R² Fit Score</div>
          <div className=\"text-sm font-bold font-mono text-isro-sky\">{metrics.r2_score}</div>
        </div>
      </div>

      <div className=\"space-y-1 text-[11px] font-mono text-slate-400 border-t border-space-800 pt-2\">
        <div className=\"flex justify-between\">
          <span>Fitted Scale (s):</span>
          <span className=\"text-slate-200 font-bold\">{metrics.scale.toFixed(3)}</span>
        </div>
        <div className=\"flex justify-between\">
          <span>Fitted Offset (t):</span>
          <span className=\"text-slate-200 font-bold\">{metrics.offset.toFixed(2)} m</span>
        </div>
        {metrics.sample_count && (
          <div className=\"flex justify-between\">
            <span>Sampled Reference Pixels:</span>
            <span className=\"text-slate-200\">{metrics.sample_count.toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  );
};
