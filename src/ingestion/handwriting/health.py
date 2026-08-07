from typing import Dict, Any
import torch

from src.llm.ollama import get_ollama_client
from src.logger import log


class OllamaHealthCheck:
    """
    Automated health check and hardware monitoring service for local Ollama OCR.
    Uses centralized OllamaClient singleton and PyTorch VRAM telemetry.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        target_model: str = "qwen2.5vl:3b",
    ):
        self.target_model = target_model
        self.client = get_ollama_client()

    def check_health(self) -> Dict[str, Any]:
        """
        Queries Ollama API service and returns comprehensive health status dictionary.
        """
        online = self.client.is_available()
        model_found = self.client.has_model(self.target_model) if online else False

        if online and model_found:
            msg = f"Ollama Active: Local VLM model '{self.target_model}' ready."
        elif online:
            msg = f"Ollama Active: Model '{self.target_model}' not pulled yet. Run 'ollama pull {self.target_model}'."
        else:
            msg = "Ollama service unreachable."

        return {
            "service_online": online,
            "host": self.client.host,
            "target_model": self.target_model,
            "model_available": model_found,
            "vram": self.get_vram_telemetry(),
            "message": msg,
        }

    @staticmethod
    def get_vram_telemetry() -> Dict[str, Any]:
        if torch.cuda.is_available():
            allocated_gb = round(torch.cuda.memory_allocated(0) / 1e9, 2)
            reserved_gb = round(torch.cuda.memory_reserved(0) / 1e9, 2)
            total_gb = round(
                torch.cuda.get_device_properties(0).total_memory / 1e9, 2
            )
            device_name = torch.cuda.get_device_name(0)
            return {
                "cuda_available": True,
                "device_name": device_name,
                "allocated_gb": allocated_gb,
                "reserved_gb": reserved_gb,
                "total_gb": total_gb,
                "utilization_percent": round((reserved_gb / total_gb) * 100, 1),
            }
        return {
            "cuda_available": False,
            "device_name": "CPU Mode",
            "allocated_gb": 0.0,
            "reserved_gb": 0.0,
            "total_gb": 0.0,
            "utilization_percent": 0.0,
        }
