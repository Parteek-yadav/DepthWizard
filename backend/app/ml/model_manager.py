# backend/app/ml/model_manager.py
import logging
from typing import Optional
from backend.app.ml.base_model import BaseDepthModel
from backend.app.ml.depth_anything_v2 import DepthAnythingV2Model

logger = logging.getLogger(__name__)

class ModelManager:
    _instance: Optional['ModelManager'] = None
    _model: Optional[BaseDepthModel] = None

    @classmethod
    def get_instance(cls) -> 'ModelManager':
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

    def get_depth_model(self, model_type: str = "depth_anything_v2", device: str = "auto") -> BaseDepthModel:
        if self._model is None:
            if device == "auto":
                try:
                    import torch
                    resolved_device = "cuda" if torch.cuda.is_available() else "cpu"
                except Exception:
                    resolved_device = "cpu"
            else:
                resolved_device = device

            logger.info(f"Instantiating Depth Model '{model_type}' on device '{resolved_device}'")
            self._model = DepthAnythingV2Model()
            self._model.load(device=resolved_device)
        return self._model
