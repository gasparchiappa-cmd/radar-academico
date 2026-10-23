
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://www.arbeitnow.com/api/job-board-api"

TERMOS_CARGOS = [
    "researcher",
    "research scientist",
    "research fellow",
    "postdoctoral",
    "professor",
    "lecturer",
    "academic",
    "investigador",
    "investigadora",
    "pesquisador",
    "profesor",
    "docente",
]

TERMOS_AREAS = [
    "physiotherapy",
    "physical therapy",
    "rehabilitation",
    "cardiology",
    "cardiovascular",
    "clinical research",
    "epidemiology",
    "fisioterapia",
    "rehabilitacion",
    "reabilitacao",
    "metaanalysis",
    "systematic review",
]

ARQUIVO = Path("vagas.json")


def normalizar(texto):
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    return re.sub(r"\s+", " ", texto).strip().lower()


def relevante(vaga):
    titulo = normalizar(vaga.get("title", ""))
    descricao = normalizar(vaga.get("description", ""))

    cargo = any(t in titulo for t in TERMOS_CARGOS)
    area = any(t in titulo + " " + descricao for t in TERMOS_AREAS)

    return cargo and area


def carregar_anteriores():
    if not ARQUIVO.exists():
        return []

    try:
        dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
        return dados if isinstance(dados, list) else []
    except (ValueError, OSError):
        return []


def buscar():
    resposta = requests.get(API_URL, timeout=30)
    resposta.raise_for_status()

    dados = resposta.json()
    return dados.get("data", [])


def main():
    anteriores = carregar_anteriores()
    registros = {
        vaga["url"]: vaga
        for vaga in anteriores
        if isinstance(vaga, dict) and vaga.get("url")
    }

    vagas = buscar()
    data = datetime.now(timezone.utc).date().isoformat()

    for vaga in vagas:
        if not relevante(vaga):
            continue

        url = vaga.get("url")
        if not url:
            continue

        registros[url] = {
            "titulo": vaga.get("title", ""),
            "instituicao": vaga.get("company_name", ""),
            "pais": vaga.get("location", ""),
            "modalidade": (
                "Remoto" if vaga.get("remote") else "Não informada"
            ),
            "categoria": "Pesquisador ou docente",
            "remuneracao": "Não informada",
            "prazo": "Não informado",
            "url": url,
            "fonte": "Arbeitnow",
            "data_coleta": data,
            "status": "Não verificado",
        }

    resultado = list(registros.values())

    ARQUIVO.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Registros armazenados: {len(resultado)}")


if __name__ == "__main__":
    main()
