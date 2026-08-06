import requests
import torch
from typing import Dict, Any
from src.logger import log

class OllamaHealthCheck:
    """
    Automated health check and hardware monitoring service for local Ollama Vision OCR.
    Verifies service connectivity, model availability, and VRAM utilization.
    """

    def __init__(self, host: str = "http://localhost:11434", target_model: str = "qwen2.5vl:3b"):
        self.host = host.rstrip("/")
        self.target_model = target_model

    def check_health(self) -> Dict[str, Any]:
        """
        Queries Ollama API service and returns comprehensive health status dictionary.
        """
        status_info = {
            "service_online": False,
            "host": self.host,
            "target_model": self.target_model,
            "model_available": False,
            "available_models": [],
            "vram": self.get_vram_telemetry(),
            "message": "Ollama service unreachable."
        }

        try:
            # 1. Query Ollama tags endpoint
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            if resp.status_code == 200:
                status_info["service_online"] = True
                models_data = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models_data]
                status_info["available_models"] = model_names

                # Check if target model or tag variant is present
                model_found = any(self.target_model in m for m in model_names)
                status_info["model_available"] = model_found

                if model_found:
                    status_info["message"] = f"Ollama Active: Local VLM model '{self.target_model}' ready."
                else:
                    status_info["message"] = f"Ollama Active: Model '{self.target_model}' not pulled yet. Run 'ollama pull {self.target_model}'."
        except Exception as e:
            status_info["message"] = f"Ollama Health Check Failed: {e}"

        return status_info

    @staticmethod
    def get_vram_telemetry() -> Dict[str, Any]:
        if torch.cuda.is_available():
            allocated_gb = round(torch.cuda.memory_allocated(0) / 1e9, 2)
            reserved_gb = round(torch.cuda.memory_reserved(0) / 1e9, 2)
            total_gb = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
            device_name = torch.cuda.get_device_name(0)
            return {
                "cuda_available": True,
                "device_name": device_name,
                "allocated_gb": allocated_gb,
                "reserved_gb": reserved_gb,
                "total_gb": total_gb,
                "utilization_percent": round((reserved_gb / total_gb) * 100, 1)
            }
        return {
            "cuda_available": False,
            "device_name": "CPU Mode",
            "allocated_gb": 0.0,
            "reserved_gb": 0.0,
            "total_gb": 0.0,
            "utilization_percent": 0.0
        }
