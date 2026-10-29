"""Fase 5 — testes de robustez com personas, perfis ambíguos e casos limite.

Executar:  python -m pytest -v
"""

import copy

import pytest

from consultor import MotorInferencia, carregar_base, diagnosticar, planejar
from consultor.personas import AMBIGUAS, PERSONAS, avaliar_ambiguas, avaliar_personas

BASE = carregar_base()
PERGUNTAS = set(p["id"] for p in BASE["perguntas"])
TRILHA_DA_REGRA = {r["id"]: r["trilha"] for r in BASE["regras"]}
LIMIAR_FORTE = BASE["parametros"]["limiar_regra_forte"]
DISPUTADAS = [p for p in AMBIGUAS if p.em_disputa]
LIMITE = {p.id: p for p in AMBIGUAS if not p.em_disputa}


def persona(id_):
    return next(p for p in PERSONAS if p.id == id_)


def compat(resultado, trilha):
    return next(c for c in resultado.ranking if c.trilha == trilha)


def fortes(comp):
    """Evidências positivas fortes: regra de peso alto com ativação acima do limiar."""
    return [e for e in comp.evidencias if e.peso >= 3 and e.grau >= LIMIAR_FORTE]


def test_uma_persona_por_trilha_com_respostas_completas():
    assert sorted(p.esperada for p in PERSONAS) == sorted(BASE["trilhas"])
    for p in PERSONAS + AMBIGUAS:
        assert set(p.respostas) == PERGUNTAS, p.id
        assert all(1 <= v <= 5 for v in p.respostas.values()), p.id


def test_conhecimento_das_personas_usa_competencias_da_trilha():
    for p in PERSONAS:
        ids = {c["id"] for c in BASE["roadmaps"][p.esperada]["competencias"]}
        assert p.conhecimento and set(p.conhecimento) <= ids, p.id


@pytest.mark.parametrize("p", PERSONAS, ids=lambda p: p.id)
def test_persona_recebe_a_trilha_esperada_em_primeiro(p):
    r = diagnosticar(p.respostas)
    assert r.vencedora.trilha == p.esperada
    assert not r.empate_parcial


@pytest.mark.parametrize("p", PERSONAS, ids=lambda p: p.id)
def test_vencedora_resiste_a_mudanca_de_uma_resposta(p):
    """Mudar qualquer resposta em ±1 ponto não troca a trilha vencedora de um perfil típico."""
    for pergunta, valor in p.respostas.items():
        for novo in (valor - 1, valor + 1):
            if 1 <= novo <= 5:
                r = diagnosticar({**p.respostas, pergunta: novo})
                assert r.vencedora.trilha == p.esperada, (pergunta, novo)


@pytest.mark.parametrize("p", PERSONAS, ids=lambda p: p.id)
def test_justificativa_da_vencedora_e_coerente(p):
    vencedora = diagnosticar(p.respostas).vencedora
    assert fortes(vencedora), "nenhuma evidência positiva forte"
    assert all(TRILHA_DA_REGRA[e.regra] == p.esperada for e in vencedora.evidencias)
    assert vencedora.evidencias[0].pontos > 0  # a evidência de maior peso é a favor


@pytest.mark.parametrize("p", DISPUTADAS, ids=lambda p: p.id)
def test_perfil_ambiguo_sinaliza_empate_parcial(p):
    r = diagnosticar(p.respostas)
    assert r.empate_parcial is p.empate_parcial
    assert r.margem < BASE["parametros"]["limiar_empate"]
    assert {c.trilha for c in r.ranking[:2]} == set(p.em_disputa)
    assert set(p.em_disputa) <= {c.trilha for c in r.top3}


@pytest.mark.parametrize("p", DISPUTADAS, ids=lambda p: p.id)
def test_perfil_ambiguo_justifica_as_duas_trilhas(p):
    r = diagnosticar(p.respostas)
    for trilha in p.em_disputa:
        comp = compat(r, trilha)
        assert fortes(comp), trilha
        assert all(TRILHA_DA_REGRA[e.regra] == trilha for e in comp.evidencias)


