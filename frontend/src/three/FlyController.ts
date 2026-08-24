// frontend/src/three/FlyController.ts
import * as THREE from 'three';

export class FlyController {
  private camera: THREE.Camera;
  private domElement: HTMLElement;
  private moveForward = false;
  private moveBackward = false;
  private moveLeft = false;
  private moveRight = false;
  private moveUp = false;
  private moveDown = false;
  private isMouseDown = false;
  private prevMouseX = 0;
  private prevMouseY = 0;
  private speed = 25.0; // units per second
  private euler = new THREE.Euler(0, 0, 0, 'YXZ');
  public enabled = false;

  constructor(camera: THREE.Camera, domElement: HTMLElement) {
    this.camera = camera;
    this.domElement = domElement;
    this.euler.setFromQuaternion(this.camera.quaternion);

    window.addEventListener('keydown', this.onKeyDown.bind(this));
    window.addEventListener('keyup', this.onKeyUp.bind(this));
    this.domElement.addEventListener('mousedown', this.onMouseDown.bind(this));
    window.addEventListener('mousemove', this.onMouseMove.bind(this));
    window.addEventListener('mouseup', this.onMouseUp.bind(this));
  }

  private onKeyDown(e: KeyboardEvent) {
    if (!this.enabled) return;
    switch (e.code) {
      case 'KeyW': case 'ArrowUp': this.moveForward = true; break;
      case 'KeyS': case 'ArrowDown': this.moveBackward = true; break;
      case 'KeyA': case 'ArrowLeft': this.moveLeft = true; break;
      case 'KeyD': case 'ArrowRight': this.moveRight = true; break;
      case 'Space': this.moveUp = true; break;
      case 'ShiftLeft': case 'KeyC': this.moveDown = true; break;
    }
  }

  private onKeyUp(e: KeyboardEvent) {
    if (!this.enabled) return;
    switch (e.code) {
      case 'KeyW': case 'ArrowUp': this.moveForward = false; break;
      case 'KeyS': case 'ArrowDown': this.moveBackward = false; break;
      case 'KeyA': case 'ArrowLeft': this.moveLeft = false; break;
      case 'KeyD': case 'ArrowRight': this.moveRight = false; break;
      case 'Space': this.moveUp = false; break;
      case 'ShiftLeft': case 'KeyC': this.moveDown = false; break;
    }
  }

  private onMouseDown(e: MouseEvent) {
    if (!this.enabled) return;
    if (e.button === 0 || e.button === 2) {
      this.isMouseDown = true;
      this.prevMouseX = e.clientX;
      this.prevMouseY = e.clientY;
    }
  }

  private onMouseMove(e: MouseEvent) {
    if (!this.enabled || !this.isMouseDown) return;
    const deltaX = e.clientX - this.prevMouseX;
    const deltaY = e.clientY - this.prevMouseY;
    this.prevMouseX = e.clientX;
    this.prevMouseY = e.clientY;

    this.euler.setFromQuaternion(this.camera.quaternion);
    this.euler.y -= deltaX * 0.003;
    this.euler.x -= deltaY * 0.003;
    this.euler.x = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, this.euler.x));
    this.camera.quaternion.setFromEuler(this.euler);
  }

  private onMouseUp() {
    this.isMouseDown = false;
  }

  public update(deltaSeconds: number) {
    if (!this.enabled) return;
    const actualSpeed = this.speed * deltaSeconds;
    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(this.camera.quaternion);
    const right = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion);

    if (this.moveForward) this.camera.position.addScaledVector(forward, actualSpeed);
    if (this.moveBackward) this.camera.position.addScaledVector(forward, -actualSpeed);
    if (this.moveRight) this.camera.position.addScaledVector(right, actualSpeed);
    if (this.moveLeft) this.camera.position.addScaledVector(right, -actualSpeed);
    if (this.moveUp) this.camera.position.y += actualSpeed;
    if (this.moveDown) this.camera.position.y -= actualSpeed;
  }

  public setSpeed(newSpeed: number) {
    this.speed = newSpeed;
  }
}
