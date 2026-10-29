# Matriz de decisão e engenharia do conhecimento

Este documento descreve como o conhecimento do **Consultor Avançado de Carreiras em TI** foi modelado
em [`consultor/regras_carreiras.json`](../consultor/regras_carreiras.json), como o motor de inferência
transforma respostas graduais em compatibilidade percentual, como os gaps e o roadmap são calculados
e quais foram os resultados dos testes de robustez da Fase 5.

As tabelas abaixo foram geradas a partir da própria base de conhecimento e do motor, na versão atual do repositório.

## 1. Perguntas por etapa

O usuário responde a 28 afirmações na escala Likert de **1 (nenhuma afinidade) a 5 (total afinidade)**,
divididas nas três etapas do wizard.

**Perfil pessoal**

| ID | Pergunta |
|---|---|
| `comunicacao` | Gosto de apresentar ideias, negociar e lidar com clientes e equipes. |
| `criatividade` | Me considero uma pessoa criativa, com senso estético apurado. |
| `detalhismo` | Tenho paciência para revisar detalhes e encontrar pequenos erros. |
| `pressao` | Lido bem com incidentes e situações de pressão (ex.: sistema fora do ar). |
| `curiosidade` | Gosto de investigar como as coisas podem ser quebradas ou burladas. |
| `organizacao` | Gosto de organizar prioridades, planejar e acompanhar entregas. |

**Afinidades técnicas**

| ID | Pergunta |
|---|---|
| `matematica` | Matemática e estatística. |
| `logica` | Lógica de programação e algoritmos. |
| `design` | Design visual, layouts e experiência do usuário. |
| `web` | Desenvolvimento para navegadores (HTML, CSS, JavaScript). |
| `apis` | APIs, servidores de aplicação e regras de negócio. |
| `banco_dados` | Bancos de dados e SQL. |
| `redes_linux` | Infraestrutura: redes, Linux e sistemas operacionais. |
| `seguranca_info` | Segurança da informação e criptografia. |
| `automacao` | Automação de tarefas repetitivas (scripts, pipelines, CI/CD). |
| `mobile` | Dispositivos móveis (celulares e tablets). |
| `nuvem` | Plataformas de nuvem (AWS, Azure, GCP). |
| `testes` | Testes de software e caça a bugs. |

**Objetivos de carreira**

| ID | Pergunta |
|---|---|
| `obj_previsoes` | Criar modelos que descobrem padrões e fazem previsões (IA). |
| `obj_pipelines` | Garantir que os dados da empresa fluam e fiquem disponíveis de forma confiável. |
| `obj_interface` | Construir o produto que o usuário final vê e usa. |
| `obj_sistemas` | Construir a lógica e as APIs que fazem o sistema funcionar por trás. |
| `obj_protecao` | Proteger sistemas contra invasões e vazamentos. |
| `obj_disponibilidade` | Manter sistemas no ar e acelerar entregas com automação. |
| `obj_escala` | Desenhar infraestruturas escaláveis e otimizar custos na nuvem. |
| `obj_apps` | Publicar aplicativos nas lojas (Google Play / App Store). |
| `obj_qualidade` | Garantir que o software funcione sem falhas. |
| `obj_estrategia` | Definir a visão do produto e decidir o que deve ser construído. |

## 2. Matriz pergunta × trilha (regras de afinidade)

Cada célula é o **peso** da regra de afinidade simples `SE <pergunta> ENTÃO <trilha>`; `·` indica que a
pergunta não pontua aquela trilha diretamente. Peso 3 marca uma pergunta **central** da trilha, peso 2 um
traço **forte** e peso 1 um **indício secundário**. Toda trilha tem duas perguntas centrais (uma técnica
e um objetivo de carreira), o que evita que um único traço decida o resultado.

| | Abreviação |
|---|---|
| Back | Desenvolvimento Back-end |
| Front | Desenvolvimento Front-end & UI/UX |
| CD/ML | Ciência de Dados e Machine Learning |
| EngD | Engenharia de Dados |
| Seg | Cibersegurança |
| DevOps | DevOps & SRE |
| Cloud | Cloud Architecture |
| Mob | Desenvolvimento Mobile |
| QA | Engenharia de Qualidade e Testes |
| PM | Product Management |

