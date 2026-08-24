// frontend/src/three/TerrainMesh.ts
import * as THREE from 'three';
import { MeshData } from '../types';

export class TerrainMesh {
  public mesh: THREE.Mesh;
  public geometry: THREE.BufferGeometry;
  private basePositions: Float32Array;
  private textureMaterial: THREE.MeshStandardMaterial;
  private wireframeMaterial: THREE.MeshBasicMaterial;
  private colorMapMaterial: THREE.MeshStandardMaterial;
  private activeMode: 'texture' | 'colormap' | 'wireframe' = 'texture';

  constructor(meshData: MeshData, textureUrl?: string) {
    this.geometry = new THREE.BufferGeometry();
    
    const posArr = new Float32Array(meshData.vertices);
    this.basePositions = new Float32Array(posArr);
    
    this.geometry.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
    this.geometry.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(meshData.normals), 3));
    this.geometry.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(meshData.uvs), 2));
    this.geometry.setIndex(meshData.indices);

    // 1. Optical RGB Texture Material
    const textureLoader = new THREE.TextureLoader();
    const texture = textureUrl ? textureLoader.load(textureUrl) : null;
    if (texture) {
      texture.wrapS = THREE.ClampToEdgeWrapping;
      texture.wrapT = THREE.ClampToEdgeWrapping;
      texture.colorSpace = THREE.SRGBColorSpace;
    }

    this.textureMaterial = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.75,
      metalness: 0.1,
      flatShading: false,
      side: THREE.DoubleSide
    });

    // 2. Wireframe Material
    this.wireframeMaterial = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true
    });

    // 3. Colormap Material
    this.colorMapMaterial = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      roughness: 0.6,
      metalness: 0.2,
      wireframe: false,
      side: THREE.DoubleSide
    });

    this.mesh = new THREE.Mesh(this.geometry, this.textureMaterial);
    this.mesh.castShadow = true;
    this.mesh.receiveShadow = true;
  }

  public setHeightExaggeration(factor: number) {
    const posAttr = this.geometry.getAttribute('position') as THREE.BufferAttribute;
    const currentArray = posAttr.array as Float32Array;

    for (let i = 0; i < currentArray.length; i += 3) {
      // Y is height in Three.js coordinates
      currentArray[i + 1] = this.basePositions[i + 1] * factor;
    }

    posAttr.needsUpdate = true;
    this.geometry.computeVertexNormals();
  }

  public setDisplayMode(mode: 'texture' | 'colormap' | 'wireframe') {
    this.activeMode = mode;
    if (mode === 'texture') {
      this.mesh.material = this.textureMaterial;
    } else if (mode === 'wireframe') {
      this.mesh.material = this.wireframeMaterial;
    } else {
      this.mesh.material = this.colorMapMaterial;
    }
  }

  public dispose() {
    this.geometry.dispose();
    this.textureMaterial.dispose();
    this.wireframeMaterial.dispose();
    this.colorMapMaterial.dispose();
  }
}
