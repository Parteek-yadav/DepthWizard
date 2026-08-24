// frontend/src/App.tsx
import React, { useEffect, useState, useRef } from 'react';
import { Header } from './components/Header';
import { PipelineProgress } from './components/PipelineProgress';
import { MultiPaneViewer } from './components/MultiPaneViewer';
import { AnalysisPanel } from './components/AnalysisPanel';
import { UploadModal } from './components/UploadModal';
import { SceneManager } from './three/SceneManager';
import { ProcessResponse, DemoDataset } from './types';
import { fetchDemoDatasets, runProcessing, uploadFile } from './services/api';
import { Loader2, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [data, setData] = useState<ProcessResponse | null>(null);
  const [demoDatasets, setDemoDatasets] = useState<DemoDataset[]>([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [pipelineStage, setPipelineStage] = useState<number>(0);
  const sceneManagerRef = useRef<SceneManager | null>(null);

  // Initialize and load default demo
  useEffect(() => {
    async function init() {
      try {
        setIsLoading(true);
        const { datasets } = await fetchDemoDatasets();
        setDemoDatasets(datasets);
        if (datasets.length > 0) {
          await handleLaunchDemo(datasets[0]);
        }
      } catch (err: any) {
        setErrorMsg('Failed to connect to DepthWizard backend. Ensure backend server is active.');
      } finally {
        setIsLoading(false);
      }
    }
    init();
  }, []);

  const handleLaunchDemo = async (ds: DemoDataset) => {
    try {
      setIsLoading(true);
      setErrorMsg(null);
      setPipelineStage(1);

      const result = await runProcessing({
        image_path: ds.image_path,
        dem_path: ds.dem_path,
        gcps: ds.gcps,
        mesh_resolution: 128,
        height_exaggeration: 1.2
      });

      setData(result);
      setPipelineStage(4);
      setIsUploadOpen(false);
    } catch (err: any) {
      setErrorMsg(err.message || 'Pipeline execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomUpload = async (imageFile: File, demFile?: File) => {
    try {
      setIsLoading(true);
      setErrorMsg(null);
      setPipelineStage(0);

      // Upload primary optical image
      const uploadedImg = await uploadFile(imageFile);
      let uploadedDemPath: string | undefined = undefined;

      if (demFile) {
        const uploadedDem = await uploadFile(demFile);
        uploadedDemPath = uploadedDem.file_path;
      }

      setPipelineStage(1);
      const result = await runProcessing({
        image_path: uploadedImg.file_path,
        dem_path: uploadedDemPath,
        mesh_resolution: 128,
        height_exaggeration: 1.2
      });

      setData(result);
      setPipelineStage(4);
      setIsUploadOpen(false);
    } catch (err: any) {
      setErrorMsg(err.message || 'Custom upload processing failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className=\"flex flex-col h-screen w-screen overflow-hidden bg-space-950 text-slate-100 font-sans select-none\">
      {/* Top Header */}
      <Header
        isGeoreferenced={data?.is_georeferenced}
        isAbsolute={data?.is_absolute}
        crs={data?.spatial_metadata.crs}
        onOpenUpload={() => setIsUploadOpen(true)}
        onSelectDemo={() => setIsUploadOpen(true)}
        onReset={() => sceneManagerRef.current?.resetCamera()}
      />

      {/* Pipeline Status Indicator */}
      <PipelineProgress currentStage={pipelineStage} />

      {/* Main Workspace Area */}
      <div className=\"flex-1 flex relative overflow-hidden\">
        {errorMsg && (
          <div className=\"absolute top-4 left-1/2 -translate-x-1/2 z-50 bg-rose-950/90 border border-rose-700 text-rose-200 text-xs px-4 py-2 rounded-lg shadow-xl flex items-center space-x-2 backdrop-blur-md\">
            <AlertCircle className=\"w-4 h-4 text-rose-400\" />
            <span>{errorMsg}</span>
          </div>
        )}

        {isLoading && (
          <div className=\"absolute inset-0 z-40 bg-space-950/70 backdrop-blur-sm flex flex-col items-center justify-center space-y-3\">
            <Loader2 className=\"w-10 h-10 text-isro-sky animate-spin\" />
            <div className=\"text-sm font-semibold text-white tracking-wide\">
              Running Monocular Depth & Elevation Calibration...
            </div>
            <div className=\"text-xs text-slate-400 font-mono\">
              Extracting micro-relief features & generating 3D terrain
            </div>
          </div>
        )}

        {data ? (
          <>
            <MultiPaneViewer data={data} sceneManagerRef={sceneManagerRef} />
            <AnalysisPanel
              stats={data.statistics}
              metadata={data.spatial_metadata}
              calibration={data.calibration_metrics}
              histogram={data.histogram}
              urls={data.urls}
            />
          </>
        ) : (
          <div className=\"flex-1 flex items-center justify-center text-slate-500 text-sm\">
            No raster loaded. Launch a preset dataset to begin.
          </div>
        )}
      </div>

      {/* Upload / Demo Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onSelectDemo={handleLaunchDemo}
        demoDatasets={demoDatasets}
        onUploadCustom={handleCustomUpload}
        isLoading={isLoading}
      />
    </div>
  );
};
export default App;
