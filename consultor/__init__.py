"""Consultor Avançado de Carreiras em TI — Sistema Especialista com pontuação ponderada."""

from .base import BaseInvalida, carregar_base
from .motor import Compatibilidade, Evidencia, MotorInferencia, Resultado, diagnosticar
from .roadmap import EtapaEstudo, Gap, Roadmap, analisar_gaps, gerar_roadmap, planejar, prontidao

__all__ = [
    "BaseInvalida", "carregar_base",
    "Compatibilidade", "Evidencia", "MotorInferencia", "Resultado", "diagnosticar",
    "EtapaEstudo", "Gap", "Roadmap", "analisar_gaps", "gerar_roadmap", "planejar", "prontidao",
]
