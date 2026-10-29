"""Personas de validação (Fase 5): perfis típicos e casos ambíguos ou limite.

Cada persona responde às 28 perguntas da base (escala Likert de 1 a 5) e
informa seu conhecimento atual (0 a 3) nas competências da trilha esperada.
As personas típicas devem receber a trilha esperada em 1º lugar; as ambíguas
devem sinalizar empate parcial e trazer as trilhas em disputa no Top 3.
"""

from dataclasses import dataclass, field

from .motor import MotorInferencia


@dataclass
class Persona:
    id: str
    nome: str
    descricao: str
    respostas: dict
    esperada: str                                     # trilha que deve ficar em 1º
    conhecimento: dict = field(default_factory=dict)  # competências da trilha esperada


@dataclass
class PersonaAmbigua:
    id: str
    nome: str
    descricao: str
    respostas: dict
    em_disputa: tuple       # trilhas que devem aparecer juntas no Top 3 (vazio nos casos limite)
    empate_parcial: bool    # se o motor deve sinalizar empate parcial
    comportamento: str      # o que se espera do sistema, em texto


def _respostas(perfil: dict, afinidades: dict, objetivos: dict) -> dict:
    return {**perfil, **afinidades, **objetivos}


def _uniforme(valor: int) -> dict:
    perguntas = (
        "comunicacao", "criatividade", "detalhismo", "pressao", "curiosidade", "organizacao",
        "matematica", "logica", "design", "web", "apis", "banco_dados", "redes_linux", "seguranca_info",
        "automacao", "mobile", "nuvem", "testes",
        "obj_previsoes", "obj_pipelines", "obj_interface", "obj_sistemas", "obj_protecao",
        "obj_disponibilidade", "obj_escala", "obj_apps", "obj_qualidade", "obj_estrategia",
    )
    return {p: valor for p in perguntas}


