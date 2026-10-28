"""Fases 1 e 2 — base de conhecimento em JSON e motor de inferência ponderado.

Executar:  python -m pytest -v
"""

import copy
import random

import pytest

from consultor import BaseInvalida, MotorInferencia, carregar_base, diagnosticar

BASE = carregar_base()
PERGUNTAS = [p["id"] for p in BASE["perguntas"]]


def respostas(padrao=2, **altas):
    r = {p: padrao for p in PERGUNTAS}
    r.update(altas)
    return r


def test_base_cobre_as_10_trilhas_e_3_etapas():
    assert len(BASE["trilhas"]) == 10
    assert [e["id"] for e in BASE["etapas"]] == ["perfil", "afinidades", "objetivos"]
    assert {r["trilha"] for r in BASE["regras"]} == set(BASE["trilhas"])


def test_toda_pergunta_e_usada_por_alguma_regra():
    usadas = {t.lstrip("!") for r in BASE["regras"] for t in r["condicao"]["todas"]}
    assert usadas == set(PERGUNTAS)


def test_base_com_referencia_invalida_e_rejeitada():
    base = copy.deepcopy(BASE)
    base["regras"][0]["condicao"] = {"todas": ["pergunta_que_nao_existe"]}
    with pytest.raises(BaseInvalida):
        MotorInferencia(base)


def test_penalidade_precisa_de_peso_negativo():
    base = copy.deepcopy(BASE)
    base["regras"][0]["tipo"] = "penalidade"
    with pytest.raises(BaseInvalida):
        MotorInferencia(base)


def test_perfil_forte_gera_top3_com_percentuais():
    r = diagnosticar(respostas(matematica=5, obj_previsoes=5, logica=5))
    assert r.vencedora.trilha == "dados_ml"
    assert len(r.top3) == 3
    percentuais = [c.percentual for c in r.ranking]
    assert percentuais == sorted(percentuais, reverse=True)
    assert all(0 <= p <= 100 for p in percentuais)
    assert not r.empate_parcial


def test_resposta_gradual_aumenta_compatibilidade():
    pct = [next(c.percentual for c in diagnosticar(respostas(automacao=n)).ranking if c.trilha == "devops")
           for n in range(1, 6)]
    assert pct == sorted(pct) and pct[0] < pct[-1]


def test_penalidade_por_perfil_conflitante():
    """Quer modelos preditivos, mas sem matemática: Ciência de Dados cai."""
    def pct_ds(matematica):
        r = diagnosticar(respostas(obj_previsoes=5, matematica=matematica))
        return next(c for c in r.ranking if c.trilha == "dados_ml")

    sem_mat, com_mat = pct_ds(1), pct_ds(5)
    assert sem_mat.percentual < com_mat.percentual
    assert any(e.regra == "P03" and e.pontos < 0 for e in sem_mat.evidencias)


def test_evidencias_explicam_a_vencedora():
    r = diagnosticar(respostas(seguranca_info=5, obj_protecao=5, redes_linux=5))
    regras = {e.regra for e in r.vencedora.evidencias}
    assert {"R21", "R22", "R25"} <= regras
    assert r.vencedora.regras_fortes >= 2


def test_respostas_neutras_sinalizam_empate_e_certeza_zero():
    r = diagnosticar(respostas(padrao=3))
    assert r.empate_parcial
    assert r.certeza == 0


def test_respostas_minimas_zeram_compatibilidade():
    r = diagnosticar(respostas(padrao=1))
    assert all(c.percentual == 0 for c in r.ranking)


def test_respostas_aleatorias_sempre_geram_ranking_completo():
    rng = random.Random(42)
    for _ in range(300):
        r = diagnosticar({p: rng.randint(1, 5) for p in PERGUNTAS})
        assert len(r.ranking) == 10
        assert 0 <= r.certeza <= 1


@pytest.mark.parametrize("valor", [0, 6, "5", 3.5, None, True])
def test_respostas_invalidas_sao_rejeitadas(valor):
    with pytest.raises(ValueError):
        diagnosticar(respostas(matematica=valor))


def test_respostas_faltando_sao_rejeitadas():
    with pytest.raises(ValueError):
        diagnosticar({"matematica": 5})
