// frontend/src/components/TerrainCanvas.tsx
import React, { useEffect, useRef } from 'react';
import { SceneManager } from '../three/SceneManager';
import { MeshData } from '../types';

interface TerrainCanvasProps {
  meshData?: MeshData | null;
  textureUrl?: string;
  exaggeration: number;
  cameraMode: 'orbit' | 'fly';
  displayMode: 'texture' | 'colormap' | 'wireframe';
  sunElevation: number;
  onPointSelected?: (point: { x: number; y: number; elevation: number }) => void;
  sceneManagerRef: React.MutableRefObject<SceneManager | null>;
}

export const TerrainCanvas: React.FC<TerrainCanvasProps> = ({
  meshData,
  textureUrl,
  exaggeration,
  cameraMode,
  displayMode,
  sunElevation,
  onPointSelected,
  sceneManagerRef
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const sm = new SceneManager(containerRef.current);
    sceneManagerRef.current = sm;

    return () => {
      sm.dispose();
      sceneManagerRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!sceneManagerRef.current || !meshData) return;
    sceneManagerRef.current.loadTerrain(meshData, textureUrl);
  }, [meshData, textureUrl]);

  useEffect(() => {
    if (!sceneManagerRef.current || !sceneManagerRef.current.terrainMesh) return;
    sceneManagerRef.current.terrainMesh.setHeightExaggeration(exaggeration);
  }, [exaggeration]);

  useEffect(() => {
    if (!sceneManagerRef.current) return;
    sceneManagerRef.current.setCameraMode(cameraMode);
  }, [cameraMode]);

  useEffect(() => {
    if (!sceneManagerRef.current || !sceneManagerRef.current.terrainMesh) return;
    sceneManagerRef.current.terrainMesh.setDisplayMode(displayMode);
  }, [displayMode]);

  useEffect(() => {
    if (!sceneManagerRef.current) return;
    sceneManagerRef.current.setSunAngle(45, sunElevation);
  }, [sunElevation]);

  return (
    <div 
      ref={containerRef} 
      className=\"w-full h-full relative cursor-crosshair overflow-hidden\"
    />
  );
};