| Pergunta | Back | Front | CD/ML | EngD | Seg | DevOps | Cloud | Mob | QA | PM |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `comunicacao` | · | · | · | · | · | · | 1 | · | · | 3 |
| `criatividade` | · | 1 | · | · | · | · | · | · | · | · |
| `detalhismo` | · | · | · | · | · | · | · | · | 2 | · |
| `pressao` | · | · | · | · | · | 1 | · | · | · | · |
| `curiosidade` | · | · | · | · | 2 | · | · | · | 1 | · |
| `organizacao` | · | · | · | · | · | · | · | · | · | 2 |
| `matematica` | · | · | 3 | · | · | · | · | · | · | · |
| `logica` | 2 | · | 1 | · | · | · | · | · | · | · |
| `design` | · | 3 | · | · | · | · | · | 1 | · | · |
| `web` | · | 3 | · | · | · | · | · | · | · | · |
| `apis` | 3 | · | · | · | · | · | · | · | · | · |
| `banco_dados` | 1 | · | 1 | 3 | · | · | · | · | · | · |
| `redes_linux` | · | · | · | · | 1 | 2 | 1 | · | · | · |
| `seguranca_info` | · | · | · | · | 3 | · | · | · | · | · |
| `automacao` | · | · | · | 1 | · | 3 | · | · | · | · |
| `mobile` | · | · | · | · | · | · | · | 3 | · | · |
| `nuvem` | · | · | · | 1 | · | · | 3 | · | · | · |
| `testes` | · | · | · | · | · | · | · | · | 3 | · |
| `obj_previsoes` | · | · | 3 | · | · | · | · | · | · | · |
| `obj_pipelines` | · | · | · | 3 | · | · | · | · | · | · |
| `obj_interface` | · | 2 | · | · | · | · | · | 1 | · | 1 |
| `obj_sistemas` | 3 | · | · | · | · | · | · | · | · | · |
| `obj_protecao` | · | · | · | · | 3 | · | · | · | · | · |
| `obj_disponibilidade` | · | · | · | · | · | 3 | · | · | · | · |
| `obj_escala` | · | · | · | · | · | · | 3 | · | · | · |
| `obj_apps` | · | · | · | · | · | · | · | 3 | · | · |
| `obj_qualidade` | · | · | · | · | · | · | · | · | 3 | · |
| `obj_estrategia` | · | · | · | · | · | · | · | · | · | 3 |

### Regras combinadas (E lógico)

Além das regras simples, cada trilha tem uma regra **combinada** que só ativa plenamente quando o
usuário tem os traços que, juntos, caracterizam o perfil. Ela reforça perfis coerentes e diferencia
quem gosta "um pouco de tudo" de quem tem o conjunto completo.

| ID | Trilha | Peso | Condição (E) |
|---|---|---:|---|
| R05 | Desenvolvimento Back-end | 2 | `logica` E `apis` E `banco_dados` |
| R10 | Desenvolvimento Front-end & UI/UX | 2 | `design` E `web` |
| R15 | Ciência de Dados e Machine Learning | 2 | `matematica` E `obj_previsoes` |
| R20 | Engenharia de Dados | 2 | `banco_dados` E `obj_pipelines` |
| R25 | Cibersegurança (Security / Pentesting) | 2 | `seguranca_info` E `redes_linux` |
| R30 | DevOps & SRE | 2 | `automacao` E `redes_linux` |
| R35 | Cloud Architecture | 2 | `nuvem` E `obj_escala` |
| R40 | Desenvolvimento Mobile | 2 | `mobile` E `obj_apps` |
| R45 | Engenharia de Qualidade e Testes (QA) | 2 | `testes` E `automacao` |
| R50 | Product Management | 2 | `comunicacao` E `obj_estrategia` |

### Pontuação máxima por trilha

A compatibilidade é normalizada pela soma dos pesos positivos da trilha, por isso trilhas com 10 ou 11
pontos possíveis são comparáveis entre si.

