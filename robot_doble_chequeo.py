"""
Robot Doble Chequeo de Confirmaciones v2
==========================================
Extrae resumen de resultado_llamadas.php cada 15 min,
cruza con los datos de Sala de Guerra (GESTION_LLAMADAS en Sheets),
y sube el reporte a la pestaña AUDITORIA_CONFIRMACIONES.
"""
import sys, time, json, os
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from playwright.sync_api import sync_playwright

TZ = ZoneInfo("America/Lima")
URL_LOGIN = "https://crearpslglobal.com/admin/login.php"
URL_RESUMEN = "https://crearpslglobal.com/admin/resultado_llamadas.php"
USER = "jsanchez"
PASS = "crearpsl25"
OUTPUT_FILE = "Auditoria.json"

# Capítulo 1: Equipos 20-27 (campaña activa)
EQUIPOS_C1 = ["EQUIPO 27", "EQUIPO 26", "EQUIPO 25", "EQUIPO 24",
              "EQUIPO 23", "EQUIPO 22", "EQUIPO 21", "EQUIPO 20"]
# Capítulo 2: Equipos 14-19 (anteriores)
EQUIPOS_C2 = ["EQUIPO 19", "EQUIPO 18", "EQUIPO 17",
              "EQUIPO 16", "EQUIPO 15", "EQUIPO 14"]

CC_MAP_LABELS = {
    "DIANA": "Diana Yesenia Moscoso Robles",
    "JOYCE": "Joyce Pamela",  # partial match
    "ZULEY": "Otty Zuley Urteaga Silva",
}

def log(msg, end="\n"):
    try:
        print(msg, end=end, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode(), end=end, flush=True)

def ahora():
    return datetime.now(TZ)

def auditar_confirmaciones():
    log(f"[AUDITORIA v2] Iniciando doble chequeo — {ahora().strftime('%d/%m/%Y %H:%M')}")
    resultados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Login
        page.goto(URL_LOGIN, wait_until="networkidle")
        page.fill("#exampleInputEmail1", USER)
        page.fill("#exampleInputPassword1", PASS)
        page.click("button.btn-primary")
        page.wait_for_load_state("networkidle")
        log("[OK] Login exitoso")

        page.goto(URL_RESUMEN, wait_until="networkidle")
        page.wait_for_selector("#cbnEquipo", timeout=15000)

        # Obtener opciones de dropdowns
        equipos_opts = page.evaluate("""() => {
            const s = document.getElementById('cbnEquipo');
            return Array.from(s.options).map(o => ({t: o.text.trim(), v: o.value}));
        }""")
        ccs_opts = page.evaluate("""() => {
            const s = document.getElementById('cbnCoordinador');
            return Array.from(s.options).map(o => ({t: o.text.trim(), v: o.value}));
        }""")

        # Mapear equipos C1 y C2
        eq_map_c1 = {}
        eq_map_c2 = {}
        for e in equipos_opts:
            for nombre in EQUIPOS_C1:
                if nombre in e["t"]:
                    eq_map_c1[nombre] = e["v"]
            for nombre in EQUIPOS_C2:
                if nombre in e["t"]:
                    eq_map_c2[nombre] = e["v"]

        # Mapear coordinadoras
        cc_map = {}
        for alias, label_fragment in CC_MAP_LABELS.items():
            for c in ccs_opts:
                if label_fragment.lower() in c["t"].lower():
                    cc_map[alias] = c["v"]
                    break

        log(f"[OK] C1: {list(eq_map_c1.keys())} | C2: {list(eq_map_c2.keys())} | CCs: {list(cc_map.keys())}")

        # Función interna para extraer datos de un equipo+cc
        def extraer_datos(eq_name, eq_val, cc_alias, cc_val, capitulo):
            log(f"  [{capitulo}] {eq_name} + {cc_alias}... ", end="")
            try:
                page.goto(URL_RESUMEN, wait_until="networkidle")
                page.wait_for_selector("#cbnEquipo", timeout=10000)

                page.select_option("#cbnEquipo", value=eq_val)
                page.wait_for_timeout(300)
                page.select_option("#cbnCoordinador", value=cc_val)
                page.wait_for_timeout(300)

                page.click("#invoice_btn")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)

                data = page.evaluate("""() => {
                    let tables = document.querySelectorAll('table');
                    if (tables.length < 2) return null;
                    let rows = Array.from(tables[1].querySelectorAll('tr'));
                    if (rows.length < 2) return null;
                    let td = Array.from(rows[1].querySelectorAll('td, th'));
                    if (td.length > 2) {
                        return {
                            total_asignados: parseInt(td[1].innerText) || 0,
                            confirmados: parseInt(td[2].innerText) || 0,
                            nc: parseInt(td[3].innerText) || 0,
                            no_interesa: parseInt(td[4].innerText) || 0,
                            siguiente: parseInt(td[5].innerText) || 0,
                            por_confirmar: parseInt(td[6].innerText) || 0,
                            devolucion: parseInt(td[7].innerText) || 0
                        };
                    }
                    return null;
                }""")

                if data:
                    resultados.append({
                        "Timestamp": ahora().strftime("%d/%m/%Y %H:%M"),
                        "Capitulo": capitulo,
                        "Equipo": eq_name,
                        "CC": cc_alias,
                        "Total_Asignados": data["total_asignados"],
                        "Confirmados": data["confirmados"],
                        "NC": data["nc"],
                        "No_Interesa": data["no_interesa"],
                        "Siguiente": data["siguiente"],
                        "Por_Confirmar": data["por_confirmar"],
                        "Devolucion": data["devolucion"],
                    })
                    log(f"✅ {data['confirmados']} Conf / {data['nc']} NC")
                else:
                    log("⚪ Sin datos")
            except Exception as e:
                log(f"❌ {e}")
            time.sleep(0.3)

        # Capítulo 1
        for eq_name, eq_val in eq_map_c1.items():
            for alias, cc_val in cc_map.items():
                extraer_datos(eq_name, eq_val, alias, cc_val, "C1")

        # Capítulo 2
        for eq_name, eq_val in eq_map_c2.items():
            for alias, cc_val in cc_map.items():
                extraer_datos(eq_name, eq_val, alias, cc_val, "C2")

        browser.close()

    if not resultados:
        log("[WARN] Sin datos de auditoría")
        return

    # Guardar JSON local
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    log(f"\n[OK] {len(resultados)} registros guardados en {OUTPUT_FILE}")

    # Cruzar con Sala de Guerra (GESTION_LLAMADAS en Sheets)
    cruzar_con_sala_guerra(resultados)

    # Subir a Sheets
    subir_a_sheets(resultados)