# (persona, trilha "gêmea" que ela não deve escolher, penalidade que separa as duas)
PARES = [
    ("fernanda", "mobile", "P11"),
    ("marcos", "frontend", "P02"),
    ("daniela", "eng_dados", "P05"),
    ("eduardo", "dados_ml", "P04"),
    ("diego", "cloud", "P10"),
    ("camila", "devops", "P08"),
]


def base_sem_penalidades():
    base = copy.deepcopy(BASE)
    base["regras"] = [r for r in base["regras"] if r["tipo"] != "penalidade"]
    return base


@pytest.mark.parametrize("id_, gemea, penalidade", PARES)
def test_penalidade_separa_trilhas_parecidas(id_, gemea, penalidade):
    p = persona(id_)
    com = MotorInferencia(BASE).inferir(p.respostas)
    sem = MotorInferencia(base_sem_penalidades()).inferir(p.respostas)

    assert any(e.regra == penalidade and e.pontos < 0 for e in compat(com, gemea).evidencias)
    margem_com = compat(com, p.esperada).percentual - compat(com, gemea).percentual
    margem_sem = compat(sem, p.esperada).percentual - compat(sem, gemea).percentual
    assert margem_com > margem_sem


@pytest.mark.parametrize("p", PERSONAS, ids=lambda p: p.id)
def test_roadmap_nao_sugere_competencias_dominadas(p):
    plano = planejar(p.esperada, p.conhecimento, horas_semana=10)
    junior = {c["id"]: c["nivel_junior"] for c in BASE["roadmaps"][p.esperada]["competencias"]}
    dominadas = {c for c, nivel in p.conhecimento.items() if nivel >= junior[c]}
    sugeridas = {e.gap.competencia for e in plano.etapas}

    assert dominadas, "a persona deveria dominar ao menos uma competência"
    assert not dominadas & sugeridas
    assert sugeridas == {c for c in junior if p.conhecimento.get(c, 0) < junior[c]}
    assert 0 < plano.prontidao < 100
    assert all(set(proj["cobre"]) for proj in plano.projetos)


def test_casos_limite_tudo_1_tudo_3_tudo_5():
    neutro, tudo5, tudo1 = (diagnosticar(LIMITE[i].respostas) for i in ("neutro", "tudo5", "tudo1"))
    for r in (neutro, tudo5, tudo1):
        assert len(r.ranking) == 10 and len(r.top3) == 3
        assert r.empate_parcial

    assert neutro.certeza == 0
    assert all(0 < c.percentual < 100 for c in neutro.ranking)
    assert tudo5.certeza == 1 and all(c.percentual == 100 for c in tudo5.ranking)
    assert tudo1.certeza == 1 and all(c.percentual == 0 for c in tudo1.ranking)
    # Com tudo em 1, as penalidades disparam mas a compatibilidade não fica negativa
    assert any(e.pontos < 0 for c in tudo1.ranking for e in c.evidencias)


def test_desempate_em_caso_limite_e_deterministico():
    ordem = list(BASE["trilhas"])
    r = diagnosticar(LIMITE["tudo5"].respostas)
    chaves = [(-c.regras_fortes, ordem.index(c.trilha)) for c in r.ranking]
    assert chaves == sorted(chaves)
    assert [c.trilha for c in r.ranking] == [c.trilha for c in diagnosticar(LIMITE["tudo5"].respostas).ranking]


@pytest.mark.parametrize("caso", LIMITE)
def test_roadmap_funciona_nos_casos_limite(caso):
    r = diagnosticar(LIMITE[caso].respostas)
    for comp in r.top3:
        competencias = BASE["roadmaps"][comp.trilha]["competencias"]
        zero = planejar(comp.trilha, {}, horas_semana=1)
        assert zero.prontidao == 0 and len(zero.etapas) == len(competencias)
        maximo = planejar(comp.trilha, {c["id"]: 3 for c in competencias}, horas_semana=40)
        assert maximo.prontidao == 100 and not maximo.etapas and maximo.semanas_total == 0
        assert maximo.projetos


def test_relatorios_de_validacao():
    linhas = avaliar_personas()
    assert len(linhas) == 10 and all(l["Acertou"] for l in linhas)
    assert all(l["Conforme"] for l in avaliar_ambiguas())
