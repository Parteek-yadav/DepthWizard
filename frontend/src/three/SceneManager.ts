// frontend/src/three/SceneManager.ts
import * as THREE from 'three';
import { FlyController } from './FlyController';
import { TerrainMesh } from './TerrainMesh';
import { MeshData } from '../types';

export class SceneManager {
  public scene: THREE.Scene;
  public camera: THREE.PerspectiveCamera;
  public renderer: THREE.WebGLRenderer;
  public flyController: FlyController;
  public terrainMesh: TerrainMesh | null = null;
  private domContainer: HTMLElement;
  private dirLight: THREE.DirectionalLight;
  private hemiLight: THREE.HemisphereLight;
  private isOrbitMode = true;
  private orbitTheta = Math.PI / 4;
  private orbitPhi = Math.PI / 4;
  private orbitRadius = 90;
  private isOrbitDragging = false;
  private prevMouseX = 0;
  private prevMouseY = 0;
  private reqId: number | null = null;
  private lastTime = 0;

  // Raycaster for point queries
  public raycaster: THREE.Raycaster;
  public mouse: THREE.Vector2;

  constructor(container: HTMLElement) {
    this.domContainer = container;
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x060913); // Deep space ISRO dark
    this.scene.fog = new THREE.FogExp2(0x060913, 0.003);

    // Camera
    this.camera = new THREE.PerspectiveCamera(50, width / height, 0.5, 2000);
    this.updateOrbitCamera();

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.domContainer.appendChild(this.renderer.domElement);

    // Lighting
    this.hemiLight = new THREE.HemisphereLight(0xffffff, 0x1e293b, 0.7);
    this.scene.add(this.hemiLight);

    this.dirLight = new THREE.DirectionalLight(0xfffaed, 1.2);
    this.dirLight.position.set(60, 80, 50);
    this.dirLight.castShadow = true;
    this.dirLight.shadow.mapSize.width = 2048;
    this.dirLight.shadow.mapSize.height = 2048;
    this.scene.add(this.dirLight);

    // Add subtle terrain grid floor
    const gridHelper = new THREE.GridHelper(140, 28, 0x0284c7, 0x1e293b);
    gridHelper.position.y = -2;
    this.scene.add(gridHelper);

    // Fly Controller
    this.flyController = new FlyController(this.camera, this.renderer.domElement);

    // Raycaster
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    // Event Listeners
    this.setupOrbitEvents();
    window.addEventListener('resize', this.onResize.bind(this));

    // Start render loop
    this.lastTime = performance.now();
    this.animate(this.lastTime);
  }

  private setupOrbitEvents() {
    const el = this.renderer.domElement;
    el.addEventListener('mousedown', (e) => {
      if (!this.isOrbitMode) return;
      if (e.button === 0) {
        this.isOrbitDragging = true;
        this.prevMouseX = e.clientX;
        this.prevMouseY = e.clientY;
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isOrbitMode || !this.isOrbitDragging) return;
      const dx = e.clientX - this.prevMouseX;
      const dy = e.clientY - this.prevMouseY;
      this.prevMouseX = e.clientX;
      this.prevMouseY = e.clientY;

      this.orbitTheta -= dx * 0.008;
      this.orbitPhi = Math.max(0.1, Math.min(Math.PI / 2 - 0.05, this.orbitPhi + dy * 0.008));
      this.updateOrbitCamera();
    });

    window.addEventListener('mouseup', () => {
      this.isOrbitDragging = false;
    });

    el.addEventListener('wheel', (e) => {
      if (!this.isOrbitMode) return;
      e.preventDefault();
      this.orbitRadius = Math.max(15, Math.min(300, this.orbitRadius + e.deltaY * 0.05));
      this.updateOrbitCamera();
    }, { passive: false });
  }

  private updateOrbitCamera() {
    const x = this.orbitRadius * Math.sin(this.orbitPhi) * Math.sin(this.orbitTheta);
    const y = this.orbitRadius * Math.cos(this.orbitPhi);
    const z = this.orbitRadius * Math.sin(this.orbitPhi) * Math.cos(this.orbitTheta);
    this.camera.position.set(x, y, z);
    this.camera.lookAt(0, 5, 0);
  }

  public setCameraMode(mode: 'orbit' | 'fly') {
    this.isOrbitMode = mode === 'orbit';
    this.flyController.enabled = mode === 'fly';
    if (this.isOrbitMode) {
      this.updateOrbitCamera();
    }
  }

  public setSunAngle(azimuthDeg: number, elevationDeg: number) {
    const radAz = (azimuthDeg * Math.PI) / 180;
    const radEl = (elevationDeg * Math.PI) / 180;
    const r = 100;
    const x = r * Math.cos(radEl) * Math.sin(radAz);
    const y = r * Math.sin(radEl);
    const z = r * Math.cos(radEl) * Math.cos(radAz);
    this.dirLight.position.set(x, y, z);
  }

  public loadTerrain(meshData: MeshData, textureUrl?: string) {
    if (this.terrainMesh) {
      this.scene.remove(this.terrainMesh.mesh);
      this.terrainMesh.dispose();
    }
    this.terrainMesh = new TerrainMesh(meshData, textureUrl);
    this.scene.add(this.terrainMesh.mesh);
  }

  public resetCamera() {
    this.orbitTheta = Math.PI / 4;
    this.orbitPhi = Math.PI / 4;
    this.orbitRadius = 90;
    this.updateOrbitCamera();
  }

  private onResize() {
    const width = this.domContainer.clientWidth;
    const height = this.domContainer.clientHeight;
    if (width === 0 || height === 0) return;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  private animate(now: number) {
    this.reqId = requestAnimationFrame(this.animate.bind(this));
    const delta = (now - this.lastTime) / 1000;
    this.lastTime = now;

    if (!this.isOrbitMode) {
      this.flyController.update(delta);
    }

    this.renderer.render(this.scene, this.camera);
  }

  public dispose() {
    if (this.reqId) cancelAnimationFrame(this.reqId);
    if (this.terrainMesh) this.terrainMesh.dispose();
    this.renderer.dispose();
    window.removeEventListener('resize', this.onResize);
  }
}
