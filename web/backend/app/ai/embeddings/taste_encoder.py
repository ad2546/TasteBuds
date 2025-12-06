"""PyTorch model for encoding TasteDNA into embeddings."""

from typing import List, Dict
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# Cuisine mapping for one-hot encoding
CUISINE_TYPES = [
    "italian", "japanese", "mexican", "chinese", "indian", "thai",
    "french", "mediterranean", "korean", "vietnamese", "american",
    "middle_eastern", "greek", "spanish", "ethiopian", "brazilian",
]

# Ambiance mapping
AMBIANCE_TYPES = ["casual", "upscale", "cozy", "trendy", "lively"]


if TORCH_AVAILABLE:
    class TasteEncoder(nn.Module):
        """Neural network for encoding taste profiles into embeddings."""

        def __init__(self, input_dim: int = 64, embedding_dim: int = 512):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, 512),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(512, embedding_dim),
                nn.LayerNorm(embedding_dim),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """Forward pass - encode input to normalized embedding."""
            embedding = self.encoder(x)
            return F.normalize(embedding, p=2, dim=1)


class TasteEmbeddingService:
    """Service for generating taste embeddings."""

    EMBEDDING_DIM = 512

    def __init__(self):
        self.model = None
        if TORCH_AVAILABLE:
            self.model = TasteEncoder(input_dim=64, embedding_dim=self.EMBEDDING_DIM)
            self.model.eval()

    def _encode_cuisines(self, cuisines: List[str]) -> List[float]:
        """One-hot encode cuisine preferences."""
        encoding = [0.0] * len(CUISINE_TYPES)
        for cuisine in cuisines:
            cuisine_lower = cuisine.lower().replace(" ", "_")
            if cuisine_lower in CUISINE_TYPES:
                idx = CUISINE_TYPES.index(cuisine_lower)
                encoding[idx] = 1.0
        return encoding

    def _encode_ambiance(self, ambiance: str) -> List[float]:
        """One-hot encode ambiance preference."""
        encoding = [0.0] * len(AMBIANCE_TYPES)
        if ambiance and ambiance.lower() in AMBIANCE_TYPES:
            idx = AMBIANCE_TYPES.index(ambiance.lower())
            encoding[idx] = 1.0
        return encoding

    def _prepare_input(self, taste_dna: Dict) -> np.ndarray:
        """Prepare TasteDNA dict as input vector."""
        # Core metrics (4 values)
        core = [
            taste_dna.get("adventure_score", 0.5),
            taste_dna.get("spice_tolerance", 0.5),
            taste_dna.get("price_sensitivity", 0.5),
            taste_dna.get("cuisine_diversity", 0.5),
        ]

        # Cuisine encoding (16 values)
        cuisines = self._encode_cuisines(taste_dna.get("preferred_cuisines", []))

        # Ambiance encoding (5 values)
        ambiance = self._encode_ambiance(taste_dna.get("ambiance_preference", "casual"))

        # Combine all features
        features = core + cuisines + ambiance

        # Pad to 64 dimensions if needed
        while len(features) < 64:
            features.append(0.0)

        return np.array(features[:64], dtype=np.float32)

    def generate_embedding(self, taste_dna: Dict) -> List[float]:
        """Generate embedding vector from TasteDNA."""
        input_vector = self._prepare_input(taste_dna)

        if TORCH_AVAILABLE and self.model:
            # Use PyTorch model
            with torch.no_grad():
                input_tensor = torch.tensor(input_vector).unsqueeze(0)
                embedding = self.model(input_tensor)
                return embedding.squeeze(0).tolist()
        else:
            # Fallback: Use input features expanded to embedding dim
            # This is a simple fallback when PyTorch is not available
            np.random.seed(int(sum(input_vector) * 1000) % (2**32))
            embedding = np.random.randn(self.EMBEDDING_DIM).astype(np.float32)
            # Incorporate actual taste features
            for i, val in enumerate(input_vector):
                if val > 0:
                    embedding[i * 8:(i + 1) * 8] += val
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


# Global service instance
taste_embedding_service = TasteEmbeddingService()


def get_embedding_service() -> TasteEmbeddingService:
    """Dependency to get embedding service."""
    return taste_embedding_service
