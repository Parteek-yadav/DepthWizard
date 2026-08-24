// frontend/src/components/TerrainControls.tsx
import React from 'react';
import { Sliders, Sun, Move3d, Compass, Maximize2 } from 'lucide-react';

interface TerrainControlsProps {
  exaggeration: number;
  onExaggerationChange: (val: number) => void;
  cameraMode: 'orbit' | 'fly';
  onCameraModeChange: (mode: 'orbit' | 'fly') => void;
  displayMode: 'texture' | 'colormap' | 'wireframe';
  onDisplayModeChange: (mode: 'texture' | 'colormap' | 'wireframe') => void;
  sunElevation: number;
  onSunElevationChange: (val: number) => void;
  onResetCamera: () => void;
}

export const TerrainControls: React.FC<TerrainControlsProps> = ({
  exaggeration,
  onExaggerationChange,
  cameraMode,
  onCameraModeChange,
  displayMode,
  onDisplayModeChange,
  sunElevation,
  onSunElevationChange,
  onResetCamera
}) => {
  return (
    <div className=\"absolute top-3 left-3 z-10 bg-space-900/90 backdrop-blur-md border border-space-800 rounded-lg p-3 shadow-2xl flex flex-col space-y-3 text-xs w-64 select-none\">
      {/* Navigation Camera Mode */}
      <div>
        <label className=\"text-[11px] font-semibold text-slate-300 flex items-center space-x-1.5 mb-1.5\">
          <Move3d className=\"w-3.5 h-3.5 text-isro-sky\" />
          <span>Camera Navigation</span>
        </label>
        <div className=\"grid grid-cols-2 gap-1.5 bg-space-950 p-1 rounded-md border border-space-800\">
          <button
            onClick={() => onCameraModeChange('orbit')}
            className={py-1 rounded font-medium transition-all }
          >
            Orbit / Pan
          </button>
          <button
            onClick={() => onCameraModeChange('fly')}
            className={py-1 rounded font-medium transition-all }
          >
            Drone Fly (WASD)
          </button>
        </div>
      </div>

      {/* Surface Shading & Material */}
      <div>
        <label className=\"text-[11px] font-semibold text-slate-300 flex items-center space-x-1.5 mb-1.5\">
          <Sliders className=\"w-3.5 h-3.5 text-isro-sky\" />
          <span>Surface Material</span>
        </label>
        <div className=\"grid grid-cols-3 gap-1 bg-space-950 p-1 rounded-md border border-space-800\">
          <button
            onClick={() => onDisplayModeChange('texture')}
            className={py-1 rounded text-[11px] font-medium }
          >
            RGB Optical
          </button>
          <button
            onClick={() => onDisplayModeChange('colormap')}
            className={py-1 rounded text-[11px] font-medium }
          >
            Colormap
          </button>
          <button
            onClick={() => onDisplayModeChange('wireframe')}
            className={py-1 rounded text-[11px] font-medium }
          >
            Wireframe
          </button>
        </div>
      </div>

      {/* Height Exaggeration Slider */}
      <div>
        <div className=\"flex justify-between items-center mb-1 text-[11px]\">
          <span className=\"text-slate-300 font-medium\">Vertical Exaggeration</span>
          <span className=\"font-mono font-bold text-isro-sky\">{exaggeration.toFixed(1)}x</span>
        </div>
        <input
          type=\"range\"
          min=\"0.2\"
          max=\"4.0\"
          step=\"0.1\"
          value={exaggeration}
          onChange={(e) => onExaggerationChange(parseFloat(e.target.value))}
          className=\"w-full accent-isro-sky cursor-pointer h-1.5 bg-space-800 rounded-lg\"
        />
      </div>

      {/* Solar Elevation Slider */}
      <div>
        <div className=\"flex justify-between items-center mb-1 text-[11px]\">
          <span className=\"text-slate-300 font-medium flex items-center space-x-1\">
            <Sun className=\"w-3 h-3 text-amber-400\" />
            <span>Sun Altitude</span>
          </span>
          <span className=\"font-mono text-slate-400\">{sunElevation}°</span>
        </div>
        <input
          type=\"range\"
          min=\"10\"
          max=\"85\"
          step=\"5\"
          value={sunElevation}
          onChange={(e) => onSunElevationChange(parseInt(e.target.value))}
          className=\"w-full accent-amber-400 cursor-pointer h-1.5 bg-space-800 rounded-lg\"
        />
      </div>

      {/* Reset Camera Button */}
      <button
        onClick={onResetCamera}
        className=\"w-full py-1.5 rounded bg-space-800 hover:bg-space-700 text-slate-200 border border-space-700 font-medium text-[11px] transition-all flex items-center justify-center space-x-1.5\"
      >
        <Compass className=\"w-3.5 h-3.5 text-slate-400\" />
        <span>Fit & Reset Camera</span>
      </button>
    </div>
  );
};
