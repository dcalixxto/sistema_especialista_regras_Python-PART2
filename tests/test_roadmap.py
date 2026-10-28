"""Fase 3 — análise de gaps e roadmap para atingir o nível Júnior.

Executar:  python -m pytest -v
"""

import copy

import pytest

from consultor import BaseInvalida, analisar_gaps, carregar_base, gerar_roadmap, planejar, prontidao

BASE = carregar_base()
TRILHAS = list(BASE["trilhas"])


def competencias(trilha):
    return BASE["roadmaps"][trilha]["competencias"]


def nivel_junior(trilha):
    return {c["id"]: c["nivel_junior"] for c in competencias(trilha)}


def test_toda_trilha_tem_competencias_certificacoes_e_projetos():
    for trilha in TRILHAS:
        r = BASE["roadmaps"][trilha]
        assert 4 <= len(r["competencias"]) <= 6
        assert 2 <= len(r["certificacoes"]) <= 3
        assert len(r["projetos_portfolio"]) == 3
        assert any(c["prontidao_minima"] == 0 for c in r["certificacoes"]), trilha


def test_toda_competencia_e_coberta_por_algum_projeto():
    for trilha in TRILHAS:
        cobertas = {c for p in BASE["roadmaps"][trilha]["projetos_portfolio"] for c in p["competencias"]}
        assert cobertas == set(nivel_junior(trilha)), trilha


@pytest.mark.parametrize("trilha", TRILHAS)
def test_nivel_junior_zera_os_gaps(trilha):
    gaps = analisar_gaps(trilha, nivel_junior(trilha), BASE)
    assert all(g.deficit == 0 and g.prioridade == 0 for g in gaps)
    assert prontidao(gaps) == 100

    plano = gerar_roadmap(trilha, gaps, 10, BASE)
    assert plano.etapas == [] and plano.semanas_total == 0
    assert plano.certificacoes_futuras == []
    assert len(plano.projetos) == 3


def test_acima_do_junior_nao_gera_deficit_negativo():
    gaps = analisar_gaps("backend", {c["id"]: 3 for c in competencias("backend")}, BASE)
    assert all(g.deficit == 0 for g in gaps)
    assert prontidao(gaps) == 100


@pytest.mark.parametrize("trilha", TRILHAS)
def test_sem_conhecimento_prontidao_zero(trilha):
    gaps = analisar_gaps(trilha, {}, BASE)
    assert prontidao(gaps) == 0
    assert all(g.atual == 0 and g.deficit == g.junior for g in gaps)

    plano = gerar_roadmap(trilha, gaps, 10, BASE)
    assert len(plano.etapas) == len(gaps)
    assert all(c["prontidao_minima"] == 0 for c in plano.certificacoes)
    assert plano.certificacoes_futuras


def test_gaps_ordenados_por_prioridade():
    gaps = analisar_gaps("dados_ml", {"python_dados": 2, "estatistica": 1}, BASE)
    prioridades = [g.prioridade for g in gaps]
    assert prioridades == sorted(prioridades, reverse=True)
    assert gaps[0].competencia == "ml"            # déficit 2 × importância 3
    assert gaps[-1].competencia == "python_dados"  # já no nível júnior
    assert next(g for g in gaps if g.competencia == "estatistica").prioridade == 3


def test_roadmap_estuda_primeiro_o_mais_prioritario_e_estima_semanas():
    plano = planejar("devops", {"linux_devops": 2}, horas_semana=10, base=BASE)
    assert plano.etapas[0].gap.prioridade == max(e.gap.prioridade for e in plano.etapas)
    assert "linux_devops" not in [e.gap.competencia for e in plano.etapas]

    horas = BASE["parametros"]["horas_por_nivel"]
    assert plano.horas_total == horas * sum(e.gap.deficit for e in plano.etapas)
    assert plano.semanas_total == -(-plano.horas_total // 10)
    assert plano.etapas[-1].semana_fim == plano.semanas_total
    inicios = [e.semana_inicio for e in plano.etapas]
    assert inicios == sorted(inicios)


def test_mais_horas_por_semana_encurtam_o_plano():
    curto = planejar("cloud", {}, 20, BASE).semanas_total
    longo = planejar("cloud", {}, 5, BASE).semanas_total
    assert curto < longo


def test_certificacoes_filtradas_pela_prontidao():
    gaps = analisar_gaps("seguranca", {"redes": 2, "linux_seg": 2, "fundamentos_seg": 1}, BASE)
    plano = gerar_roadmap("seguranca", gaps, 8, BASE)
    assert all(c["prontidao_minima"] <= plano.prontidao for c in plano.certificacoes)
    assert all(c["prontidao_minima"] > plano.prontidao for c in plano.certificacoes_futuras)


def test_projetos_cobrem_os_gaps():
    plano = planejar("frontend", {"html_css": 2, "ux_ui": 1, "git": 2}, 10, BASE)
    assert plano.projetos and all(p["cobre"] for p in plano.projetos)
    assert "Portfólio pessoal responsivo" not in [p["titulo"] for p in plano.projetos]


@pytest.mark.parametrize("conhecimento", [
    {"prog_backend": 4}, {"prog_backend": -1}, {"prog_backend": "2"},
    {"prog_backend": 1.5}, {"prog_backend": None}, {"prog_backend": True},
    {"competencia_que_nao_existe": 1},
])
def test_conhecimento_invalido_e_rejeitado(conhecimento):
    with pytest.raises(ValueError):
        analisar_gaps("backend", conhecimento, BASE)


def test_trilha_inexistente_e_rejeitada():
    with pytest.raises(ValueError):
        analisar_gaps("astronauta", {}, BASE)


@pytest.mark.parametrize("horas", [0, -5, 200, "10", None, True])
def test_horas_por_semana_invalidas_sao_rejeitadas(horas):
    gaps = analisar_gaps("qa", {}, BASE)
    with pytest.raises(ValueError):
        gerar_roadmap("qa", gaps, horas, BASE)


def test_gaps_de_outra_trilha_sao_rejeitados():
    gaps = analisar_gaps("qa", {}, BASE)
    with pytest.raises(ValueError):
        gerar_roadmap("mobile", gaps, 10, BASE)


def test_projeto_com_competencia_inexistente_e_rejeitado():
    base = copy.deepcopy(BASE)
    base["roadmaps"]["backend"]["projetos_portfolio"][0]["competencias"].append("competencia_fantasma")
    with pytest.raises(BaseInvalida):
        analisar_gaps("backend", {}, base)


@pytest.mark.parametrize("alterar", [
    lambda r: r["competencias"].append(dict(r["competencias"][0])),            # id duplicado
    lambda r: r["competencias"][0].update(nivel_junior=4),                    # fora da escala
    lambda r: r["competencias"][0].update(nivel_junior=0),                    # júnior sem exigência
    lambda r: r["competencias"][0].update(importancia=5),
    lambda r: r["certificacoes"][0].update(nivel_entrada="mestre"),
    lambda r: r["certificacoes"][0].update(prontidao_minima=150),
])
def test_roadmap_invalido_na_base_e_rejeitado(alterar):
    base = copy.deepcopy(BASE)
    alterar(base["roadmaps"]["backend"])
    with pytest.raises(BaseInvalida):
        analisar_gaps("backend", {}, base)


def test_trilha_sem_roadmap_e_rejeitada():
    base = copy.deepcopy(BASE)
    del base["roadmaps"]["produto"]
    with pytest.raises(BaseInvalida):
        analisar_gaps("backend", {}, base)
