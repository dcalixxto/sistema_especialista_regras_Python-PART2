# 🧭 Consultor Avançado de Carreiras em TI (Etapa 2)

Sistema Especialista baseado em regras com **tratamento de incerteza** e **pontuação ponderada**, escrito em Python. Ele analisa respostas graduais (escala Likert de 1 a 5), calcula a compatibilidade percentual com **10 trilhas de carreira em TI** e explica quais regras levaram a cada resultado.

> Trabalho da disciplina de Inteligência Artificial, curso de Ciência da Computação, UNIPAC Barbacena.

## Andamento

- [x] Fase 1: engenharia do conhecimento e modelagem em JSON
- [x] Fase 2: motor de inferência com pontuação ponderada
- [x] Fase 3: análise de gaps e roadmap
- [x] Fase 4: interface web em etapas (Streamlit)
- [ ] Fase 5: testes de robustez e casos limite

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

## Testes

```bash
python -m pytest -v
```