| Trilha | Soma dos pesos positivos |
|---|---:|
| Desenvolvimento Back-end | 11 |
| Desenvolvimento Front-end & UI/UX | 11 |
| Ciência de Dados e Machine Learning | 10 |
| Engenharia de Dados | 10 |
| Cibersegurança (Security / Pentesting) | 11 |
| DevOps & SRE | 11 |
| Cloud Architecture | 10 |
| Desenvolvimento Mobile | 10 |
| Engenharia de Qualidade e Testes (QA) | 11 |
| Product Management | 11 |

## 3. Penalidades e pares desambiguados

Penalidades têm peso negativo e retiram pontos quando o perfil **conflita** com a trilha. O termo `!x`
significa baixa afinidade com `x` (grau `1 − x`). Há dois grupos:

- **Penalidades de ausência** (P01, P06, P07, P09, P12, P13): a trilha exige um traço que o usuário não tem.
- **Penalidades de desempate entre trilhas parecidas** (P02/P11, P03, P04/P05, P08/P10): o usuário prefere
  claramente uma das trilhas "gêmeas", e a outra perde pontos.

| ID | Penaliza | Peso | Condição | Descrição |
|---|---|---:|---|---|
| P01 | Desenvolvimento Back-end | -2 | `!logica` E `!apis` | SE não gosta de lógica NEM de APIs ENTÃO penaliza Back-end |
| P02 | Desenvolvimento Front-end & UI/UX | -2 | `mobile` E `!web` | SE prefere mobile e não gosta de web ENTÃO penaliza Front-end (Front × Mobile) |
| P03 | Ciência de Dados e Machine Learning | -2 | `obj_previsoes` E `!matematica` | SE quer modelos preditivos mas não gosta de matemática ENTÃO penaliza Ciência de Dados |
| P04 | Ciência de Dados e Machine Learning | -2 | `obj_pipelines` E `!obj_previsoes` | SE prefere pipelines a modelos ENTÃO penaliza Ciência de Dados (Ciência × Engenharia) |
| P05 | Engenharia de Dados | -2 | `obj_previsoes` E `!obj_pipelines` | SE prefere modelos a pipelines ENTÃO penaliza Engenharia de Dados (Engenharia × Ciência) |
| P06 | Cibersegurança (Security / Pentesting) | -2 | `!seguranca_info` E `!obj_protecao` | SE não gosta de segurança NEM quer proteger sistemas ENTÃO penaliza Cibersegurança |
| P07 | DevOps & SRE | -2 | `!automacao` | SE não gosta de automação ENTÃO penaliza DevOps |
| P08 | DevOps & SRE | -1 | `obj_escala` E `!obj_disponibilidade` | SE prefere arquitetar a operar/automatizar ENTÃO penaliza DevOps (DevOps × Cloud) |
| P09 | Cloud Architecture | -2 | `!nuvem` | SE não gosta de nuvem ENTÃO penaliza Cloud |
| P10 | Cloud Architecture | -1 | `obj_disponibilidade` E `!obj_escala` | SE prefere operar/automatizar a arquitetar ENTÃO penaliza Cloud (Cloud × DevOps) |
| P11 | Desenvolvimento Mobile | -2 | `web` E `!mobile` | SE prefere web e não gosta de mobile ENTÃO penaliza Mobile (Mobile × Front) |
| P12 | Engenharia de Qualidade e Testes (QA) | -2 | `!detalhismo` | SE não tem paciência para detalhes ENTÃO penaliza QA |
| P13 | Product Management | -2 | `!comunicacao` | SE não gosta de lidar com pessoas ENTÃO penaliza Product Management |

