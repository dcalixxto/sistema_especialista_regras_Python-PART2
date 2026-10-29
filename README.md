# 🧭 Consultor Avançado de Carreiras em TI (Etapa 2)

Sistema Especialista baseado em regras com **tratamento de incerteza** e **pontuação ponderada**, escrito em Python. Ele analisa respostas graduais (escala Likert de 1 a 5), calcula a compatibilidade percentual com **10 trilhas de carreira em TI** e explica quais regras levaram a cada resultado.

> Trabalho da disciplina de Inteligência Artificial, curso de Ciência da Computação, UNIPAC Barbacena.

## Andamento

- [x] Fase 1: engenharia do conhecimento e modelagem em JSON
- [x] Fase 2: motor de inferência com pontuação ponderada
- [x] Fase 3: análise de gaps e roadmap
- [x] Fase 4: interface web em etapas (Streamlit)
- [x] Fase 5: testes de robustez e casos limite (personas, perfis ambíguos e documentação final)

## Arquitetura

```
               ┌──────────────────────────────────────────────┐
               │  consultor/regras_carreiras.json             │
               │  Base de conhecimento: etapas, 28 perguntas, │
               │  10 trilhas, 63 regras ponderadas, roadmaps  │
               └──────────────────────┬───────────────────────┘
                                      │ carregar_base() + validar_base()
                                      ▼
┌───────────────┐  respostas   ┌──────────────────────┐  ranking, Top 3,   ┌──────────────────────┐
│  app.py       │  Likert 1–5  │  consultor/motor.py  │  certeza, empate,  │  consultor/          │
│  Streamlit    ├─────────────►│  Motor de inferência ├───────────────────►│  roadmap.py          │
│  (wizard em   │              │  (grau difuso ×      │  trilha escolhida  │  Gaps, prontidão,    │
│  4 passos +   │◄─────────────┤  peso, penalidades)  │  + conhecimento    │  roadmap, certific., │
│  Validação +  │  resultado e │                      │                    │  projetos            │
│  Base)        │  plano       └──────────▲───────────┘                    └──────────┬───────────┘
└──────▲────────┘                         │                                           │
       │                       ┌──────────┴───────────┐                               │
       │  aba Validação        │ consultor/personas.py│                               │
       └───────────────────────┤ 10 personas típicas  │◄──── tests/ (pytest) ─────────┘
                               │ + 7 ambíguas/limite  │
                               └──────────────────────┘
```

O conhecimento (perguntas, regras, pesos, competências) fica só no JSON; o motor e o roadmap são genéricos
e funcionam com qualquer base válida. A engenharia do conhecimento está documentada em
[docs/matriz_decisao.md](docs/matriz_decisao.md).

## Estrutura de pastas

```
├── app.py                      # interface Streamlit (wizard + Validação + Base de conhecimento)
├── consultor/
│   ├── __init__.py             # API pública do pacote
│   ├── regras_carreiras.json   # base de conhecimento (desacoplada do código)
│   ├── base.py                 # carregamento e validação da base
│   ├── motor.py                # motor de inferência ponderado com incerteza
│   ├── roadmap.py              # análise de gaps e roadmap para o nível Júnior
│   └── personas.py             # personas de validação (Fase 5)
├── docs/
│   └── matriz_decisao.md       # matriz pergunta × trilha, fórmulas e resultados dos testes
├── tests/
│   ├── test_motor.py           # Fases 1 e 2
│   ├── test_roadmap.py         # Fase 3
│   └── test_personas.py        # Fase 5: personas, ambíguos e casos limite
├── conftest.py
└── requirements.txt
```

## Instalação

Requer **Python 3.10 ou superior**.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

## Como usar a interface web

```bash
streamlit run app.py
```

O navegador abre em `http://localhost:8501` com um assistente em 4 passos:

