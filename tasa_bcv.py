#!/usr/bin/env python3
"""Actualiza tasa.json con la tasa oficial del Banco Central de Venezuela.

Lo ejecuta la tarea .github/workflows/tasa-bcv.yml. Lee el dólar directamente
de https://www.bcv.org.ve; si el sitio no responde usa fuentes de respaldo que
publican la misma tasa oficial. No toca la tasa manual que haya publicado el
panel administrativo. Solo usa la biblioteca estándar de Python.
"""
import datetime as dt
import json
import os
import re
import ssl
import sys
import urllib.request

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasa.json")
AGENTE = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CARACAS = dt.timezone(dt.timedelta(hours=-4))


def bajar(url, verificar=True, espera=30):
    ctx = ssl.create_default_context()
    if not verificar:  # el certificado del BCV suele llegar con la cadena incompleta
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    pet = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": "*/*"})
    with urllib.request.urlopen(pet, timeout=espera, context=ctx) as r:
        return r.read().decode("utf-8", "replace")


def numero(txt):
    """'36,12340000' o '1.036,12' -> float"""
    t = txt.strip().replace("\xa0", "").replace(" ", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return float(t)


def leer_bcv(html):
    """Extrae el dólar y la fecha valor de la portada del BCV."""
    m = re.search(r'id="dolar".*?<strong>\s*([\d.,]+)\s*</strong>', html, re.S)
    if not m:
        raise ValueError("no se encontró el bloque del dólar en la página del BCV")
    tasa = numero(m.group(1))
    f = re.search(r'date-display-single[^>]*content="(\d{4}-\d{2}-\d{2})', html)
    fecha = f.group(1) if f else dt.datetime.now(CARACAS).date().isoformat()
    return tasa, fecha


def del_bcv():
    ultimo = None
    for verificar in (True, False):
        try:
            tasa, fecha = leer_bcv(bajar("https://www.bcv.org.ve/", verificar))
            return {"tasa": tasa, "fecha": fecha, "fuente": "BCV · bcv.org.ve"}
        except Exception as e:  # noqa: BLE001
            ultimo = e
    raise ultimo


def de_respaldo():
    fuentes = [
        ("BCV · DolarApi", "https://ve.dolarapi.com/v1/dolares/oficial", ("promedio", "venta"), ("fechaActualizacion",)),
        ("BCV · bcv-api", "https://bcv-api.rafnixg.dev/rates/", ("dollar",), ("date",)),
    ]
    ultimo = None
    for nombre, url, claves, fechas in fuentes:
        try:
            j = json.loads(bajar(url, espera=20))
            tasa = next(float(j[k]) for k in claves if j.get(k))
            cruda = next((str(j[k]) for k in fechas if j.get(k)), "")
            fecha = dt.datetime.now(CARACAS).date().isoformat()
            if re.match(r"\d{4}-\d{2}-\d{2}T", cruda):
                fecha = dt.datetime.fromisoformat(cruda.replace("Z", "+00:00")).astimezone(CARACAS).date().isoformat()
            elif re.match(r"\d{4}-\d{2}-\d{2}", cruda):
                fecha = cruda[:10]
            return {"tasa": tasa, "fecha": fecha, "fuente": nombre}
        except Exception as e:  # noqa: BLE001
            ultimo = e
            print(f"  {nombre}: {e}")
    raise ultimo or RuntimeError("sin fuentes de respaldo")


def actualizar(actual, nueva, ahora):
    """Devuelve (documento, cambió). Conserva la tasa manual y el historial.

    Formato de tasa.json:
      valor, fecha, actualizada, fuente  -> tasa BCV vigente
      manual {valor, fecha, nota, activo} -> la publica el panel administrativo
      historial [{fecha, valor}]
    """
    doc = {"valor": None, "fecha": None, "actualizada": None, "fuente": None, "manual": None, "historial": []}
    doc.update(actual or {})
    tasa = round(float(nueva["tasa"]), 4)
    if not tasa > 0:
        raise ValueError("tasa no válida")
    previa = doc.get("valor")
    if previa and abs(tasa / previa - 1) > 0.5:
        raise ValueError(f"la tasa leída ({tasa}) se aleja demasiado de la anterior ({previa}); no se publica")
    cambio = previa != tasa or doc.get("fecha") != nueva["fecha"]
    if cambio:
        doc.update({"valor": tasa, "fecha": nueva["fecha"], "actualizada": ahora, "fuente": nueva["fuente"]})
        h = {x["fecha"]: x["valor"] for x in (doc.get("historial") or []) if x.get("fecha") and x.get("valor")}
        h[nueva["fecha"]] = tasa
        doc["historial"] = [{"fecha": f, "valor": h[f]} for f in sorted(h)][-400:]
    return doc, cambio


def main():
    try:
        nueva = del_bcv()
    except Exception as e:  # noqa: BLE001
        print(f"bcv.org.ve no respondió ({e}); se prueban las fuentes de respaldo")
        try:
            nueva = de_respaldo()
        except Exception as e2:  # noqa: BLE001
            print(f"No se pudo obtener la tasa: {e2}")
            return 1
    try:
        with open(RUTA, encoding="utf-8") as f:
            actual = json.load(f)
    except (OSError, ValueError):
        actual = {}
    ahora = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc, cambio = actualizar(actual, nueva, ahora)
    print(f"Tasa BCV {nueva['tasa']} · fecha valor {nueva['fecha']} · {nueva['fuente']} · {'actualizada' if cambio else 'sin cambios'}")
    if cambio:
        with open(RUTA, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
