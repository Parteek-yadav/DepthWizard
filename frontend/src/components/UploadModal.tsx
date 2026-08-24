// frontend/src/components/UploadModal.tsx
import React, { useState } from 'react';
import { DemoDataset } from '../types';
import { X, UploadCloud, Sparkles, FileImage, Mountain, MapPin, Check } from 'lucide-react';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectDemo: (demo: DemoDataset) => void;
  demoDatasets: DemoDataset[];
  onUploadCustom: (imageFile: File, demFile?: File) => void;
  isLoading: boolean;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onSelectDemo,
  demoDatasets,
  onUploadCustom,
  isLoading
}) => {
  const [activeTab, setActiveTab] = useState<'demo' | 'custom'>('demo');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [demFile, setDemFile] = useState<File | null>(null);

  if (!isOpen) return null;

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile) return;
    onUploadCustom(imageFile, demFile || undefined);
  };

  return (
    <div className=\"fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4\">
      <div className=\"bg-space-900 border border-space-800 rounded-xl max-w-2xl w-full shadow-2xl overflow-hidden flex flex-col text-slate-200 select-none\">
        {/* Header */}
        <div className=\"p-4 border-b border-space-800 flex justify-between items-center bg-space-950/60\">
          <div className=\"flex items-center space-x-2\">
            <div className=\"w-7 h-7 rounded bg-isro-blue/20 text-isro-sky flex items-center justify-center font-bold\">
              DW
            </div>
            <h2 className=\"font-bold text-base text-white\">Load Remote Sensing Dataset</h2>
          </div>
          <button onClick={onClose} className=\"p-1 text-slate-400 hover:text-white rounded\">
            <X className=\"w-5 h-5\" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className=\"flex border-b border-space-800 bg-space-950/40 text-xs font-semibold\">
          <button
            onClick={() => setActiveTab('demo')}
            className={lex-1 py-2.5 flex items-center justify-center space-x-2 border-b-2 transition-all }
          >
            <Sparkles className=\"w-4 h-4\" />
            <span>Preset Datasets (Offline Demo)</span>
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={lex-1 py-2.5 flex items-center justify-center space-x-2 border-b-2 transition-all }
          >
            <UploadCloud className=\"w-4 h-4\" />
            <span>Custom File Ingestion</span>
          </button>
        </div>

        {/* Modal Content */}
        <div className=\"p-6 overflow-y-auto max-h-[70vh]\">
          {activeTab === 'demo' ? (
            <div className=\"space-y-3\">
              <p className=\"text-xs text-slate-400 mb-2\">
                Select a pre-aligned dataset bundled directly in the repository for instant, zero-configuration evaluation:
              </p>
              {demoDatasets.map((ds) => (
                <div
                  key={ds.id}
                  onClick={() => onSelectDemo(ds)}
                  className=\"p-3.5 rounded-lg bg-space-950 hover:bg-space-850 border border-space-800 hover:border-isro-sky/60 cursor-pointer transition-all flex items-start justify-between group shadow-sm\"
                >
                  <div className=\"space-y-1\">
                    <div className=\"flex items-center space-x-2\">
                      <span className=\"font-bold text-xs text-white group-hover:text-isro-sky transition-colors\">
                        {ds.name}
                      </span>
                      {ds.is_georeferenced ? (
                        <span className=\"text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/80 font-mono\">
                          Mode 2: GeoTIFF + {ds.dem_path ? 'SRTM DEM' : 'GCPs'}
                        </span>
                      ) : (
                        <span className=\"text-[10px] px-1.5 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800/80 font-mono\">
                          Mode 1: Non-Georeferenced (Relative rDSM)
                        </span>
                      )}
                    </div>
                    <p className=\"text-[11px] text-slate-400 leading-snug\">{ds.description}</p>
                    {ds.expected_crs && (
                      <div className=\"text-[10px] font-mono text-slate-500\">
                        Spatial Reference: {ds.expected_crs} {ds.elevation_range ? | Elevation:  : ''}
                      </div>
                    )}
                  </div>
                  <button className=\"px-3 py-1 text-xs font-semibold rounded bg-space-800 group-hover:bg-isro-blue text-slate-200 group-hover:text-white transition-all\">
                    Launch
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <form onSubmit={handleCustomSubmit} className=\"space-y-4 text-xs\">
              {/* Primary Optical Raster Upload */}
              <div>
                <label className=\"block font-semibold text-slate-200 mb-1.5\">
                  1. Optical RGB Raster (GeoTIFF, PNG, JPG) <span className=\"text-rose-400\">*</span>
                </label>
                <input
                  type=\"file\"
                  accept=\".tif,.tiff,.png,.jpg,.jpeg\"
                  onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                  className=\"w-full p-2 bg-space-950 border border-space-800 rounded file:mr-3 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:bg-space-800 file:text-slate-200 hover:file:bg-space-700 cursor-pointer\"
                  required
                />
              </div>

              {/* Optional Reference DEM Upload */}
              <div>
                <label className=\"block font-semibold text-slate-200 mb-1.5\">
                  2. Reference DEM GeoTIFF (Optional for Absolute DSM Calibration)
                </label>
                <input
                  type=\"file\"
                  accept=\".tif,.tiff\"
                  onChange={(e) => setDemFile(e.target.files?.[0] || null)}
                  className=\"w-full p-2 bg-space-950 border border-space-800 rounded file:mr-3 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:bg-space-800 file:text-slate-200 hover:file:bg-space-700 cursor-pointer\"
                />
                <p className=\"text-[10px] text-slate-500 mt-1\">
                  If omitted for georeferenced imagery, system computes relative rDSM.
                </p>
              </div>

              <div className=\"pt-3 flex justify-end space-x-2 border-t border-space-800\">
                <button
                  type=\"button\"
                  onClick={onClose}
                  className=\"px-4 py-2 rounded bg-space-800 hover:bg-space-700 text-slate-300 font-medium\"
                >
                  Cancel
                </button>
                <button
                  type=\"submit\"
                  disabled={!imageFile || isLoading}
                  className=\"px-4 py-2 rounded bg-isro-blue hover:bg-sky-600 disabled:opacity-50 text-white font-semibold transition-all\"
                >
                  {isLoading ? 'Processing Pipeline...' : 'Run Pipeline'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
