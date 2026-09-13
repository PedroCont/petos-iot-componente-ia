"""
PetOS - API de Inteligência Artificial
Serve o modelo de classificação de risco de saúde (normal / atencao / critico)
treinado em notebook/modelo_risco_petos.ipynb.

Endpoints:
  GET  /          -> healthcheck
  POST /predict   -> recebe leitura(s) da coleira + perfil do animal, retorna o risco
"""

import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify

MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_risco_pet.pkl")
modelo = joblib.load(MODEL_PATH)

app = Flask(__name__)

CAMPOS_OBRIGATORIOS = [
    "especie",          # "cao" | "gato" | "ave"
    "porte",            # "pequeno" | "medio" | "grande" | "unico"
    "idade_categoria",  # "filhote" | "adulto" | "idoso"
    "temperatura",      # float, graus Celsius (sensor DHT22)
    "umidade",          # float, percentual (sensor DHT22)
    "atividade_pct",    # float, 0-100, percentual de tempo com movimento (sensor PIR)
]


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "PetOS IA - Modelo de Risco de Saude"})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True, silent=True)

    if payload is None:
        return jsonify({"erro": "JSON invalido ou ausente no corpo da requisicao"}), 400

    # aceita tanto um objeto único quanto uma lista de objetos
    itens = payload if isinstance(payload, list) else [payload]

    faltando = [
        campo for campo in CAMPOS_OBRIGATORIOS
        if any(campo not in item for item in itens)
    ]
    if faltando:
        return jsonify({
            "erro": "Campos obrigatorios ausentes em um ou mais itens",
            "campos_faltando": faltando,
            "campos_esperados": CAMPOS_OBRIGATORIOS,
        }), 400

    try:
        df = pd.DataFrame(itens)[CAMPOS_OBRIGATORIOS]
        predicoes = modelo.predict(df)
        probabilidades = modelo.predict_proba(df)
        classes = modelo.classes_
    except Exception as e:
        return jsonify({"erro": f"Falha ao gerar predicao: {str(e)}"}), 422

    resultados = []
    for i in range(len(df)):
        resultados.append({
            "nivel_risco": predicoes[i],
            "probabilidades": {
                classes[j]: round(float(probabilidades[i][j]), 4)
                for j in range(len(classes))
            },
        })

    resposta = resultados if len(resultados) > 1 else resultados[0]
    return jsonify(resposta)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