PERSONAS = [
    Persona(
        "bruno", "Bruno, construtor de APIs",
        "Adora lógica e regras de negócio; quer construir o que roda por trás do sistema.",
        _respostas(
            {"comunicacao": 2, "criatividade": 2, "detalhismo": 4, "pressao": 3, "curiosidade": 3, "organizacao": 3},
            {"matematica": 3, "logica": 5, "design": 1, "web": 2, "apis": 5, "banco_dados": 4, "redes_linux": 3,
             "seguranca_info": 2, "automacao": 3, "mobile": 1, "nuvem": 2, "testes": 3},
            {"obj_previsoes": 1, "obj_pipelines": 2, "obj_interface": 1, "obj_sistemas": 5, "obj_protecao": 2,
             "obj_disponibilidade": 2, "obj_escala": 2, "obj_apps": 1, "obj_qualidade": 3, "obj_estrategia": 1},
        ),
        "backend", {"prog_backend": 2, "git": 2, "sql_bd": 1, "apis_rest": 1},
    ),
    Persona(
        "fernanda", "Fernanda, designer que programa",
        "Criativa, ama design visual e web; quer construir o que o usuário vê.",
        _respostas(
            {"comunicacao": 3, "criatividade": 5, "detalhismo": 3, "pressao": 2, "curiosidade": 2, "organizacao": 3},
            {"matematica": 2, "logica": 3, "design": 5, "web": 5, "apis": 2, "banco_dados": 2, "redes_linux": 1,
             "seguranca_info": 1, "automacao": 2, "mobile": 2, "nuvem": 1, "testes": 2},
            {"obj_previsoes": 1, "obj_pipelines": 1, "obj_interface": 5, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 1, "obj_apps": 2, "obj_qualidade": 3, "obj_estrategia": 2},
        ),
        "frontend", {"html_css": 3, "ux_ui": 2, "javascript": 1},
    ),
    Persona(
        "daniela", "Daniela, analista com veia estatística",
        "Forte em matemática e estatística; quer criar modelos que fazem previsões.",
        _respostas(
            {"comunicacao": 3, "criatividade": 3, "detalhismo": 4, "pressao": 2, "curiosidade": 3, "organizacao": 3},
            {"matematica": 5, "logica": 4, "design": 2, "web": 1, "apis": 2, "banco_dados": 4, "redes_linux": 1,
             "seguranca_info": 1, "automacao": 2, "mobile": 1, "nuvem": 2, "testes": 2},
            {"obj_previsoes": 5, "obj_pipelines": 2, "obj_interface": 1, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 1, "obj_apps": 1, "obj_qualidade": 2, "obj_estrategia": 2},
        ),
        "dados_ml", {"estatistica": 3, "python_dados": 1, "sql_analise": 2},
    ),
    Persona(
        "eduardo", "Eduardo, encanador de dados",
        "Gosta de bancos de dados e automação; quer que os dados fluam de forma confiável.",
        _respostas(
            {"comunicacao": 2, "criatividade": 2, "detalhismo": 4, "pressao": 3, "curiosidade": 2, "organizacao": 3},
            {"matematica": 3, "logica": 4, "design": 1, "web": 1, "apis": 3, "banco_dados": 5, "redes_linux": 3,
             "seguranca_info": 2, "automacao": 4, "mobile": 1, "nuvem": 3, "testes": 2},
            {"obj_previsoes": 2, "obj_pipelines": 5, "obj_interface": 1, "obj_sistemas": 3, "obj_protecao": 1,
             "obj_disponibilidade": 2, "obj_escala": 2, "obj_apps": 1, "obj_qualidade": 2, "obj_estrategia": 1},
        ),
        "eng_dados", {"sql_modelagem": 2, "python_eng": 1, "docker_basico": 1},
    ),
    Persona(
        "sofia", "Sofia, mentalidade hacker",
        "Curiosa para descobrir como burlar sistemas; gosta de redes, Linux e criptografia.",
        _respostas(
            {"comunicacao": 2, "criatividade": 3, "detalhismo": 4, "pressao": 4, "curiosidade": 5, "organizacao": 2},
            {"matematica": 3, "logica": 3, "design": 1, "web": 2, "apis": 2, "banco_dados": 2, "redes_linux": 5,
             "seguranca_info": 5, "automacao": 3, "mobile": 1, "nuvem": 2, "testes": 3},
            {"obj_previsoes": 1, "obj_pipelines": 1, "obj_interface": 1, "obj_sistemas": 2, "obj_protecao": 5,
             "obj_disponibilidade": 2, "obj_escala": 1, "obj_apps": 1, "obj_qualidade": 3, "obj_estrategia": 1},
        ),
        "seguranca", {"redes": 2, "linux_seg": 3, "pentest": 1},
    ),
    Persona(
        "diego", "Diego, automatizador de plantão",
        "Automatiza tudo e lida bem com incidentes; quer manter os sistemas no ar.",
        _respostas(
            {"comunicacao": 3, "criatividade": 2, "detalhismo": 3, "pressao": 5, "curiosidade": 3, "organizacao": 3},
            {"matematica": 2, "logica": 3, "design": 1, "web": 2, "apis": 3, "banco_dados": 2, "redes_linux": 5,
             "seguranca_info": 3, "automacao": 5, "mobile": 1, "nuvem": 4, "testes": 3},
            {"obj_previsoes": 1, "obj_pipelines": 3, "obj_interface": 1, "obj_sistemas": 2, "obj_protecao": 2,
             "obj_disponibilidade": 5, "obj_escala": 3, "obj_apps": 1, "obj_qualidade": 3, "obj_estrategia": 1},
        ),
        "devops", {"linux_devops": 2, "git_ci": 2, "containers": 1},
    ),
    Persona(
        "camila", "Camila, arquiteta de nuvem",
        "Gosta de plataformas de nuvem e de conversar com stakeholders; quer desenhar infraestruturas escaláveis.",
        _respostas(
            {"comunicacao": 4, "criatividade": 2, "detalhismo": 3, "pressao": 3, "curiosidade": 2, "organizacao": 4},
            {"matematica": 3, "logica": 3, "design": 1, "web": 2, "apis": 3, "banco_dados": 3, "redes_linux": 4,
             "seguranca_info": 3, "automacao": 3, "mobile": 1, "nuvem": 5, "testes": 2},
            {"obj_previsoes": 1, "obj_pipelines": 2, "obj_interface": 1, "obj_sistemas": 2, "obj_protecao": 2,
             "obj_disponibilidade": 2, "obj_escala": 5, "obj_apps": 1, "obj_qualidade": 2, "obj_estrategia": 3},
        ),
        "cloud", {"fundamentos_cloud": 2, "redes_cloud": 1, "custos": 1},
    ),
    Persona(
        "marcos", "Marcos, criador de apps",
        "Vive no celular e quer publicar aplicativos nas lojas.",
        _respostas(
            {"comunicacao": 3, "criatividade": 4, "detalhismo": 3, "pressao": 2, "curiosidade": 2, "organizacao": 3},
            {"matematica": 2, "logica": 3, "design": 4, "web": 2, "apis": 3, "banco_dados": 2, "redes_linux": 1,
             "seguranca_info": 1, "automacao": 2, "mobile": 5, "nuvem": 2, "testes": 2},
            {"obj_previsoes": 1, "obj_pipelines": 1, "obj_interface": 4, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 1, "obj_apps": 5, "obj_qualidade": 3, "obj_estrategia": 2},
        ),
        "mobile", {"linguagem_mobile": 2, "git": 2, "ux_mobile": 1},
    ),
    Persona(
        "larissa", "Larissa, caçadora de bugs",
        "Detalhista ao extremo, gosta de testes e automação; quer software sem falhas.",
        _respostas(
            {"comunicacao": 3, "criatividade": 2, "detalhismo": 5, "pressao": 3, "curiosidade": 4, "organizacao": 4},
            {"matematica": 2, "logica": 3, "design": 2, "web": 3, "apis": 3, "banco_dados": 2, "redes_linux": 2,
             "seguranca_info": 2, "automacao": 4, "mobile": 2, "nuvem": 2, "testes": 5},
            {"obj_previsoes": 1, "obj_pipelines": 1, "obj_interface": 2, "obj_sistemas": 2, "obj_protecao": 2,
             "obj_disponibilidade": 2, "obj_escala": 1, "obj_apps": 1, "obj_qualidade": 5, "obj_estrategia": 2},
        ),
        "qa", {"fundamentos_teste": 2, "gestao_bugs": 1, "testes_api": 1},
    ),
    Persona(
        "paula", "Paula, ponte entre negócio e tecnologia",
        "Comunicativa e organizada; quer definir a visão do produto.",
        _respostas(
            {"comunicacao": 5, "criatividade": 4, "detalhismo": 3, "pressao": 3, "curiosidade": 2, "organizacao": 5},
            {"matematica": 2, "logica": 2, "design": 3, "web": 2, "apis": 2, "banco_dados": 2, "redes_linux": 1,
             "seguranca_info": 1, "automacao": 2, "mobile": 2, "nuvem": 1, "testes": 2},
            {"obj_previsoes": 1, "obj_pipelines": 1, "obj_interface": 4, "obj_sistemas": 1, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 1, "obj_apps": 2, "obj_qualidade": 3, "obj_estrategia": 5},
        ),
        "produto", {"agil": 2, "discovery": 1, "prototipacao": 1},
    ),
]


