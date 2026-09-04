// frontend/src/components/AnalysisPanel.tsx
import React, { useState } from 'react';
import { SummaryStats, CalibrationMetrics, SpatialMetadata } from '../types';
import { Ruler, Mountain, Target, BarChart2, Info, Compass, Maximize } from 'lucide-react';
import { CalibrationReport } from './CalibrationReport';
import { ProfileChart } from './ProfileChart';
import { ExportBar } from './ExportBar';

interface AnalysisPanelProps {
  stats: SummaryStats;
  metadata: SpatialMetadata;
  calibration?: CalibrationMetrics | null;
  histogram: Array<{ bin_start: number; bin_end: number; count: number }>;
  urls: any;
  modelMetadata?: { model_name: string; backbone: string; is_fallback: boolean; device: string } | null;
  onRunMeasurement?: (dz: number, slope: number) => void;
}

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  stats,
  metadata,
  calibration,
  histogram,
  urls,
  modelMetadata
}) => {
  const [pointAz, setPointAz] = useState<number>(stats.min_elevation + (stats.max_elevation - stats.min_elevation) * 0.25);
  const [pointBz, setPointBz] = useState<number>(stats.max_elevation * 0.85);

  const dz = Math.abs(pointBz - pointAz);
  const estimatedHorizDist = 150.0; // meters approximate
  const slopeAngle = Math.atan2(dz, estimatedHorizDist) * (180 / Math.PI);
  const slopePercent = (dz / estimatedHorizDist) * 100;

  return (
    <aside className=\"w-84 bg-space-950/95 border-l border-space-800 p-4 flex flex-col space-y-4 overflow-y-auto z-20 shrink-0 select-none text-slate-200\">
      {/* Top Header */}
      <div className=\"flex items-center justify-between border-b border-space-800 pb-2\">
        <div className=\"flex items-center space-x-2 font-bold text-sm text-white\">
          <BarChart2 className=\"w-4 h-4 text-isro-sky\" />
          <span>Spatial Terrain Analytics</span>
        </div>
      </div>

      {/* Elevation Statistics Card */}
      <div className=\"p-3 rounded-lg bg-space-900 border border-space-800 text-xs shadow\">
        <div className=\"flex items-center space-x-1.5 text-slate-300 font-semibold mb-2.5\">
          <Mountain className=\"w-3.5 h-3.5 text-emerald-400\" />
          <span>Elevation Bounds & Metrics</span>
        </div>
        <div className=\"grid grid-cols-3 gap-2 text-center\">
          <div className=\"p-1.5 rounded bg-space-950 border border-space-800\">
            <div className=\"text-[10px] text-slate-400\">Min</div>
            <div className=\"font-mono font-bold text-xs text-sky-400\">{stats.min_elevation}</div>
            <div className=\"text-[9px] text-slate-500 font-mono\">{stats.elevation_unit === 'meters' ? 'm' : 'rel'}</div>
          </div>
          <div className=\"p-1.5 rounded bg-space-950 border border-space-800\">
            <div className=\"text-[10px] text-slate-400\">Mean</div>
            <div className=\"font-mono font-bold text-xs text-slate-200\">{stats.mean_elevation}</div>
            <div className=\"text-[9px] text-slate-500 font-mono\">{stats.elevation_unit === 'meters' ? 'm' : 'rel'}</div>
          </div>
          <div className=\"p-1.5 rounded bg-space-950 border border-space-800\">
            <div className=\"text-[10px] text-slate-400\">Max</div>
            <div className=\"font-mono font-bold text-xs text-emerald-400\">{stats.max_elevation}</div>
            <div className=\"text-[9px] text-slate-500 font-mono\">{stats.elevation_unit === 'meters' ? 'm' : 'rel'}</div>
          </div>
        </div>
      </div>

      {/* Calibration Report */}
      <CalibrationReport metrics={calibration} isGeoreferenced={stats.is_georeferenced} />

      {/* Interactive 2-Point Structural Height & Slope Measurement Tool */}
      <div className=\"p-3 rounded-lg bg-space-900 border border-space-800 text-xs shadow space-y-2.5\">
        <div className=\"flex items-center justify-between\">
          <div className=\"flex items-center space-x-1.5 text-slate-300 font-semibold\">
            <Ruler className=\"w-3.5 h-3.5 text-amber-400\" />
            <span>Structural Height & Slope Tool</span>
          </div>
          <span className=\"text-[10px] text-amber-400/80 font-mono\">Interactive</span>
        </div>

        <div className=\"space-y-1.5\">
          <div className=\"flex items-center justify-between text-[11px]\">
            <span className=\"text-slate-400\">Point A Elevation:</span>
            <span className=\"font-mono text-slate-200\">{pointAz.toFixed(1)} {stats.elevation_unit === 'meters' ? 'm' : 'rel'}</span>
          </div>
          <input
            type=\"range\"
            min={stats.min_elevation}
            max={stats.max_elevation}
            step=\"1\"
            value={pointAz}
            onChange={(e) => setPointAz(parseFloat(e.target.value))}
            className=\"w-full accent-isro-sky cursor-pointer h-1 bg-space-800 rounded\"
          />

          <div className=\"flex items-center justify-between text-[11px]\">
            <span className=\"text-slate-400\">Point B Elevation:</span>
            <span className=\"font-mono text-slate-200\">{pointBz.toFixed(1)} {stats.elevation_unit === 'meters' ? 'm' : 'rel'}</span>
          </div>
          <input
            type=\"range\"
            min={stats.min_elevation}
            max={stats.max_elevation}
            step=\"1\"
            value={pointBz}
            onChange={(e) => setPointBz(parseFloat(e.target.value))}
            className=\"w-full accent-emerald-400 cursor-pointer h-1 bg-space-800 rounded\"
          />
        </div>

        <div className=\"grid grid-cols-2 gap-2 pt-1 border-t border-space-800\">
          <div className=\"p-2 rounded bg-space-950 border border-space-800\">
            <div className=\"text-[10px] text-slate-400\">Height Diff (ΔZ)</div>
            <div className=\"font-mono font-bold text-sm text-amber-400\">
              {dz.toFixed(2)} {stats.elevation_unit === 'meters' ? 'm' : 'rel'}
            </div>
          </div>
          <div className=\"p-2 rounded bg-space-950 border border-space-800\">
            <div className=\"text-[10px] text-slate-400\">Slope Angle (θ)</div>
            <div className=\"font-mono font-bold text-sm text-sky-400\">
              {slopeAngle.toFixed(1)}° ({slopePercent.toFixed(0)}%)
            </div>
          </div>
        </div>
      </div>

      {/* Hypsometric Elevation Profile */}
      <ProfileChart histogram={histogram} elevationUnit={stats.elevation_unit} />

      {/* Spatial Metadata Card */}
      <div className=\"p-3 rounded-lg bg-space-900 border border-space-800 text-xs font-mono text-slate-400 space-y-1\">
        <div className=\"text-[11px] font-sans font-semibold text-slate-300 flex items-center space-x-1.5 mb-1.5\">
          <Info className=\"w-3.5 h-3.5 text-slate-400\" />
          <span>Raster Specifications</span>
        </div>
        <div className=\"flex justify-between\">
          <span>Dimensions:</span>
          <span className=\"text-slate-200\">{stats.dimensions.width} &times; {stats.dimensions.height} px</span>
        </div>
        <div className="flex justify-between">
          <span>CRS:</span>
          <span className="text-slate-200">{metadata.crs || 'Non-Georeferenced'}</span>
        </div>
        {metadata.gsd && (
          <div className="flex justify-between">
            <span>GSD:</span>
            <span className="text-slate-200">{metadata.gsd.toFixed(2)} m/px</span>
          </div>
        )}
        <div className="flex justify-between">
          <span>Depth Backend:</span>
          <span className={modelMetadata?.is_fallback ? 'text-amber-400' : 'text-emerald-400'}>
            {modelMetadata
              ? (modelMetadata.is_fallback ? 'Structural Fallback' : 'Depth Anything V2 (ONNX)')
              : 'Unknown'}
          </span>
        </div>
      </div>

      {/* Export Bar */}
      <ExportBar urls={urls} isGeoreferenced={stats.is_georeferenced} />
    </aside>
  );
};
