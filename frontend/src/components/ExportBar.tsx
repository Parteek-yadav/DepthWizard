// frontend/src/components/ExportBar.tsx
import React from 'react';
import { Download, FileCode, Box, FileSpreadsheet } from 'lucide-react';

interface ExportBarProps {
  urls: {
    texture: string;
    relative_depth: string;
    dsm_preview: string;
    geotiff_dsm?: string | null;
    obj_mesh: string;
    report_json: string;
  };
  isGeoreferenced: boolean;
}

export const ExportBar: React.FC<ExportBarProps> = ({ urls, isGeoreferenced }) => {
  return (
    <div className=\"p-3 rounded-lg bg-space-900 border border-space-800 text-xs flex flex-col space-y-2\">
      <div className=\"text-[11px] font-semibold text-slate-300 flex items-center space-x-1.5\">
        <Download className=\"w-3.5 h-3.5 text-isro-sky\" />
        <span>Geospatial & 3D Exports</span>
      </div>

      <div className=\"grid grid-cols-1 gap-1.5\">
        {isGeoreferenced && urls.geotiff_dsm && (
          <a
            href={urls.geotiff_dsm}
            download=\"dsm_metric.tif\"
            className=\"py-1.5 px-2.5 rounded bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700/60 text-emerald-300 font-medium flex items-center justify-between transition-all\"
          >
            <div className=\"flex items-center space-x-2\">
              <FileSpreadsheet className=\"w-3.5 h-3.5 text-emerald-400\" />
              <span>GeoTIFF Metric DSM</span>
            </div>
            <span className=\"text-[10px] font-mono opacity-80\">.TIF</span>
          </a>
        )}

        <a
          href={urls.obj_mesh}
          download=\"terrain_mesh.obj\"
          className=\"py-1.5 px-2.5 rounded bg-space-800 hover:bg-space-700 border border-space-700 text-slate-200 font-medium flex items-center justify-between transition-all\"
        >
          <div className=\"flex items-center space-x-2\">
            <Box className=\"w-3.5 h-3.5 text-sky-400\" />
            <span>3D Wavefront Mesh</span>
          </div>
          <span className=\"text-[10px] font-mono opacity-80\">.OBJ</span>
        </a>

        <a
          href={urls.report_json}
          download=\"analysis_report.json\"
          className=\"py-1.5 px-2.5 rounded bg-space-800 hover:bg-space-700 border border-space-700 text-slate-200 font-medium flex items-center justify-between transition-all\"
        >
          <div className=\"flex items-center space-x-2\">
            <FileCode className=\"w-3.5 h-3.5 text-amber-400\" />
            <span>Analysis Report Metadata</span>
          </div>
          <span className=\"text-[10px] font-mono opacity-80\">.JSON</span>
        </a>
      </div>
    </div>
  );
};