AMBIGUAS = [
    PersonaAmbigua(
        "igor", "Igor, dados + web",
        "Gosta tanto de estatística e modelos preditivos quanto de design e desenvolvimento web.",
        _respostas(
            {"comunicacao": 3, "criatividade": 4, "detalhismo": 3, "pressao": 2, "curiosidade": 3, "organizacao": 3},
            {"matematica": 5, "logica": 5, "design": 5, "web": 5, "apis": 2, "banco_dados": 3, "redes_linux": 1,
             "seguranca_info": 1, "automacao": 2, "mobile": 1, "nuvem": 1, "testes": 2},
            {"obj_previsoes": 5, "obj_pipelines": 2, "obj_interface": 5, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 1, "obj_apps": 1, "obj_qualidade": 2, "obj_estrategia": 2},
        ),
        ("dados_ml", "frontend"), True,
        "Empate parcial entre Ciência de Dados e Front-end, as duas no Top 3.",
    ),
    PersonaAmbigua(
        "otavio", "Otávio, DevOps × Cloud",
        "Automatiza tudo, ama nuvem e quer tanto manter sistemas no ar quanto desenhar a arquitetura.",
        _respostas(
            {"comunicacao": 3, "criatividade": 2, "detalhismo": 3, "pressao": 4, "curiosidade": 2, "organizacao": 3},
            {"matematica": 2, "logica": 3, "design": 1, "web": 2, "apis": 3, "banco_dados": 2, "redes_linux": 4,
             "seguranca_info": 2, "automacao": 5, "mobile": 1, "nuvem": 5, "testes": 2},
            {"obj_previsoes": 1, "obj_pipelines": 2, "obj_interface": 1, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 4, "obj_escala": 4, "obj_apps": 1, "obj_qualidade": 2, "obj_estrategia": 1},
        ),
        ("devops", "cloud"), True,
        "Empate parcial entre DevOps e Cloud; P08/P10 disparam fraco e por igual, pois os dois objetivos são altos.",
    ),
    PersonaAmbigua(
        "beatriz", "Beatriz, Front-end × Mobile",
        "Criativa, gosta de design, web e celulares; quer construir interfaces e publicar apps.",
        _respostas(
            {"comunicacao": 3, "criatividade": 4, "detalhismo": 3, "pressao": 2, "curiosidade": 2, "organizacao": 3},
            {"matematica": 2, "logica": 3, "design": 4, "web": 4, "apis": 2, "banco_dados": 2, "redes_linux": 1,
             "seguranca_info": 1, "automacao": 2, "mobile": 4, "nuvem": 1, "testes": 2},
            {"obj_previsoes": 1, "obj_pipelines": 1, "obj_interface": 5, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 1, "obj_apps": 4, "obj_qualidade": 2, "obj_estrategia": 2},
        ),
        ("frontend", "mobile"), True,
        "Empate parcial entre Front-end e Mobile, as duas no Top 3.",
    ),
    PersonaAmbigua(
        "renato", "Renato, Ciência × Engenharia de Dados",
        "Gosta de matemática e de bancos de dados; quer tanto modelos preditivos quanto pipelines confiáveis.",
        _respostas(
            {"comunicacao": 2, "criatividade": 2, "detalhismo": 4, "pressao": 3, "curiosidade": 3, "organizacao": 3},
            {"matematica": 4, "logica": 4, "design": 1, "web": 1, "apis": 2, "banco_dados": 4, "redes_linux": 2,
             "seguranca_info": 1, "automacao": 3, "mobile": 1, "nuvem": 3, "testes": 2},
            {"obj_previsoes": 4, "obj_pipelines": 4, "obj_interface": 1, "obj_sistemas": 2, "obj_protecao": 1,
             "obj_disponibilidade": 1, "obj_escala": 2, "obj_apps": 1, "obj_qualidade": 2, "obj_estrategia": 1},
        ),
        ("dados_ml", "eng_dados"), True,
        "Empate parcial entre Ciência de Dados e Engenharia de Dados, as duas no Top 3.",
    ),
    PersonaAmbigua(
        "neutro", "Indeciso (tudo 3)",
        "Respondeu 3 (afinidade moderada) em todas as perguntas.",
        _uniforme(3), (), True,
        "Certeza 0% e empate parcial; o ranking fica definido só pelas penalidades e pela ordem da base.",
    ),
    PersonaAmbigua(
        "tudo5", "Entusiasta de tudo (tudo 5)",
        "Respondeu 5 (total afinidade) em todas as perguntas.",
        _uniforme(5), (), True,
        "Todas as trilhas em 100%, certeza 100% e empate parcial; desempate por regras fortes e ordem da base.",
    ),
    PersonaAmbigua(
        "tudo1", "Sem afinidade (tudo 1)",
        "Respondeu 1 (nenhuma afinidade) em todas as perguntas.",
        _uniforme(1), (), True,
        "Todas as trilhas em 0% (as penalidades não deixam negativo) e empate parcial, sem quebrar o motor.",
    ),
]