| Par parecido | Penalidades | Como separam |
|---|---|---|
| Front-end × Mobile | P02, P11 | Quem gosta de web mas não de mobile perde pontos em Mobile (P11), e vice-versa (P02). Design e "produto que o usuário vê" pontuam as duas trilhas, então sem essas regras o par ficaria próximo. |
| Ciência de Dados × Engenharia de Dados | P04, P05 (e P03) | Quem prefere pipelines a modelos é penalizado em Ciência de Dados (P04) e quem prefere modelos a pipelines, em Engenharia de Dados (P05). P03 ainda tira pontos de quem quer modelos preditivos sem gostar de matemática. Bancos de dados pontuam as duas. |
| DevOps × Cloud | P08, P10 | Quem quer arquitetar (`obj_escala`) mais do que operar (`obj_disponibilidade`) perde pontos em DevOps (P08), e o contrário em Cloud (P10). Redes/Linux pontuam as duas. |

O teste `test_penalidade_separa_trilhas_parecidas` confirma, com as personas típicas, que cada uma dessas
penalidades **dispara** na trilha gêmea e que a margem entre a trilha certa e a gêmea é **maior com
penalidades do que numa cópia da base sem penalidades**.

## 4. Fórmulas do motor de inferência

**Intensidade da resposta** (escala Likert de 1 a 5 → [0, 1]):

```
x = (resposta − 1) / (5 − 1)        1 → 0,00 · 2 → 0,25 · 3 → 0,50 · 4 → 0,75 · 5 → 1,00
!x = 1 − x                          baixa afinidade com x
```

**Grau de ativação da regra** (lógica difusa, operadores de Zadeh):

```
condição "todas" (E):   grau = min(termos)
condição "alguma" (OU): grau = max(termos)
```

**Pontos da regra** = peso × grau (negativo nas penalidades).

**Compatibilidade da trilha**:

```
pontos(t)          = Σ peso(r) × grau(r)       para toda regra r da trilha t (inclui penalidades)
máximo(t)          = Σ peso(r)                 só regras com peso positivo
compatibilidade(t) = 100 × pontos(t) / máximo(t), limitada a [0 %, 100 %]
```

**Exemplo (persona Diego, DevOps)**: automação = 5, redes/Linux = 5, pressão = 5 e
`obj_disponibilidade` = 5 ativam R26, R27, R28, R29 e R30 com grau 1,0 → 11/11 = **100 %**. Em Cloud,
nuvem = 4 dá grau 0,75 em R31 (+2,25), `obj_escala` = 3 dá grau 0,5 em R32 (+1,5) e a penalidade P10
(operar mais do que arquitetar) tira 0,5. Com as demais regras, Cloud fica em 5,25/10 = **52,5 %**.

**Certeza do diagnóstico**: média de `|x − 0,5| × 2` sobre todas as respostas. Vale 0 % quando tudo é 3
(neutro) e 100 % quando tudo é 1 ou 5. Abaixo de 30 % a interface avisa que o resultado tem baixa certeza.

## 5. Critérios de desempate e de empate parcial

O ranking ordena as trilhas por:

1. **maior compatibilidade (%)**;
2. em caso de igualdade, **mais regras decisivas fortes**, isto é, regras de peso ≥ 3 com grau ≥ 0,75
   (`limiar_regra_forte`). Vence quem tem mais evidência central, não só indícios secundários;
3. persistindo a igualdade, a **ordem das trilhas na base**, o que deixa o resultado determinístico.

**Empate parcial**: quando a 1ª e a 2ª colocadas ficam a menos de `limiar_empate` = **5 pontos
percentuais**, o resultado é marcado com `empate_parcial = True` e a interface mostra o aviso
"⚖️ Empate parcial", recomendando explorar as duas trilhas. O Top 3 continua sendo exibido com os
percentuais e as justificativas de cada trilha.

## 6. Análise de gaps e roadmap

- Cada trilha tem de 4 a 6 **competências**, cada uma com nível exigido de um Júnior (1 a 3 na escala 0 nenhum,
  1 básico, 2 intermediário, 3 avançado), **importância** (1 a 3) e tecnologias.
- **Déficit** = max(0, júnior − atual); **prioridade** = déficit × importância. Competências omitidas contam como 0.
- **Prontidão para Júnior (%)** = Σ min(atual, júnior) × importância ÷ Σ júnior × importância.
- **Roadmap**: as competências com déficit são estudadas em ordem de prioridade. Cada nível de déficit custa
  `horas_por_nivel` = 30 h, e a janela de semanas sai das horas semanais informadas pelo usuário.
