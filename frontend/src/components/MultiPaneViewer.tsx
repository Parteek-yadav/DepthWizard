// frontend/src/components/MultiPaneViewer.tsx
import React, { useState } from 'react';
import { ProcessResponse } from '../types';
import { Eye, Layers, Mountain, Box, SplitSquareVertical } from 'lucide-react';
import { TerrainCanvas } from './TerrainCanvas';
import { TerrainControls } from './TerrainControls';
import { SceneManager } from '../three/SceneManager';

interface MultiPaneViewerProps {
  data: ProcessResponse;
  sceneManagerRef: React.MutableRefObject<SceneManager | null>;
}

export const MultiPaneViewer: React.FC<MultiPaneViewerProps> = ({ data, sceneManagerRef }) => {
  const [activeTab, setActiveTab] = useState<'3d' | 'rgb' | 'depth' | 'dsm' | 'split'>('3d');
  const [exaggeration, setExaggeration] = useState(1.2);
  const [cameraMode, setCameraMode] = useState<'orbit' | 'fly'>('orbit');
  const [displayMode, setDisplayMode] = useState<'texture' | 'colormap' | 'wireframe'>('texture');
  const [sunElevation, setSunElevation] = useState(45);

  return (
    <div className=\"flex-1 flex flex-col bg-space-950 relative overflow-hidden select-none\">
      {/* Viewer Viewport Subheader */}
      <div className=\"h-10 bg-space-900/80 border-b border-space-800 px-4 flex items-center justify-between text-xs shrink-0 z-20\">
        <div className=\"flex items-center space-x-1\">
          <button
            onClick={() => setActiveTab('3d')}
            className={px-3 py-1 rounded font-medium flex items-center space-x-1.5 transition-all }
          >
            <Box className=\"w-3.5 h-3.5\" />
            <span>Interactive 3D Terrain</span>
          </button>

          <button
            onClick={() => setActiveTab('rgb')}
            className={px-3 py-1 rounded font-medium flex items-center space-x-1.5 transition-all }
          >
            <Eye className=\"w-3.5 h-3.5\" />
            <span>1. Optical RGB</span>
          </button>

          <button
            onClick={() => setActiveTab('depth')}
            className={px-3 py-1 rounded font-medium flex items-center space-x-1.5 transition-all }
          >
            <Layers className=\"w-3.5 h-3.5\" />
            <span>2. Relative Depth Map</span>
          </button>

          <button
            onClick={() => setActiveTab('dsm')}
            className={px-3 py-1 rounded font-medium flex items-center space-x-1.5 transition-all }
          >
            <Mountain className=\"w-3.5 h-3.5\" />
            <span>3. Digital Surface Model</span>
          </button>

          <button
            onClick={() => setActiveTab('split')}
            className={px-3 py-1 rounded font-medium flex items-center space-x-1.5 transition-all }
          >
            <SplitSquareVertical className=\"w-3.5 h-3.5\" />
            <span>4-Pane Comparative</span>
          </button>
        </div>

        <div className=\"flex items-center space-x-2 text-[11px] text-slate-400 font-mono\">
          <span>Resolution: {data.spatial_metadata.width}×{data.spatial_metadata.height}</span>
          <span>|</span>
          <span>Mesh Vertices: {data.mesh.vertex_count.toLocaleString()}</span>
        </div>
      </div>

      {/* Main Viewport Content */}
      <div className=\"flex-1 relative overflow-hidden bg-space-950\">
        {/* 3D WebGL Canvas */}
        <div className={w-full h-full }>
          <TerrainCanvas
            meshData={data.mesh}
            textureUrl={data.urls.texture}
            exaggeration={exaggeration}
            cameraMode={cameraMode}
            displayMode={displayMode}
            sunElevation={sunElevation}
            sceneManagerRef={sceneManagerRef}
          />
          <TerrainControls
            exaggeration={exaggeration}
            onExaggerationChange={setExaggeration}
            cameraMode={cameraMode}
            onCameraModeChange={setCameraMode}
            displayMode={displayMode}
            onDisplayModeChange={setDisplayMode}
            sunElevation={sunElevation}
            onSunElevationChange={setSunElevation}
            onResetCamera={() => sceneManagerRef.current?.resetCamera()}
          />
        </div>

        {/* 2D Optical RGB View */}
        {activeTab === 'rgb' && (
          <div className=\"w-full h-full flex items-center justify-center p-6 bg-black\">
            <img src={data.urls.texture} alt=\"Optical RGB Texture\" className=\"max-w-full max-h-full object-contain rounded shadow-2xl border border-space-800\" />
          </div>
        )}

        {/* 2D Relative Depth Map */}
        {activeTab === 'depth' && (
          <div className=\"w-full h-full flex items-center justify-center p-6 bg-black\">
            <img src={data.urls.relative_depth} alt=\"Relative Depth\" className=\"max-w-full max-h-full object-contain rounded shadow-2xl border border-space-800\" />
          </div>
        )}

        {/* 2D DSM Elevation Map */}
        {activeTab === 'dsm' && (
          <div className=\"w-full h-full flex items-center justify-center p-6 bg-black\">
            <img src={data.urls.dsm_preview} alt=\"Digital Surface Model\" className=\"max-w-full max-h-full object-contain rounded shadow-2xl border border-space-800\" />
          </div>
        )}

        {/* 4-Pane Comparative Split View */}
        {activeTab === 'split' && (
          <div className=\"w-full h-full grid grid-cols-2 grid-rows-2 gap-1 p-1 bg-space-900\">
            <div className=\"relative bg-black flex flex-col rounded border border-space-800 overflow-hidden\">
              <span className=\"absolute top-2 left-2 z-10 text-[10px] font-bold px-2 py-0.5 rounded bg-black/70 text-slate-200 border border-space-700\">
                1. Optical RGB Input
              </span>
              <img src={data.urls.texture} className=\"w-full h-full object-contain\" alt=\"RGB\" />
            </div>

            <div className=\"relative bg-black flex flex-col rounded border border-space-800 overflow-hidden\">
              <span className=\"absolute top-2 left-2 z-10 text-[10px] font-bold px-2 py-0.5 rounded bg-black/70 text-sky-400 border border-space-700\">
                2. Relative Depth Map
              </span>
              <img src={data.urls.relative_depth} className=\"w-full h-full object-contain\" alt=\"Depth\" />
            </div>

            <div className=\"relative bg-black flex flex-col rounded border border-space-800 overflow-hidden\">
              <span className=\"absolute top-2 left-2 z-10 text-[10px] font-bold px-2 py-0.5 rounded bg-black/70 text-emerald-400 border border-space-700\">
                3. Digital Surface Model ({data.elevation_unit})
              </span>
              <img src={data.urls.dsm_preview} className=\"w-full h-full object-contain\" alt=\"DSM\" />
            </div>

            <div className=\"relative bg-black flex flex-col rounded border border-space-800 overflow-hidden\">
              <span className=\"absolute top-2 left-2 z-10 text-[10px] font-bold px-2 py-0.5 rounded bg-black/70 text-amber-400 border border-space-700\">
                4. 3D Terrain View
              </span>
              <TerrainCanvas
                meshData={data.mesh}
                textureUrl={data.urls.texture}
                exaggeration={exaggeration}
                cameraMode=\"orbit\"
                displayMode=\"texture\"
                sunElevation={45}
                sceneManagerRef={sceneManagerRef}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
