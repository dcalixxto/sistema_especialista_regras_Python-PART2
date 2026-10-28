"""Consultor Avançado de Carreiras em TI — Sistema Especialista com pontuação ponderada."""

from .base import BaseInvalida, carregar_base
from .motor import Compatibilidade, Evidencia, MotorInferencia, Resultado, diagnosticar

__all__ = [
    "BaseInvalida", "carregar_base",
    "Compatibilidade", "Evidencia", "MotorInferencia", "Resultado", "diagnosticar",
]