- **Certificações**: as que têm `prontidao_minima` ≤ prontidão atual são recomendadas agora e as demais ficam para depois.
- **Projetos de portfólio**: ordenados pela soma das prioridades dos gaps que cobrem. Sem gaps, todos são sugeridos.

Competências que o usuário já domina (atual ≥ júnior) **nunca** entram no roadmap. Isso é verificado para
cada persona em `test_roadmap_nao_sugere_competencias_dominadas`.

## 7. Testes de robustez (Fase 5)

As personas estão em [`consultor/personas.py`](../consultor/personas.py) e são verificadas em
[`tests/test_personas.py`](../tests/test_personas.py). Os mesmos resultados aparecem na aba **✅ Validação** da interface.

### 7.1 Perfis típicos: uma persona por trilha

Cada persona responde às 28 perguntas e informa seu nível atual em parte das competências da trilha.

| Persona | Esperada | Obtida (1ª) | % | 2ª colocada | Margem | OK |
|---|---|---|---:|---|---:|:-:|
| Bruno, construtor de APIs | Desenvolvimento Back-end | Desenvolvimento Back-end | 93.2% | Engenharia de Qualidade e Testes (QA) | 43.2 | ✅ |
| Fernanda, designer que programa | Desenvolvimento Front-end & UI/UX | Desenvolvimento Front-end & UI/UX | 100.0% | Product Management | 65.9 | ✅ |
| Daniela, analista com veia estatística | Ciência de Dados e Machine Learning | Ciência de Dados e Machine Learning | 95.0% | Desenvolvimento Back-end | 60.9 | ✅ |
| Eduardo, encanador de dados | Engenharia de Dados | Engenharia de Dados | 92.5% | Desenvolvimento Back-end | 38.0 | ✅ |
| Sofia, mentalidade hacker | Cibersegurança (Security / Pentesting) | Cibersegurança (Security / Pentesting) | 100.0% | Engenharia de Qualidade e Testes (QA) | 45.5 | ✅ |
| Diego, automatizador de plantão | DevOps & SRE | DevOps & SRE | 100.0% | Cloud Architecture | 47.5 | ✅ |
| Camila, arquiteta de nuvem | Cloud Architecture | Cloud Architecture | 95.0% | Product Management | 42.7 | ✅ |
| Marcos, criador de apps | Desenvolvimento Mobile | Desenvolvimento Mobile | 95.0% | Desenvolvimento Front-end & UI/UX | 56.4 | ✅ |
| Larissa, caçadora de bugs | Engenharia de Qualidade e Testes (QA) | Engenharia de Qualidade e Testes (QA) | 93.2% | DevOps & SRE | 56.8 | ✅ |
| Paula, ponte entre negócio e tecnologia | Product Management | Product Management | 97.7% | Desenvolvimento Front-end & UI/UX | 56.8 | ✅ |

**Taxa de acerto: 10 de 10 (100 %).** Além disso:

- **Estabilidade**: alterar qualquer uma das 28 respostas de qualquer persona em ±1 ponto não troca a
  trilha vencedora (`test_vencedora_resiste_a_mudanca_de_uma_resposta`, 462 variações).
- **Justificativas coerentes**: a vencedora de cada persona tem pelo menos uma evidência positiva forte
  (peso ≥ 3 e grau ≥ 0,75), a evidência de maior impacto é positiva e todas as regras citadas pertencem à
  própria trilha.
- **Roadmap** com o conhecimento de cada persona: prontidão entre 39 % e 64 %, de 3 a 4 competências a
  estudar e de 12 a 21 semanas a 10 h/semana, sem sugerir competências já dominadas.

### 7.2 Perfis ambíguos e casos limite

