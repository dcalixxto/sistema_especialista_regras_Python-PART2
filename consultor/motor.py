"""Motor de inferência com pontuação ponderada e tratamento de incerteza.

Funcionamento:
  1. Cada resposta Likert (1 a 5) vira uma intensidade entre 0 e 1.
  2. Cada regra SE-ENTÃO tem um grau de ativação: ``todas`` = mínimo dos termos (E),
     ``alguma`` = máximo (OU). O termo ``!x`` vale ``1 - x`` (baixa afinidade).
  3. Pontos da regra = peso × grau. Penalidades têm peso negativo e reduzem a
     pontuação de trilhas com perfil conflitante.
  4. Compatibilidade (%) = pontos da trilha / soma dos pesos positivos da trilha.
"""

from dataclasses import dataclass, field

from .base import carregar_base, termos, validar_base


@dataclass
class Evidencia:
    """Uma regra que disparou (grau > 0) a favor ou contra uma trilha."""

    regra: str
    descricao: str
    tipo: str
    peso: float
    grau: float

    @property
    def pontos(self) -> float:
        return self.peso * self.grau


@dataclass
class Compatibilidade:
    trilha: str
    nome: str
    icone: str
    pontos: float
    maximo: float
    regras_fortes: int
    evidencias: list = field(default_factory=list)

    @property
    def percentual(self) -> float:
        return round(max(0.0, min(100.0, 100 * self.pontos / self.maximo)), 1)


@dataclass
class Resultado:
    ranking: list            # [Compatibilidade] em ordem decrescente
    certeza: float           # 0 a 1: quão decididas (longe do neutro) foram as respostas
    empate_parcial: bool     # 1ª e 2ª colocadas separadas por menos que o limiar

    @property
    def vencedora(self) -> Compatibilidade:
        return self.ranking[0]

    @property
    def top3(self) -> list:
        return self.ranking[:3]

    @property
    def margem(self) -> float:
        return round(self.ranking[0].percentual - self.ranking[1].percentual, 1)


class MotorInferencia:
    def __init__(self, base=None):
        if base is None:
            base = carregar_base()
        else:
            validar_base(base)
        self.base = base
        self.escala = self.base["escala"]
        self.parametros = self.base["parametros"]

    def validar_respostas(self, respostas: dict) -> None:
        faltando = [p["id"] for p in self.base["perguntas"] if p["id"] not in respostas]
        if faltando:
            raise ValueError(f"Respostas faltando: {', '.join(faltando)}")
        for p in self.base["perguntas"]:
            valor = respostas[p["id"]]
            if isinstance(valor, bool) or not isinstance(valor, int) \
                    or not self.escala["min"] <= valor <= self.escala["max"]:
                raise ValueError(f"Valor inválido para '{p['id']}': {valor!r}")

    def intensidades(self, respostas: dict) -> dict:
        """Converte a escala Likert para [0, 1] (1 → 0.0, 3 → 0.5, 5 → 1.0)."""
        lo, hi = self.escala["min"], self.escala["max"]
        return {p["id"]: (respostas[p["id"]] - lo) / (hi - lo) for p in self.base["perguntas"]}

    @staticmethod
    def grau(regra: dict, intensidades: dict) -> float:
        valores = [1 - intensidades[t[1:]] if t.startswith("!") else intensidades[t] for t in termos(regra)]
        return min(valores) if "todas" in regra["condicao"] else max(valores)

    def inferir(self, respostas: dict) -> Resultado:
        self.validar_respostas(respostas)
        intensidades = self.intensidades(respostas)
        limiar_forte = self.parametros["limiar_regra_forte"]

        trilhas = {
            t: Compatibilidade(trilha=t, nome=info["nome"], icone=info["icone"], pontos=0.0, maximo=0.0, regras_fortes=0)
            for t, info in self.base["trilhas"].items()
        }
        for regra in self.base["regras"]:
            comp = trilhas[regra["trilha"]]
            if regra["peso"] > 0:
                comp.maximo += regra["peso"]
            grau = self.grau(regra, intensidades)
            if grau <= 0:
                continue
            comp.pontos += regra["peso"] * grau
            comp.evidencias.append(Evidencia(regra["id"], regra["descricao"], regra["tipo"], regra["peso"], round(grau, 2)))
            if regra["peso"] >= 3 and grau >= limiar_forte:
                comp.regras_fortes += 1

        for comp in trilhas.values():
            comp.pontos = round(comp.pontos, 2)
            comp.evidencias.sort(key=lambda e: -abs(e.pontos))

        # Desempate: percentual, depois regras decisivas fortes, depois ordem da base
        ordem = list(self.base["trilhas"])
        ranking = sorted(trilhas.values(), key=lambda c: (-c.percentual, -c.regras_fortes, ordem.index(c.trilha)))

        certeza = sum(abs(i - 0.5) * 2 for i in intensidades.values()) / len(intensidades)
        empate = ranking[0].percentual - ranking[1].percentual < self.parametros["limiar_empate"]
        return Resultado(ranking=ranking, certeza=round(certeza, 2), empate_parcial=empate)


def diagnosticar(respostas: dict, base=None) -> Resultado:
    """Atalho: executa o motor de inferência sobre as respostas."""
    return MotorInferencia(base).inferir(respostas)
