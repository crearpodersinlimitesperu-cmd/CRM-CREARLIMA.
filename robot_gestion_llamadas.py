"""
Robot Gestion de Llamadas v3 - Extrae datos con Playwright
============================================================
Corregido: selecciona equipo + CC uno por uno, espera reload completo.
"""
import sys, time, re, pandas as pd
from playwright.sync_api import sync_playwright

def log(msg, end="\n"):
    print(msg, end=end, flush=True)

URL_LOGIN = "https://crearpslglobal.com/admin/login.php"
URL_GESTION = "https://crearpslglobal.com/admin/reporte_detallegestion.php"
USER = "jsanchez"
PASS = "crearpsl25"
OUTPUT_FILE = "Gestion_Llamadas.xlsx"

# Solo equipos relevantes para C1
EQUIPOS_C1 = ["EQUIPO 27", "EQUIPO 26", "EQUIPO 25", "EQUIPO 24",
              "EQUIPO 23", "EQUIPO 22", "EQUIPO 21", "EQUIPO 20"]
CC_ALIASES = ["DIANA", "JOYCE", "ZULEY"]

def iniciar_robot_gestion():
    log("[ROBOT-GESTION v3] Iniciando...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Login
        page.goto(URL_LOGIN, wait_until="networkidle")
        page.fill("#exampleInputEmail1", USER)
        page.fill("#exampleInputPassword1", PASS)
        page.click("button.btn-primary")
        page.wait_for_load_state("networkidle")
        log("[OK] Login exitoso")

        # 2. Ir a gestion
        page.goto(URL_GESTION, wait_until="networkidle")
        page.wait_for_selector("#cbnEquipo", timeout=15000)

        # Obtener opciones
        equipos = page.evaluate("""() => {
            const s = document.getElementById('cbnEquipo');
            return Array.from(s.options).map(o => ({t: o.text.trim(), v: o.value}));
        }""")
        ccs = page.evaluate("""() => {
            const s = document.getElementById('IdCoordinador');
            return Array.from(s.options).map(o => ({t: o.text.trim(), v: o.value}));
        }""")
        log(f"[OK] {len(equipos)} equipos, {len(ccs)} coordinadores")

        # Mapear
        eq_map = {}
        for e in equipos:
            for nombre in EQUIPOS_C1:
                if nombre in e["t"]:
                    eq_map[nombre] = e["v"]
        cc_map = {}
        for alias in CC_ALIASES:
            for c in ccs:
                if alias.lower() in c["t"].lower():
                    cc_map[alias] = c["v"]
                    break
        log(f"[OK] Equipos C1: {list(eq_map.keys())}")
        log(f"[OK] CCs: {cc_map}")

        all_data = []

        for eq_name, eq_val in eq_map.items():
            for alias, cc_val in cc_map.items():
                log(f"  {eq_name} + {alias}... ", end="")
                try:
                    # Navegar fresco cada vez para evitar estado corrupto
                    page.goto(URL_GESTION, wait_until="networkidle")
                    page.wait_for_selector("#cbnEquipo", timeout=10000)

                    # Seleccionar equipo
                    page.select_option("#cbnEquipo", value=eq_val)
                    page.wait_for_timeout(300)
                    # Seleccionar coordinadora
                    page.select_option("#IdCoordinador", value=cc_val)
                    page.wait_for_timeout(300)

                    # Click Consultar y esperar reload
                    page.click("#invoice_btn")
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)

                    # Leer Total de Registros
                    body = page.text_content("body") or ""
                    m = re.search(r"Total de Registros:\s*(\d+)", body)
                    total = int(m.group(1)) if m else 0

                    if total == 0:
                        log("0")
                        continue

                    # Poner 400 entries
                    try:
                        page.select_option("select.form-select", "400")
                        page.wait_for_timeout(1500)
                    except:
                        pass

                    # Extraer filas
                    rows = page.evaluate("""() => {
                        const trs = document.querySelectorAll('table tbody tr');
                        return Array.from(trs).map(tr => {
                            const td = tr.querySelectorAll('td');
                            if (td.length < 9) return null;
                            return [
                                td[0].innerText.trim(),
                                td[1].innerText.trim(),
                                td[2].innerText.trim(),
                                td[3].innerText.trim(),
                                td[4].innerText.trim(),
                                td[5].innerText.trim().substring(0,200),
                                td[6].innerText.trim(),
                                td[7].innerText.trim(),
                                td[8].innerText.trim()
                            ];
                        }).filter(r => r !== null);
                    }""")

                    for r in rows:
                        if r[0] and "No data" not in r[0]:
                            all_data.append({
                                "Coordinador": r[0],
                                "Equipo": r[1] or eq_name,
                                "Primera_Llamada": r[2],
                                "Segunda_Llamada": r[3],
                                "Ultima_Gestion": r[4],
                                "Comentario": r[5],
                                "Asistencia_C1": r[6],
                                "Apellidos": r[7],
                                "Nombres": r[8],
                                "CC_Alias": alias,
                            })
                    log(f"{len(rows)} registros")
                except Exception as e:
                    log(f"ERROR: {e}")
                time.sleep(0.3)

        browser.close()

    if not all_data:
        log("[WARN] Sin datos")
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    df.to_excel(OUTPUT_FILE, index=False)
    log(f"\n[TOTAL] {len(df)} registros guardados en {OUTPUT_FILE}")
    subir_a_sheets(df)
    return df


def subir_a_sheets(df):
    try:
        from sync_cloud import conectar_sheets, SHEET_ID
        c = conectar_sheets()
        if not c: return
        sh = c.open_by_key(SHEET_ID)
        tabs = [w.title for w in sh.worksheets()]
        if "GESTION_LLAMADAS" not in tabs:
            sh.add_worksheet(title="GESTION_LLAMADAS", rows=5000, cols=15)
        ws = sh.worksheet("GESTION_LLAMADAS")
        ws.clear()
        out = df.fillna("").astype(str)
        ws.update([out.columns.values.tolist()] + out.values.tolist())
        log(f"[OK] Subido a GESTION_LLAMADAS en Sheets")
    except Exception as e:
        log(f"[ERROR Sheets] {e}")


if __name__ == "__main__":
    iniciar_robot_gestion()
