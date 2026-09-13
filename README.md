# 🐾 PetOS — Componente de Inteligência Artificial

Modelo de IA para **priorização de risco de saúde** de pets, a partir dos dados da coleira inteligente (ESP32 + DHT22 + PIR) desenvolvida na etapa de IoT do projeto PetOS.

> Documentação técnica completa (problema, dados, personalização, arquitetura): [`docs/DOCUMENTACAO_IA.md`](docs/DOCUMENTACAO_IA.md)

## O que este componente faz

Recebe a leitura da coleira (temperatura, umidade, atividade) + o perfil do animal (espécie, porte, idade) e retorna um nível de risco **personalizado**: `normal`, `atencao` ou `critico`, com a probabilidade de cada classe.

Isso substitui o alerta genérico por limiar fixo (usado na etapa anterior de IoT) por uma decisão que considera que um cão, um gato e uma ave em reabilitação têm faixas fisiológicas diferentes — e que filhotes/idosos têm menor tolerância a desvios.

## Estrutura do repositório

```
.
├── README.md                          <- este arquivo
├── notebook/
│   ├── modelo_risco_petos.ipynb       <- geração do dataset, treino e avaliação do modelo
│   └── dataset_sintetico_petos.csv    <- dataset gerado pelo notebook
├── api/
│   ├── app.py                         <- API Flask que serve o modelo
│   ├── modelo_risco_pet.pkl           <- modelo treinado (exportado pelo notebook)
│   ├── requirements.txt
│   └── Dockerfile
└── docs/
    ├── DOCUMENTACAO_IA.md             <- documentação técnica completa do componente de IA
    └── arquitetura.mermaid            <- diagrama de arquitetura (fonte)
```

## Tecnologias utilizadas

- **Python 3.11**
- **scikit-learn 1.8.0** — treinamento do modelo (RandomForestClassifier)
- **pandas / numpy** — geração do dataset sintético e manipulação de dados
- **Flask 3.1.3** — API de predição
- **Docker** — empacotamento e execução da API
- **Jupyter Notebook** — pipeline de geração de dados, treino e avaliação

## Como executar

### 1. Treinar o modelo (opcional — o `.pkl` já vem treinado em `api/`)

```bash
cd notebook
pip install pandas numpy scikit-learn matplotlib seaborn joblib
jupyter notebook modelo_risco_petos.ipynb
```

Executar todas as células gera `dataset_sintetico_petos.csv` e `modelo_risco_pet.pkl` nesta pasta. Se for usar esse `.pkl` recém-gerado na API, copie-o para dentro de `api/`, substituindo o existente.

### 2. Rodar a API localmente (sem Docker)

```bash
cd api
pip install -r requirements.txt
python app.py
```

A API sobe em `http://localhost:8000`.

### 3. Rodar a API com Docker

```bash
cd api
docker build -t petos-ia .
docker run -p 8000:8000 petos-ia
```

### 4. Testar a API

**Healthcheck:**
```bash
curl http://localhost:8000/
```

**Predição (via curl):**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"especie":"ave","porte":"unico","idade_categoria":"filhote","temperatura":41.0,"umidade":35.0,"atividade_pct":8.0}'
```

**Predição (via Postman):**
- Método: `POST`
- URL: `http://localhost:8000/predict`
- Body → raw → JSON:
```json
{
  "especie": "cao",
  "porte": "medio",
  "idade_categoria": "adulto",
  "temperatura": 27.0,
  "umidade": 50.0,
  "atividade_pct": 60.0
}
```

Também é possível enviar uma lista de objetos no mesmo formato para prever vários animais em uma única requisição.

## Resultados parciais

Modelo treinado e avaliado no notebook (`notebook/modelo_risco_petos.ipynb`), com dataset sintético de 4.000 registros:

- **Acurácia geral:** ~90%
- **Classe `critico`:** precisão ~0.92 / recall ~0.83 — poucos falsos negativos em casos críticos, o erro mais custoso deste sistema
- **Confusões concentradas entre níveis adjacentes** (`normal`↔`atencao`, `atencao`↔`critico`), quase nenhuma confusão direta entre `normal` e `critico`
- **Features mais relevantes:** temperatura, umidade e atividade (leituras diretas da coleira), seguidas por espécie e idade — confirmando que a personalização por perfil do animal contribui para a decisão

Detalhes completos (matriz de confusão, importância de features, gráficos) estão no notebook.

## Limitações conhecidas

- Modelo treinado com dados **sintéticos**; não substitui avaliação veterinária real.
- Répteis silvestres fora do escopo desta versão (fisiologia ectotérmica exige lógica de referência diferente).

Mais detalhes em [`docs/DOCUMENTACAO_IA.md`](docs/DOCUMENTACAO_IA.md).
