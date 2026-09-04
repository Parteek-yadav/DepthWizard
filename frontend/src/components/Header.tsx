// frontend/src/components/Header.tsx
import React from 'react';
import { Layers, Globe, Compass, RefreshCw, UploadCloud, Play, Sparkles, Cpu, AlertTriangle } from 'lucide-react';

interface ModelMetadata {
  model_name: string;
  backbone: string;
  is_fallback: boolean;
  device: string;
}

interface HeaderProps {
  isGeoreferenced?: boolean;
  isAbsolute?: boolean;
  crs?: string | null;
  modelMetadata?: ModelMetadata | null;
  onOpenUpload: () => void;
  onSelectDemo: () => void;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isGeoreferenced,
  isAbsolute,
  crs,
  modelMetadata,
  onOpenUpload,
  onSelectDemo,
  onReset,
}) => {
  return (
    <header className=\"h-14 border-b border-space-800 bg-space-900/90 backdrop-blur-md px-4 flex items-center justify-between z-30 shrink-0\">
      {/* Left: Brand & Problem Badge */}
      <div className=\"flex items-center space-x-3\">
        <div className=\"w-9 h-9 rounded-lg bg-gradient-to-tr from-isro-orange to-isro-sky flex items-center justify-center shadow-lg shadow-isro-blue/20\">
          <Layers className=\"w-5 h-5 text-white\" />
        </div>
        <div>
          <div className=\"flex items-center space-x-2\">
            <span className=\"font-bold text-base tracking-tight text-white\">DepthWizard</span>
            <span className=\"text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-orange-950/80 text-orange-400 border border-orange-800/60\">
              ISRO SIH26175
            </span>
          </div>
          <p className=\"text-[11px] text-slate-400 font-mono\">Single-View Height Estimation & 3D Flythrough</p>
        </div>
      </div>

      {/* Center: Active Pipeline Mode Badge + Model Status Badge */}
      <div className=\"flex items-center space-x-2\">
        {isGeoreferenced !== undefined && (
          <div className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5 border `}>
            <Globe className=\"w-3.5 h-3.5\" />
            <span>
              {isAbsolute 
                ? `Mode 2: Georeferenced (Absolute DSM in Meters)` 
                : `Mode 1: Non-Georeferenced (Relative rDSM)`}
            </span>
            {crs && (
              <span className=\"text-[10px] opacity-75 font-mono px-1.5 py-0.2 bg-black/40 rounded\">
                {crs}
              </span>
            )}
          </div>
        )}

        {/* Depth Model Status Badge */}
        {modelMetadata && (
          <div
            id=\"depth-model-badge\"
            className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5 border transition-colors ${
              modelMetadata.is_fallback
                ? 'bg-amber-950/60 text-amber-300 border-amber-700/60'
                : 'bg-emerald-950/60 text-emerald-300 border-emerald-700/60'
            }`}
          >
            {modelMetadata.is_fallback ? (
              <AlertTriangle className=\"w-3.5 h-3.5\" />
            ) : (
              <Cpu className=\"w-3.5 h-3.5\" />
            )}
            <span>
              {modelMetadata.is_fallback
                ? 'Structural Fallback (no ONNX weights)'
                : 'Depth Anything V2 (ONNX)'}
            </span>
          </div>
        )}
      </div>

      {/* Right: Quick Action Buttons */}
      <div className=\"flex items-center space-x-2\">
        <button
          onClick={onSelectDemo}
          className=\"px-3 py-1.5 rounded-md text-xs font-medium bg-space-800 hover:bg-space-700 text-slate-200 border border-space-700 hover:border-slate-500 transition-all flex items-center space-x-1.5\"
        >
          <Sparkles className=\"w-3.5 h-3.5 text-isro-sky\" />
          <span>Demo Datasets</span>
        </button>

        <button
          onClick={onOpenUpload}
          className=\"px-3 py-1.5 rounded-md text-xs font-semibold bg-isro-blue hover:bg-sky-600 text-white shadow-md transition-all flex items-center space-x-1.5\"
        >
          <UploadCloud className=\"w-3.5 h-3.5\" />
          <span>Upload Optical Raster</span>
        </button>

        <button
          onClick={onReset}
          title=\"Reset Scene\"
          className=\"p-2 rounded-md bg-space-800 hover:bg-space-700 text-slate-400 hover:text-white border border-space-700 transition-all\"
        >
          <RefreshCw className=\"w-3.5 h-3.5\" />
        </button>
      </div>
    </header>
  );
};
