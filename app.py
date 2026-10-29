"""Interface web em etapas (wizard) do Consultor Avançado de Carreiras em TI.

Executar:  streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from consultor import analisar_gaps, carregar_base, diagnosticar, gerar_roadmap
from consultor.base import termos
from consultor.personas import AMBIGUAS, avaliar_ambiguas, avaliar_personas

st.set_page_config(page_title="Consultor de Carreiras em TI", page_icon="🧭", layout="wide")

EXPERIENCIAS = [
    "Nenhuma (começando do zero)",
    "Estudante de TI",
    "Estágio ou primeiro emprego em TI",
    "Já trabalho em TI e quero mudar de área",
]
PASSOS = {1: "perfil", 2: "afinidades", 3: "objetivos"}
TOTAL_PASSOS = 4


@st.cache_resource
def obter_base() -> dict:
    return carregar_base()


BASE = obter_base()
ETAPAS = {e["id"]: e for e in BASE["etapas"]}
ROTULOS = {int(k): v for k, v in BASE["escala"]["rotulos"].items()}
ROTULOS_CONHECIMENTO = {int(k): v for k, v in BASE["escala_conhecimento"]["rotulos"].items()}

estado = st.session_state
estado.setdefault("passo", 1)
estado.setdefault("respostas", {})
estado.setdefault("perfil", {"nome": "", "experiencia": EXPERIENCIAS[0], "horas": 10})


# --- Navegação -------------------------------------------------------------

def salvar_passo() -> None:
    """Copia os valores dos widgets do passo atual para o estado permanente."""
    if estado.passo == 1:
        for campo in ("nome", "experiencia", "horas"):
            if campo in estado:
                estado.perfil[campo] = estado[campo]
    etapa = PASSOS.get(estado.passo)
    for p in BASE["perguntas"]:
        if p["etapa"] == etapa and f"q_{p['id']}" in estado:
            estado.respostas[p["id"]] = estado[f"q_{p['id']}"]


def avancar() -> None:
    salvar_passo()
    estado.passo = min(estado.passo + 1, TOTAL_PASSOS)


def voltar() -> None:
    salvar_passo()
    estado.passo = max(estado.passo - 1, 1)


def recomecar() -> None:
    for chave in list(estado.keys()):
        del estado[chave]


# --- Componentes -----------------------------------------------------------

def perguntas_likert(etapa: str) -> None:
    for p in BASE["perguntas"]:
        if p["etapa"] == etapa:
            st.select_slider(
                p["texto"], options=list(ROTULOS), key=f"q_{p['id']}",
                value=estado.respostas.get(p["id"], 3),
                format_func=lambda v: f"{v} · {ROTULOS[v]}",
            )


def botoes_navegacao(pode_avancar: bool = True) -> None:
    esquerda, _, direita = st.columns([1, 3, 1])
    if estado.passo > 1:
        esquerda.button("⬅️ Voltar", on_click=voltar, width="stretch")
    if estado.passo < TOTAL_PASSOS:
        rotulo = "Ver resultado ✅" if estado.passo == TOTAL_PASSOS - 1 else "Avançar ➡️"
        direita.button(rotulo, on_click=avancar, type="primary", disabled=not pode_avancar, width="stretch")


def grafico_radar(resultado) -> go.Figure:
    ranking = sorted(resultado.ranking, key=lambda c: list(BASE["trilhas"]).index(c.trilha))
    nomes = [f"{c.icone} {c.nome.split(' (')[0]}" for c in ranking]
    valores = [c.percentual for c in ranking]
    fig = go.Figure(go.Scatterpolar(r=valores + valores[:1], theta=nomes + nomes[:1], fill="toself",
                                    name="Aderência", hovertemplate="%{theta}: %{r}%<extra></extra>"))
    fig.update_layout(polar={"radialaxis": {"range": [0, 100], "ticksuffix": "%"}},
                      showlegend=False, margin={"l": 60, "r": 60, "t": 30, "b": 30}, height=460)
    return fig


def grafico_barras(resultado) -> go.Figure:
    ranking = list(reversed(resultado.ranking))
    top = {c.trilha for c in resultado.top3}
    fig = go.Figure(go.Bar(
        x=[c.percentual for c in ranking], y=[f"{c.icone} {c.nome}" for c in ranking], orientation="h",
        marker_color=["#2563eb" if c.trilha in top else "#94a3b8" for c in ranking],
        text=[f"{c.percentual}%" for c in ranking], textposition="outside",
        hovertemplate="%{y}: %{x}%<extra></extra>",
    ))
    fig.update_layout(xaxis={"range": [0, 110], "ticksuffix": "%"}, margin={"l": 10, "r": 10, "t": 30, "b": 30},
                      height=460)
    return fig


def grafico_gaps(gaps: list) -> go.Figure:
    nomes = [g.nome for g in gaps]
    fig = go.Figure([
        go.Bar(name="Seu nível atual", x=nomes, y=[g.atual for g in gaps], marker_color="#2563eb"),
        go.Bar(name="Nível Júnior", x=nomes, y=[g.junior for g in gaps], marker_color="#f59e0b"),
    ])
    fig.update_layout(barmode="group", height=380, margin={"l": 10, "r": 10, "t": 30, "b": 10},
                      yaxis={"range": [0, 3.2], "tickvals": list(ROTULOS_CONHECIMENTO),
                             "ticktext": list(ROTULOS_CONHECIMENTO.values())},
                      legend={"orientation": "h", "y": 1.15})
    return fig


def plano_markdown(nome: str, plano) -> str:
    linhas = [f"# Plano de ação — {plano.nome}", "",
              f"**{nome or 'Visitante'}**, sua prontidão para o nível Júnior é de **{plano.prontidao}%**.", ""]
    if plano.etapas:
        linhas += [f"Estimativa: **{plano.semanas_total} semanas** ({plano.horas_total:.0f} h a "
                   f"{plano.horas_semana} h/semana).", "", "## O que estudar primeiro", ""]
        for e in plano.etapas:
            linhas.append(f"{e.ordem}. **{e.gap.nome}** (semanas {e.semana_inicio}–{e.semana_fim}): "
                          f"{ROTULOS_CONHECIMENTO[e.gap.atual]} → {ROTULOS_CONHECIMENTO[e.gap.junior]}. "
                          f"Tecnologias: {', '.join(e.gap.tecnologias)}.")
    else:
        linhas.append("Você já atinge o nível Júnior em todas as competências da trilha.")
    linhas += ["", "## Certificações", ""]
    linhas += [f"- {c['nome']} ({c['emissor']}, {c['nivel_entrada']})" for c in plano.certificacoes]
    linhas += [f"- Depois: {c['nome']} ({c['emissor']}, a partir de {c['prontidao_minima']}% de prontidão)"
               for c in plano.certificacoes_futuras]
    linhas += ["", "## Projetos para o portfólio no GitHub", ""]
    linhas += [f"- **{p['titulo']}**: {p['descricao']}" for p in plano.projetos]
    return "\n".join(linhas) + "\n"


# --- Passos ----------------------------------------------------------------

def cabecalho() -> None:
    titulos = [ETAPAS[PASSOS[i]]["titulo"] for i in (1, 2, 3)] + ["Resultado"]
    st.progress(estado.passo / TOTAL_PASSOS, text=f"Passo {estado.passo} de {TOTAL_PASSOS}: {titulos[estado.passo - 1]}")


def passo_perfil() -> None:
    st.header("👤 Passo 1 · Perfil pessoal")
    st.caption(ETAPAS["perfil"]["descricao"])
    perfil = estado.perfil
    st.text_input("Seu nome", value=perfil["nome"], key="nome", max_chars=60)
    col1, col2 = st.columns(2)
    col1.selectbox("Experiência em TI", EXPERIENCIAS, index=EXPERIENCIAS.index(perfil["experiencia"]), key="experiencia")
    col2.slider("Horas por semana disponíveis para estudo", 1, 40, value=perfil["horas"], key="horas")
    st.subheader("Como você se descreve?")
    perguntas_likert("perfil")
    nome_ok = bool(estado.get("nome", "").strip())
    if not nome_ok:
        st.info("Informe seu nome para avançar.")
    botoes_navegacao(pode_avancar=nome_ok)


def passo_likert(numero: int, icone: str) -> None:
    etapa = ETAPAS[PASSOS[numero]]
    st.header(f"{icone} Passo {numero} · {etapa['titulo']}")
    st.caption(f"{etapa['descricao']} Use a escala de 1 (nenhuma afinidade) a 5 (total afinidade).")
    perguntas_likert(etapa["id"])
    botoes_navegacao()


def passo_resultado() -> None:
    perfil = estado.perfil
    faltando = [p["id"] for p in BASE["perguntas"] if p["id"] not in estado.respostas]
    if faltando:
        st.warning("Algumas respostas se perderam. Volte e revise os passos anteriores.")
        botoes_navegacao()
        return

    resultado = diagnosticar(estado.respostas, BASE)
    st.header(f"🎯 Resultado de {perfil['nome']}")
    st.caption(f"{perfil['experiencia']} · {perfil['horas']} h/semana para estudo")

    cols = st.columns(3)
    for i, (col, comp) in enumerate(zip(cols, resultado.top3)):
        delta = None if i == 0 else f"{comp.percentual - resultado.vencedora.percentual:.1f} p.p. da 1ª"
        col.metric(f"{i + 1}º · {comp.icone} {comp.nome}", f"{comp.percentual}%", delta=delta)

    certeza = int(resultado.certeza * 100)
    st.progress(resultado.certeza, text=f"Certeza do diagnóstico: {certeza}% (quão decididas foram suas respostas)")
    if resultado.empate_parcial:
        st.warning(f"⚖️ Empate parcial: {resultado.ranking[0].nome} e {resultado.ranking[1].nome} ficaram a apenas "
                   f"{resultado.margem} p.p. de distância. Vale explorar as duas trilhas.")
    if resultado.certeza < 0.3:
        st.info("Muitas respostas ficaram próximas do neutro (3); o resultado tem baixa certeza.")

    aba_radar, aba_barras = st.tabs(["🕸️ Radar", "📊 Barras"])
    aba_radar.plotly_chart(grafico_radar(resultado), width="stretch")
    aba_barras.plotly_chart(grafico_barras(resultado), width="stretch")

    vencedora = resultado.vencedora
    with st.expander(f"🔎 Por que {vencedora.nome}?", expanded=True):
        positivas = [e for e in vencedora.evidencias if e.pontos > 0]
        penalidades = [e for e in vencedora.evidencias if e.pontos < 0]
        st.markdown("**Regras que contribuíram:**")
        for e in positivas[:8]:
            st.markdown(f"- `{e.regra}` {e.descricao} — ativação {e.grau:.0%}, **+{e.pontos:.2f}** pts")
        if not positivas:
            st.markdown("- Nenhuma regra positiva disparou.")
        if penalidades:
            st.markdown("**Penalidades aplicadas:**")
            for e in penalidades:
                st.markdown(f"- `{e.regra}` {e.descricao} — ativação {e.grau:.0%}, **{e.pontos:.2f}** pts")

    st.divider()
    st.header("🗺️ Plano de carreira")
    opcoes = [c.trilha for c in resultado.top3]
    nomes = {c.trilha: f"{c.icone} {c.nome} ({c.percentual}%)" for c in resultado.top3}
    trilha = st.radio("Qual trilha do Top 3 você quer seguir?", opcoes, format_func=nomes.get,
                      horizontal=True, key="trilha_escolhida")

    st.subheader("Seu nível atual em cada competência")
    competencias = BASE["roadmaps"][trilha]["competencias"]
    conhecimento = {}
    cols = st.columns(2)
    for i, c in enumerate(competencias):
        conhecimento[c["id"]] = cols[i % 2].select_slider(
            c["nome"], options=list(ROTULOS_CONHECIMENTO), value=0, key=f"c_{trilha}_{c['id']}",
            format_func=lambda v: f"{v} · {ROTULOS_CONHECIMENTO[v]}",
            help=f"Tecnologias: {', '.join(c['tecnologias'])}. Júnior: {ROTULOS_CONHECIMENTO[c['nivel_junior']]}.",
        )

    gaps = analisar_gaps(trilha, conhecimento, BASE)
    plano = gerar_roadmap(trilha, gaps, perfil["horas"], BASE)

    st.subheader("📉 Análise de gaps")
    m1, m2, m3 = st.columns(3)
    m1.metric("Prontidão para Júnior", f"{plano.prontidao}%")
    m2.metric("Competências a desenvolver", len(plano.etapas))
    m3.metric("Duração estimada", f"{plano.semanas_total} semanas" if plano.etapas else "—")
    st.progress(plano.prontidao / 100)

    st.plotly_chart(grafico_gaps(gaps), width="stretch")
    tabela = pd.DataFrame([{
        "Competência": g.nome, "Atual": ROTULOS_CONHECIMENTO[g.atual], "Júnior": ROTULOS_CONHECIMENTO[g.junior],
        "Déficit": g.deficit, "Importância": g.importancia, "Prioridade": g.prioridade,
    } for g in gaps])
    st.dataframe(tabela, hide_index=True, width="stretch")

    st.subheader("🚀 Roadmap personalizado")
    if plano.etapas:
        st.markdown(f"Com **{plano.horas_semana} h/semana**, o plano leva cerca de **{plano.semanas_total} semanas** "
                    f"({plano.horas_total:.0f} h). Estude nesta ordem:")
        for e in plano.etapas:
            st.markdown(f"**{e.ordem}. {e.gap.nome}** · semanas {e.semana_inicio}–{e.semana_fim} · "
                        f"{ROTULOS_CONHECIMENTO[e.gap.atual]} → {ROTULOS_CONHECIMENTO[e.gap.junior]}  \n"
                        f"Tecnologias: {' · '.join(f'`{t}`' for t in e.gap.tecnologias)}")
    else:
        st.success("🎉 Você já atinge o nível Júnior em todas as competências desta trilha! "
                   "Foque no portfólio e nas certificações.")

    col_cert, col_proj = st.columns(2)
    with col_cert:
        st.markdown("#### 🏅 Certificações")
        for c in plano.certificacoes:
            st.markdown(f"- **{c['nome']}** ({c['emissor']}) · nível {c['nivel_entrada']}")
        for c in plano.certificacoes_futuras:
            st.markdown(f"- {c['nome']} ({c['emissor']}) · *quando atingir {c['prontidao_minima']}% de prontidão*")
    with col_proj:
        st.markdown("#### 💼 Projetos para o GitHub")
        for p in plano.projetos:
            cobre = f"  \n*Cobre: {', '.join(p['cobre'])}*" if p["cobre"] else ""
            st.markdown(f"- **{p['titulo']}**: {p['descricao']}{cobre}")

    st.download_button("⬇️ Baixar plano de ação (.md)", plano_markdown(perfil["nome"], plano),
                       file_name=f"plano_{trilha}.md", mime="text/markdown")
    st.divider()
    botoes_navegacao()


# --- Validação e base de conhecimento --------------------------------------

def aba_validacao() -> None:
    st.header("✅ Validação com personas (Fase 5)")
    st.caption("Perfis típicos de cada trilha e perfis ambíguos ou extremos, rodados no motor com a base atual. "
               "Os mesmos casos são verificados automaticamente em tests/test_personas.py.")

    personas = pd.DataFrame(avaliar_personas(BASE))
    acertos = int(personas["Acertou"].sum())
    ambiguas = avaliar_ambiguas(BASE)
    conformes = sum(linha["Conforme"] for linha in ambiguas)
    m1, m2, m3 = st.columns(3)
    m1.metric("Taxa de acerto (perfis típicos)", f"{100 * acertos / len(personas):.0f}%", f"{acertos} de {len(personas)}")
    m2.metric("Margem média sobre a 2ª colocada", f"{personas['Margem (p.p.)'].mean():.1f} p.p.")
    m3.metric("Casos ambíguos/limite conformes", f"{conformes} de {len(ambiguas)}")

    st.subheader("Esperado × obtido")
    st.dataframe(personas, hide_index=True, width="stretch",
                 column_config={"% obtida": st.column_config.NumberColumn(format="%.1f%%"),
                                "% esperada": st.column_config.NumberColumn(format="%.1f%%")})

    st.subheader("Perfis ambíguos e casos limite")
    for persona, linha in zip(AMBIGUAS, ambiguas):
        with st.expander(f"{'✅' if linha['Conforme'] else '❌'} {persona.nome}", expanded=bool(persona.em_disputa)):
            st.markdown(f"*{persona.descricao}*  \n**Esperado:** {persona.comportamento}")
            st.markdown(f"**Top 3:** {linha['Top 3']}  \n"
                        f"Margem entre 1ª e 2ª: {linha['Margem (p.p.)']} p.p. · certeza {linha['Certeza']:.0%}")
            if linha["Empate parcial"]:
                st.warning("⚖️ Empate parcial sinalizado: as primeiras colocadas ficaram a menos de "
                           f"{BASE['parametros']['limiar_empate']} p.p. de distância.")
            else:
                st.info("Sem empate parcial.")


def aba_base() -> None:
    st.header("📚 Base de conhecimento")
    st.caption(f"Conteúdo de consultor/regras_carreiras.json (versão {BASE.get('versao', '—')}). "
               "Alterar regras e pesos no arquivo muda o diagnóstico sem tocar no código.")
    trilhas = BASE["trilhas"]
    regras = pd.DataFrame([{
        "ID": r["id"], "Trilha": f"{trilhas[r['trilha']]['icone']} {trilhas[r['trilha']]['nome']}",
        "Tipo": r["tipo"], "Peso": r["peso"],
        "Condição": (" E " if "todas" in r["condicao"] else " OU ").join(termos(r)),
        "Descrição": r["descricao"],
    } for r in BASE["regras"]])

    m1, m2, m3 = st.columns(3)
    m1.metric("Trilhas", len(trilhas))
    m2.metric("Perguntas", len(BASE["perguntas"]))
    m3.metric("Regras", len(regras), f"{(regras['Tipo'] == 'penalidade').sum()} penalidades", delta_color="off")

    col1, col2 = st.columns(2)
    filtro_trilha = col1.multiselect("Filtrar por trilha", sorted(regras["Trilha"].unique()))
    filtro_tipo = col2.multiselect("Filtrar por tipo", ["afinidade", "combinada", "penalidade"])
    if filtro_trilha:
        regras = regras[regras["Trilha"].isin(filtro_trilha)]
    if filtro_tipo:
        regras = regras[regras["Tipo"].isin(filtro_tipo)]
    st.dataframe(regras, hide_index=True, width="stretch")
    st.caption("Na condição, `!x` significa baixa afinidade com x (grau = 1 − intensidade de x).")

    with st.expander("Perguntas por etapa"):
        st.dataframe(pd.DataFrame([{"Etapa": ETAPAS[p["etapa"]]["titulo"], "ID": p["id"], "Pergunta": p["texto"]}
                                   for p in BASE["perguntas"]]), hide_index=True, width="stretch")


# --- Página ----------------------------------------------------------------

st.title("🧭 Consultor Avançado de Carreiras em TI")
aba_consultor, aba_val, aba_conhecimento = st.tabs(["🧭 Consultor", "✅ Validação", "📚 Base de conhecimento"])
with aba_consultor:
    cabecalho()
    if estado.passo == 1:
        passo_perfil()
    elif estado.passo == 2:
        passo_likert(2, "🛠️")
    elif estado.passo == 3:
        passo_likert(3, "🎯")
    else:
        passo_resultado()
with aba_val:
    aba_validacao()
with aba_conhecimento:
    aba_base()

with st.sidebar:
    st.markdown("### Etapas")
    for i, titulo in enumerate(["Perfil pessoal", "Afinidades técnicas", "Objetivos de carreira", "Resultado"], start=1):
        marcador = "✅" if i < estado.passo else ("👉" if i == estado.passo else "⬜")
        st.markdown(f"{marcador} {titulo}")
    st.button("🔄 Recomeçar", on_click=recomecar, width="stretch")