1. **Perfil pessoal**: nome, experiência em TI, horas por semana para estudo e perguntas sobre seu jeito de trabalhar.
2. **Afinidades técnicas**: quanto você gosta de cada área (escala de 1 a 5).
3. **Objetivos de carreira**: que tipo de resultado você quer entregar.
4. **Resultado**: Top 3 com % de aderência, gráficos de radar e de barras das 10 trilhas, certeza do diagnóstico, aviso de empate parcial e as regras que justificam a trilha vencedora. Em seguida você escolhe uma trilha do Top 3, informa seu nível atual em cada competência e recebe a análise de gaps e o roadmap, que também pode ser baixado em Markdown.

Os botões **Voltar** e **Avançar** navegam entre os passos sem perder as respostas; **Recomeçar** (na barra lateral) limpa tudo.

Além do assistente, a página tem duas abas:

- **✅ Validação**: roda as personas no motor e mostra a tabela esperado × obtido com os percentuais, a taxa de acerto e os casos ambíguos e limite com o aviso de empate parcial.
- **📚 Base de conhecimento**: lista as regras do JSON (ID, trilha, tipo, peso, condição e descrição), com filtros por trilha e por tipo, e as perguntas de cada etapa.

### Exemplo de saída (persona Diego, perfil DevOps)

```
1º ⚙️ DevOps & SRE ............. 100.0%
2º ☁️ Cloud Architecture ........ 52.5%
3º 🛢️ Engenharia de Dados ....... 45.0%
Certeza do diagnóstico: 48%

Por que DevOps & SRE?
- R26 SE gosta de automação ENTÃO DevOps — ativação 100%, +3.00 pts
- R27 SE quer manter sistemas no ar e acelerar entregas ENTÃO DevOps/SRE — ativação 100%, +3.00 pts
- R28 SE gosta de redes e Linux ENTÃO DevOps — ativação 100%, +2.00 pts
- R30 SE automação E infraestrutura ENTÃO perfil DevOps — ativação 100%, +2.00 pts
- R29 SE lida bem com incidentes ENTÃO SRE — ativação 100%, +1.00 pts
```

Um perfil ambíguo, como alguém que gosta tanto de dados quanto de web, recebe o aviso de empate:

```
1º 🎨 Desenvolvimento Front-end & UI/UX ...... 97.7%
2º 🧠 Ciência de Dados e Machine Learning .... 95.0%
3º 🧩 Desenvolvimento Back-end ............... 40.9%
⚖️ Empate parcial: as duas primeiras ficaram a apenas 2.7 p.p. de distância. Vale explorar as duas trilhas.
```

## Base de conhecimento ([consultor/regras_carreiras.json](consultor/regras_carreiras.json))

O conhecimento fica fora do código Python, num arquivo JSON carregado e validado em tempo de execução:

- `etapas`: Perfil pessoal, Afinidades técnicas e Objetivos de carreira.
- `perguntas`: 28 afirmações respondidas de 1 (nenhuma afinidade) a 5 (total afinidade).
- `trilhas`: as 10 trilhas.
- `regras`: 63 regras SE-ENTÃO com peso. Os tipos são `afinidade` (uma pergunta), `combinada` (várias perguntas ligadas por E) e `penalidade` (peso negativo, para perfis conflitantes).
- `parametros`: limiar de empate parcial, limiar de regra forte e horas de estudo por nível de competência.
- `escala_conhecimento`: 0 (nenhum), 1 (básico), 2 (intermediário) e 3 (avançado).
- `roadmaps`: para cada trilha, de 4 a 6 `competencias` (nível exigido de um Júnior, importância de 1 a 3 e tecnologias), de 2 a 3 `certificacoes` (nível de entrada e prontidão mínima recomendada) e 3 `projetos_portfolio` ligados às competências que exercitam.

## Motor de inferência ([consultor/motor.py](consultor/motor.py))