| Persona | Top 3 | Margem | Certeza | Empate parcial | OK |
|---|---|---:|---:|:-:|:-:|
| Igor, dados + web | Desenvolvimento Front-end & UI/UX (97.7%) · Ciência de Dados e Machine Learning (95.0%) · Desenvolvimento Back-end (40.9%) | 2.7 | 66% | sim | ✅ |
| Otávio, DevOps × Cloud | DevOps & SRE (79.5%) · Cloud Architecture (77.5%) · Engenharia de Dados (40.0%) | 2.0 | 57% | sim | ✅ |
| Beatriz, Front-end × Mobile | Desenvolvimento Front-end & UI/UX (75.0%) · Desenvolvimento Mobile (72.5%) · Product Management (34.1%) | 2.5 | 59% | sim | ✅ |
| Renato, Ciência × Engenharia de Dados | Ciência de Dados e Machine Learning (65.0%) · Engenharia de Dados (65.0%) · Desenvolvimento Back-end (34.1%) | 0.0 | 57% | sim | ✅ |
| Indeciso (tudo 3) | Desenvolvimento Back-end (40.9%) · Desenvolvimento Front-end & UI/UX (40.9%) · Cibersegurança (Security / Pentesting) (40.9%) | 0.0 | 0% | sim | ✅ |
| Entusiasta de tudo (tudo 5) | Desenvolvimento Back-end (100.0%) · Desenvolvimento Front-end & UI/UX (100.0%) · Ciência de Dados e Machine Learning (100.0%) | 0.0 | 100% | sim | ✅ |
| Sem afinidade (tudo 1) | Desenvolvimento Back-end (0.0%) · Desenvolvimento Front-end & UI/UX (0.0%) · Ciência de Dados e Machine Learning (0.0%) | 0.0 | 100% | sim | ✅ |

- **Igor (dados + web)**, o exemplo do enunciado: Front-end (97,7 %) e Ciência de Dados (95,0 %) ficam a
  2,7 p.p., o sistema sinaliza empate parcial e justifica as duas trilhas com regras próprias e fortes
  (R06, R07 e R10 para Front-end; R11, R12 e R15 para Ciência de Dados).
- **Renato (Ciência × Engenharia de Dados)** empata exatamente em 65 %. As duas têm 2 regras fortes, então
  vale a ordem da base. As penalidades P04 e P05 disparam com o mesmo grau (0,25) e não favorecem nenhum lado.
- **Otávio (DevOps × Cloud)** e **Beatriz (Front-end × Mobile)**: as penalidades de desempate disparam fraco
  e por igual, porque os dois objetivos são altos. É o comportamento desejado, já que o perfil é de fato misto.
- **Casos limite**: com tudo 1, as penalidades disparam, mas a compatibilidade é limitada a 0 % e não fica
  negativa. Com tudo 5, todas as trilhas chegam a 100 % e o desempate cai nas regras fortes e na ordem da base.
  Com tudo 3, a certeza é 0 % e só as penalidades diferenciam as trilhas. Nos três casos o motor e o roadmap
  funcionam, com prontidão 0 % sem conhecimento e 100 % com conhecimento máximo.

### 7.3 Observações da calibração

- **Nenhum peso precisou ser alterado na Fase 5**: as 10 personas típicas acertaram com a base das Fases 1 e 2.
- **Sensibilidade do empate**: uma primeira versão do Igor com design e `obj_interface` = 4 (contra matemática e `obj_previsoes` = 5) dava 10,7 p.p. de
  margem a favor de Ciência de Dados, sem empate. Isso é coerente: um ponto a menos numa pergunta de peso 3
  indica preferência real. Por isso as personas ambíguas foram escritas com os itens centrais das duas
  trilhas **no mesmo nível**. O mesmo ajuste foi feito em Beatriz (design 5 → 4, já que design pesa 3 em
  Front-end e 1 em Mobile) e em Renato (bancos de dados 5 → 4, já que pesa 3 em Engenharia e 1 em Ciência).
- **Limitação conhecida**: penalidades com `!x` disparam com grau 0,25 já quando `x = 4`. Por exemplo, P03
  tira 0,5 ponto de quem tem matemática 4 e `obj_previsoes` 4. O efeito é pequeno e, nos pares gêmeos, simétrico,
  mas uma evolução possível seria um limiar mínimo de ativação para as penalidades.
