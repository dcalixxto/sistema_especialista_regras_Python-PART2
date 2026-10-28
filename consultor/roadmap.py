"""Análise de gaps e roadmap personalizado para atingir o nível Júnior.

Funcionamento:
  1. O usuário informa seu nível atual (0 nenhum, 1 básico, 2 intermediário,
     3 avançado) em cada competência da trilha escolhida.
  2. Gap = competência abaixo do nível Júnior. Déficit = júnior − atual e
     prioridade = déficit × importância da competência.
  3. Prontidão (%) = níveis já atingidos ÷ níveis exigidos, ponderados pela importância.
  4. O roadmap estuda primeiro as competências de maior prioridade, estima a
     duração com as horas semanais disponíveis e sugere certificações
     compatíveis com a prontidão e projetos de portfólio que cobrem os gaps.
"""

import math
from dataclasses import dataclass, field

from .base import carregar_base, validar_base


@dataclass
class Gap:
    competencia: str
    nome: str
    atual: int
    junior: int
    importancia: int
    tecnologias: list

    @property
    def deficit(self) -> int:
        return max(0, self.junior - self.atual)

    @property
    def prioridade(self) -> int:
        return self.deficit * self.importancia


@dataclass
class EtapaEstudo:
    """Uma competência a estudar no roadmap, com sua janela de semanas."""

    ordem: int
    gap: Gap
    horas: float
    semana_inicio: int
    semana_fim: int


@dataclass
class Roadmap:
    trilha: str
    nome: str
    prontidao: float
    horas_semana: float
    etapas: list = field(default_factory=list)                 # [EtapaEstudo] por prioridade
    certificacoes: list = field(default_factory=list)          # já compatíveis com a prontidão
    certificacoes_futuras: list = field(default_factory=list)  # para depois de evoluir
    projetos: list = field(default_factory=list)               # [dict] com a chave extra 'cobre'

    @property
    def horas_total(self) -> float:
        return sum(e.horas for e in self.etapas)

    @property
    def semanas_total(self) -> int:
        return math.ceil(self.horas_total / self.horas_semana)


def _base(base):
    if base is None:
        return carregar_base()
    validar_base(base)
    return base


def _roadmap_da_trilha(trilha, base) -> dict:
    if trilha not in base["roadmaps"]:
        raise ValueError(f"Trilha inexistente: {trilha!r}")
    return base["roadmaps"][trilha]


def analisar_gaps(trilha: str, conhecimento: dict, base=None) -> list:
    """Compara o conhecimento atual com o nível Júnior; competências omitidas valem 0.

    Retorna todas as competências da trilha como ``Gap`` (déficit 0 quando já
    atingiu o nível Júnior), ordenadas da maior para a menor prioridade.
    """
    base = _base(base)
    competencias = _roadmap_da_trilha(trilha, base)["competencias"]
    escala = base["escala_conhecimento"]

    ids = [c["id"] for c in competencias]
    desconhecidas = [c for c in conhecimento if c not in ids]
    if desconhecidas:
        raise ValueError(f"Competências inexistentes em {trilha}: {', '.join(map(str, desconhecidas))}")
    for comp, valor in conhecimento.items():
        if isinstance(valor, bool) or not isinstance(valor, int) or not escala["min"] <= valor <= escala["max"]:
            raise ValueError(f"Nível inválido para '{comp}': {valor!r}")

    gaps = [Gap(c["id"], c["nome"], conhecimento.get(c["id"], 0), c["nivel_junior"], c["importancia"], c["tecnologias"])
            for c in competencias]
    # Desempate: maior importância, depois a ordem da base
    return sorted(gaps, key=lambda g: (-g.prioridade, -g.importancia, ids.index(g.competencia)))


def prontidao(gaps: list) -> float:
    """Percentual do nível Júnior já atingido, ponderado pela importância."""
    exigido = sum(g.junior * g.importancia for g in gaps)
    atingido = sum(min(g.atual, g.junior) * g.importancia for g in gaps)
    return round(100 * atingido / exigido, 1) if exigido else 100.0


def gerar_roadmap(trilha: str, gaps: list, horas_semana: float, base=None) -> Roadmap:
    """Monta o plano de estudos a partir dos gaps de ``analisar_gaps``."""
    base = _base(base)
    roadmap = _roadmap_da_trilha(trilha, base)
    if isinstance(horas_semana, bool) or not isinstance(horas_semana, (int, float)) or not 0 < horas_semana <= 168:
        raise ValueError(f"Horas por semana inválidas: {horas_semana!r}")
    competencias = {c["id"] for c in roadmap["competencias"]}
    if not gaps or any(not isinstance(g, Gap) or g.competencia not in competencias for g in gaps):
        raise ValueError(f"Os gaps informados não correspondem à trilha {trilha!r}")

    pct = prontidao(gaps)
    plano = Roadmap(trilha=trilha, nome=base["trilhas"][trilha]["nome"], prontidao=pct, horas_semana=horas_semana)

    horas_por_nivel = base["parametros"]["horas_por_nivel"]
    acumulado = 0.0
    pendentes = sorted((g for g in gaps if g.deficit > 0), key=lambda g: -g.prioridade)
    for ordem, gap in enumerate(pendentes, start=1):
        horas = gap.deficit * horas_por_nivel
        inicio = math.floor(acumulado / horas_semana) + 1
        acumulado += horas
        plano.etapas.append(EtapaEstudo(ordem, gap, horas, inicio, math.ceil(acumulado / horas_semana)))

    for cert in sorted(roadmap["certificacoes"], key=lambda c: c["prontidao_minima"]):
        (plano.certificacoes if cert["prontidao_minima"] <= pct else plano.certificacoes_futuras).append(cert)

    # Projetos que cobrem os gaps mais prioritários vêm primeiro
    prioridade = {g.competencia: g.prioridade for g in pendentes}
    nomes = {g.competencia: g.nome for g in gaps}
    projetos = []
    for projeto in roadmap["projetos_portfolio"]:
        cobre = [nomes[c] for c in projeto["competencias"] if c in prioridade]
        peso = sum(prioridade.get(c, 0) for c in projeto["competencias"])
        projetos.append((peso, {**projeto, "cobre": cobre}))
    relevantes = [p for peso, p in sorted(projetos, key=lambda x: -x[0]) if p["cobre"]]
    # Sem gaps, todos os projetos continuam úteis para montar o portfólio
    plano.projetos = relevantes or [p for _, p in projetos]
    return plano


def planejar(trilha: str, conhecimento: dict, horas_semana: float, base=None) -> Roadmap:
    """Atalho: analisa os gaps e gera o roadmap de uma vez."""
    base = _base(base)
    return gerar_roadmap(trilha, analisar_gaps(trilha, conhecimento, base), horas_semana, base)