1. Cada resposta vira uma intensidade entre 0 e 1 (1 → 0,0; 3 → 0,5; 5 → 1,0).
2. Grau de ativação da regra: `todas` usa o mínimo dos termos (E lógico) e `alguma` usa o máximo (OU lógico). O termo `!x` vale `1 − x`, ou seja, baixa afinidade com `x`.
3. Pontos da regra = peso × grau. As penalidades subtraem pontos (ex.: quer criar modelos preditivos mas não gosta de matemática → Ciência de Dados perde pontos).
4. Compatibilidade da trilha = pontos ÷ soma dos pesos positivos da trilha, entre 0% e 100%.
5. O ranking é ordenado por percentual. Em caso de empate, vence quem tem mais regras decisivas fortes e depois quem vem antes na base. O resultado traz o Top 3, a **certeza** (quão longe do neutro foram as respostas) e um aviso de **empate parcial** quando a 1ª e a 2ª colocadas ficam a menos de 5 pontos percentuais.

```python
from consultor import diagnosticar

resultado = diagnosticar({"matematica": 5, "obj_previsoes": 5, ...})  # todas as 28 perguntas
for c in resultado.top3:
    print(c.nome, f"{c.percentual}%")
```

## Análise de gaps e roadmap ([consultor/roadmap.py](consultor/roadmap.py))

1. O usuário informa o nível atual (0 a 3) em cada competência da trilha escolhida; competências omitidas contam como 0.
2. **Gap**: déficit = nível Júnior − nível atual (nunca negativo) e prioridade = déficit × importância. `analisar_gaps` devolve todas as competências ordenadas da maior para a menor prioridade.
3. **Prontidão para Júnior (%)** = níveis já atingidos ÷ níveis exigidos, ponderados pela importância (0% sem nenhum conhecimento, 100% quando todas as competências chegam ao nível Júnior).
4. **Roadmap** (`gerar_roadmap`): estuda primeiro as competências de maior prioridade, cada nível de déficit custa `horas_por_nivel` horas (30 na base) e as semanas são estimadas a partir das horas semanais disponíveis. As certificações são separadas entre recomendadas agora (prontidão mínima já atingida) e para depois, e os projetos de portfólio são ordenados pelos gaps que cobrem.

```python
from consultor import planejar

plano = planejar("dados_ml", {"python_dados": 2, "estatistica": 1}, horas_semana=10)
print(plano.prontidao, plano.semanas_total)
for etapa in plano.etapas:
    print(etapa.ordem, etapa.gap.nome, etapa.gap.tecnologias)
```

## Testes de robustez (Fase 5) ([consultor/personas.py](consultor/personas.py))

- **10 personas típicas**, uma por trilha, com as 28 respostas e o conhecimento atual: todas recebem a trilha esperada em 1º lugar (**taxa de acerto de 100%**, com margem média de 51 p.p. sobre a 2ª colocada), e a vencedora não muda quando qualquer resposta é alterada em ±1.
- **4 perfis ambíguos** (dados + web, DevOps × Cloud, Front-end × Mobile, Ciência × Engenharia de Dados): todos sinalizam empate parcial, as duas trilhas em disputa ocupam o 1º e o 2º lugar e cada uma é justificada por regras fortes dela própria.
- **3 casos limite** (tudo 1, tudo 3, tudo 5): o motor e o roadmap funcionam, a compatibilidade fica entre 0% e 100% e o desempate é determinístico.
- **Penalidades** separam os pares parecidos: com elas, a margem entre a trilha certa e a "gêmea" é maior do que numa base sem penalidades.
- O **roadmap** de cada persona nunca sugere competências que ela já domina.

A tabela completa dos resultados está em [docs/matriz_decisao.md](docs/matriz_decisao.md#7-testes-de-robustez-fase-5).

## Testes

```bash
python -m pytest -v
```

São 131 testes: `tests/test_motor.py` (base e motor, 18), `tests/test_roadmap.py` (gaps e roadmap, 51) e `tests/test_personas.py` (personas, perfis ambíguos e casos limite, 62).