def cruzar_con_sala_guerra(resultados):
    """Cruza datos de resultado_llamadas con GESTION_LLAMADAS y genera alertas."""
    try:
        from sync_cloud import conectar_sheets
        SHEET_ID = os.environ.get("CRM_SHEET_ID", "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y")
        c = conectar_sheets()
        if not c:
            log("[CRUCE] Sin conexion a Sheets")
            return

        sh = c.open_by_key(SHEET_ID)
        tabs = [w.title for w in sh.worksheets()]
        if "GESTION_LLAMADAS" not in tabs:
            log("[CRUCE] Pestana GESTION_LLAMADAS no existe aun")
            return

        ws = sh.worksheet("GESTION_LLAMADAS")
        records = ws.get_all_records()
        df_sala = pd.DataFrame(records)

        if df_sala.empty:
            log("[CRUCE] GESTION_LLAMADAS vacia")
            return

        # La columna real de resultado es Primera_Llamada (CONFIRMADO, NO CONTESTAN, etc.)
        col_resultado = "Primera_Llamada" if "Primera_Llamada" in df_sala.columns else "Asistencia_C1"

        alertas = []
        for reg in resultados:
            eq = reg["Equipo"]
            cc = reg["CC"]
            sys_conf = reg["Confirmados"]
            sys_nc = reg["NC"]

            if "Equipo" not in df_sala.columns or "CC_Alias" not in df_sala.columns:
                continue

            mask_eq = df_sala["Equipo"].astype(str).str.strip() == eq
            mask_cc = df_sala["CC_Alias"].astype(str).str.strip().str.upper() == cc
            subset = df_sala[mask_eq & mask_cc]

            if not subset.empty:
                sala_conf = int((subset[col_resultado].astype(str).str.upper() == "CONFIRMADO").sum())
                sala_nc = int((subset[col_resultado].astype(str).str.upper().str.contains("NO CONTESTA", na=False)).sum())

                reg["Sala_Confirmados"] = sala_conf
                reg["Sala_NC"] = sala_nc
                reg["Delta_Conf"] = sys_conf - sala_conf
                reg["Delta_NC"] = sys_nc - sala_nc

                if abs(reg["Delta_Conf"]) > 2:
                    alertas.append(f"ALERTA {cc}-{eq}: Sistema={sys_conf} vs Sala={sala_conf} (D={reg['Delta_Conf']})")
            else:
                reg["Sala_Confirmados"] = "N/A"
                reg["Sala_NC"] = "N/A"
                reg["Delta_Conf"] = "N/A"
                reg["Delta_NC"] = "N/A"

        if alertas:
            log("\nALERTAS DE DISCREPANCIA:")
            for a in alertas:
                log(f"  {a}")
        else:
            log("\nCRUCE LIMPIO: Datos de Sistema y Sala de Guerra coinciden")

        # Actualizar JSON con cruce
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)

    except Exception as e:
        log(f"[CRUCE ERROR] {e}")


def subir_a_sheets(resultados):
    """Sube la auditoría a la pestaña AUDITORIA_CONFIRMACIONES."""
    try:
        from sync_cloud import conectar_sheets
        SHEET_ID = os.environ.get("CRM_SHEET_ID", "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y")
        c = conectar_sheets()
        if not c:
            return

        sh = c.open_by_key(SHEET_ID)
        tabs = [w.title for w in sh.worksheets()]
        if "AUDITORIA_CONFIRMACIONES" not in tabs:
            sh.add_worksheet(title="AUDITORIA_CONFIRMACIONES", rows=5000, cols=20)
        ws = sh.worksheet("AUDITORIA_CONFIRMACIONES")

        # Limpiar y subir todo
        df = pd.DataFrame(resultados).fillna("").astype(str)
        ws.clear()
        ws.update([df.columns.values.tolist()] + df.values.tolist())
        log(f"[OK] Subido a AUDITORIA_CONFIRMACIONES en Sheets ({len(resultados)} registros)")
    except Exception as e:
        log(f"[ERROR Sheets] {e}")


if __name__ == "__main__":
    auditar_confirmaciones()
