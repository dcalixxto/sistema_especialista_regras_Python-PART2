# 🧭 Consultor Avançado de Carreiras em TI (Etapa 2)

Sistema Especialista baseado em regras com **tratamento de incerteza** e **pontuação ponderada**, escrito em Python. Ele analisa respostas graduais (escala Likert de 1 a 5), calcula a compatibilidade percentual com **10 trilhas de carreira em TI** e explica quais regras levaram a cada resultado.

> Trabalho da disciplina de Inteligência Artificial, curso de Ciência da Computação, UNIPAC Barbacena.

## Andamento

- [x] Fase 1: engenharia do conhecimento e modelagem em JSON
- [x] Fase 2: motor de inferência com pontuação ponderada
- [ ] Fase 3: análise de gaps e roadmap
- [ ] Fase 4: interface web em etapas (Streamlit)
- [ ] Fase 5: testes de robustez e casos limite

## Instalação

Requer **Python 3.10 ou superior**.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

## Base de conhecimento ([consultor/regras_carreiras.json](consultor/regras_carreiras.json))

O conhecimento fica fora do código Python, num arquivo JSON carregado e validado em tempo de execução:

- `etapas`: Perfil pessoal, Afinidades técnicas e Objetivos de carreira.
- `perguntas`: 28 afirmações respondidas de 1 (nenhuma afinidade) a 5 (total afinidade).
- `trilhas`: as 10 trilhas.
- `regras`: 63 regras SE-ENTÃO com peso. Os tipos são `afinidade` (uma pergunta), `combinada` (várias perguntas ligadas por E) e `penalidade` (peso negativo, para perfis conflitantes).
- `parametros`: limiar de empate parcial e limiar de regra forte.

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

## Testes

```bash
python -m pytest -v
```
