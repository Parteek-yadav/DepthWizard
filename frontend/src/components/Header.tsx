// frontend/src/components/Header.tsx
import React from 'react';
import { Layers, Globe, Compass, RefreshCw, UploadCloud, Play, Sparkles } from 'lucide-react';

interface HeaderProps {
  isGeoreferenced?: boolean;
  isAbsolute?: boolean;
  crs?: string | null;
  onOpenUpload: () => void;
  onSelectDemo: () => void;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isGeoreferenced,
  isAbsolute,
  crs,
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

      {/* Center: Active Pipeline Mode Badge */}
      <div className=\"flex items-center space-x-2\">
        {isGeoreferenced !== undefined && (
          <div className={px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5 border }>
            <Globe className=\"w-3.5 h-3.5\" />
            <span>
              {isAbsolute 
                ? Mode 2: Georeferenced (Absolute DSM in Meters) 
                : Mode 1: Non-Georeferenced (Relative rDSM)}
            </span>
            {crs && (
              <span className=\"text-[10px] opacity-75 font-mono px-1.5 py-0.2 bg-black/40 rounded\">
                {crs}
              </span>
            )}
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
