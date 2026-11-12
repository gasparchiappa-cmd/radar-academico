
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from urllib.request import Request, urlopen
from urllib.error import URLError

ARQUIVO = Path("vagas.json")

BUSCAS = [
    "concurso professor fisioterapia universidade inscrições",
    "professor fisioterapia centro universitário contratação",
    "edital professor visitante fisioterapia doutorado",
    "concurso professor adjunto fisioterapia",
    "concurso professor assistente fisioterapia",
    "edital PROFIX fisioterapia reabilitação",
    "PROFIX fixação doutores ciências da saúde",
    "professor fisioterapia convocatoria universidad",
    "plaza profesor fisioterapia universidad España",
    "concurso professor fisioterapia universidade Portugal",
    "assistant professor visiting professor physical therapy university",
]

TERMOS_OPORTUNIDADE = [
    "concurso", "edital", "seleção", "selecao",
    "inscrições", "inscricoes", "vaga", "vagas",
    "professor visitante", "bolsa", "bolsas",
    "convocatoria", "plaza", "plazas",
    "oferta de empleo", "contratación",
    "recruitment", "vacancy", "vacancies",
    "fellowship", "postdoctoral", "hiring", "profix",
]

TERMOS_ACADEMICOS = [
    "universidade", "universidad", "university",
    "instituto", "institut", "faculdade",
    "faculty", "research", "pesquisa",
    "investigação", "investigacion",
    "docente", "professor", "profesor", "profix",
    "pesquisador", "investigador",
]

TERMOS_AREAS = [
    "fisioterapia", "physiotherapy",
    "physical therapy", "rehabilitation",
    "reabilitação", "rehabilitación",
    "cardiologia", "cardiology",
    "cardiovascular", "exercise physiology",
    "fisiologia do exercício",
    "fisiología del ejercicio",
    "clinical research", "pesquisa clínica",
]

def normalizar(texto):
    return re.sub(r"\s+", " ", str(texto or "")).strip().lower()

def carregar_anteriores():
    if not ARQUIVO.exists():
        return []
    try:
        dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
        return dados if isinstance(dados, list) else []
    except (OSError, ValueError):
        return []

def pesquisar_noticias(consulta):
    parametros = urlencode({
        "q": consulta,
        "hl": "pt-BR",
        "gl": "BR",
        "ceid": "BR:pt-419",
    })
    url = "https://news.google.com/rss/search?" + parametros

    with urlopen(Request(url, headers={"User-Agent": "RadarAcademico/2.0"}), timeout=20) as resposta:
        raiz = ET.fromstring(resposta.read(3000000))
    return raiz.findall("./channel/item")

def relevante(titulo):
    texto = normalizar(titulo)
    oportunidade = any(t in texto for t in TERMOS_OPORTUNIDADE)
    academico = any(t in texto for t in TERMOS_ACADEMICOS)
    area = any(t in texto for t in TERMOS_AREAS)
    return oportunidade and academico and (area or "profix" in texto)

def identificar_pais(titulo):
    texto = normalizar(titulo)
    if "portugal" in texto:
        return "Portugal"
    if "españa" in texto or "espana" in texto:
        return "Espanha"
    if "brasil" in texto or "federal" in texto:
        return "Brasil"
    return "Não informado"

def main():
    anteriores = carregar_anteriores()
    registros = {
        item["url"]: item
        for item in anteriores
        if isinstance(item, dict) and item.get("url")
    }

    data = datetime.now(timezone.utc).date().isoformat()
    novas = 0
    falhas = 0

    for consulta in BUSCAS:
        print("Pesquisando:", consulta)

        try:
            anuncios = pesquisar_noticias(consulta)
        except (URLError, OSError, ET.ParseError) as erro:
            print("Falha na consulta:", erro)
            falhas += 1
            continue

        for anuncio in anuncios:
            titulo = (anuncio.findtext("title") or "").strip()
            url = (anuncio.findtext("link") or "").strip()
            fonte = anuncio.findtext("source") or "Google Notícias"

            if not titulo or not url or not relevante(titulo):
                continue

            if url in registros:
                continue

            registros[url] = {
                "titulo": titulo,
                "instituicao": fonte,
                "pais": identificar_pais(titulo),
                "modalidade": "Não informada",
                "categoria": "Pesquisador",
                "remuneracao": "Não informada",
                "prazo": "",
                "url": url,
                "fonte": "Google Notícias RSS: " + fonte,
                "data_coleta": data,
                "status": "Não verificado",
            }
            novas += 1

        time.sleep(1)

    resultado = list(registros.values())

    ARQUIVO.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Novas oportunidades candidatas:", novas)
    print("Total de registros:", len(resultado))
    print("Consultas com falha:", falhas)
    print("Atenção: resultados não verificados.")

if __name__ == "__main__":
    main()
