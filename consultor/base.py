"""Carregamento e validação da base de conhecimento (regras_carreiras.json).

A base fica num arquivo externo para que regras, pesos e trilhas possam ser
alterados sem mexer no código do motor de inferência.
"""

import json
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).with_name("regras_carreiras.json")
SECOES = ("parametros", "escala", "etapas", "trilhas", "perguntas", "regras")
TIPOS_REGRA = ("afinidade", "combinada", "penalidade")


class BaseInvalida(ValueError):
    """A base de conhecimento tem estrutura ou referências inválidas."""


def carregar_base(caminho=None) -> dict:
    """Lê o JSON da base de conhecimento e valida sua consistência."""
    caminho = Path(caminho) if caminho else CAMINHO_PADRAO
    with open(caminho, encoding="utf-8") as arquivo:
        base = json.load(arquivo)
    validar_base(base)
    return base


def termos(regra: dict) -> list:
    """Termos da condição de uma regra (``"!x"`` significa baixa afinidade com ``x``)."""
    condicao = regra["condicao"]
    return condicao.get("todas") or condicao.get("alguma") or []


def validar_base(base: dict) -> None:
    faltando = [s for s in SECOES if s not in base]
    if faltando:
        raise BaseInvalida(f"Seções ausentes: {', '.join(faltando)}")

    if base["escala"]["min"] >= base["escala"]["max"]:
        raise BaseInvalida("Escala inválida: 'min' deve ser menor que 'max'")

    etapas = {e["id"] for e in base["etapas"]}
    perguntas = set()
    for p in base["perguntas"]:
        if p["id"] in perguntas:
            raise BaseInvalida(f"Pergunta duplicada: {p['id']}")
        if p["etapa"] not in etapas:
            raise BaseInvalida(f"Pergunta {p['id']} aponta para etapa inexistente: {p['etapa']}")
        perguntas.add(p["id"])

    ids = set()
    positivas = {t: 0 for t in base["trilhas"]}
    for r in base["regras"]:
        if r["id"] in ids:
            raise BaseInvalida(f"Regra duplicada: {r['id']}")
        ids.add(r["id"])
        if r["trilha"] not in base["trilhas"]:
            raise BaseInvalida(f"Regra {r['id']} aponta para trilha inexistente: {r['trilha']}")
        if r["tipo"] not in TIPOS_REGRA:
            raise BaseInvalida(f"Regra {r['id']} tem tipo inválido: {r['tipo']}")
        if not isinstance(r["peso"], (int, float)) or r["peso"] == 0:
            raise BaseInvalida(f"Regra {r['id']} precisa de peso numérico diferente de zero")
        if (r["peso"] < 0) != (r["tipo"] == "penalidade"):
            raise BaseInvalida(f"Regra {r['id']}: só penalidades têm peso negativo")
        if len(r["condicao"]) != 1 or not termos(r):
            raise BaseInvalida(f"Regra {r['id']} precisa de condição 'todas' ou 'alguma' não vazia")
        for termo in termos(r):
            if termo.lstrip("!") not in perguntas:
                raise BaseInvalida(f"Regra {r['id']} usa pergunta inexistente: {termo}")
        if r["peso"] > 0:
            positivas[r["trilha"]] += 1

    sem_regras = [t for t, n in positivas.items() if n == 0]
    if sem_regras:
        raise BaseInvalida(f"Trilhas sem regras positivas: {', '.join(sem_regras)}")