def avaliar_personas(base=None) -> list:
    """Roda as personas típicas e devolve uma linha (dict) por persona: esperado × obtido."""
    motor = MotorInferencia(base)
    nomes = {t: info["nome"] for t, info in motor.base["trilhas"].items()}
    linhas = []
    for p in PERSONAS:
        r = motor.inferir(p.respostas)
        esperada = next(c for c in r.ranking if c.trilha == p.esperada)
        linhas.append({
            "Persona": p.nome,
            "Esperada": nomes[p.esperada],
            "Obtida (1ª)": r.vencedora.nome,
            "% obtida": r.vencedora.percentual,
            "% esperada": esperada.percentual,
            "2ª colocada": r.ranking[1].nome,
            "Margem (p.p.)": r.margem,
            "Acertou": r.vencedora.trilha == p.esperada,
        })
    return linhas


def avaliar_ambiguas(base=None) -> list:
    """Roda os perfis ambíguos e casos limite e confere o comportamento esperado."""
    motor = MotorInferencia(base)
    linhas = []
    for p in AMBIGUAS:
        r = motor.inferir(p.respostas)
        top = [c.trilha for c in r.top3]
        ok = r.empate_parcial == p.empate_parcial and all(t in top for t in p.em_disputa)
        linhas.append({
            "Persona": p.nome,
            "Top 3": " · ".join(f"{c.nome} ({c.percentual}%)" for c in r.top3),
            "Margem (p.p.)": r.margem,
            "Certeza": r.certeza,
            "Empate parcial": r.empate_parcial,
            "Esperado": p.comportamento,
            "Conforme": ok,
        })
    return linhas
