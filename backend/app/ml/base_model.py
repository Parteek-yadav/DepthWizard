# backend/app/ml/base_model.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
import numpy as np

class BaseDepthModel(ABC):
    """Abstract base interface for monocular depth estimation backbones."""
    
    @abstractmethod
    def load(self, device: str = "cpu") -> bool:
        """Initialize model weights and setup execution device."""
        pass

    @abstractmethod
    def predict(self, rgb_image: np.ndarray) -> np.ndarray:
        """
        Infers relative depth from RGB uint8 array (H, W, 3).
        Returns normalized relative depth array (H, W) float32 in [0, 1].
        Higher values represent greater relative elevation/closer features.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Returns model metadata, license, and architectural parameters."""
        pass
