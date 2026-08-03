import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import csv
import os
import pathlib
import tempfile
import zipfile
import shutil
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

BASE_DIR = pathlib.Path(__file__).parent.absolute()
TEMPLATE_DIR = BASE_DIR / 'template'
OUTPUT_DIR = BASE_DIR / 'outputs'

def get_template():
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    return env.get_template('diploma_template.html')

import base64

def get_logo_uri():
    logo_file = TEMPLATE_DIR / 'logo_oficial.png'
    try:
        with open(logo_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception:
        return ""

def get_bg_uri():
    bg_file = TEMPLATE_DIR / 'fondo_premium.png'
    try:
        with open(bg_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception:
        return ""

def render_html(template, logo_path, bg_path, nombre, rol, curso, equipo, num_equipo, sede, fecha_inicio, fecha_final, gerente_sede):
    return template.render(
        nombre=nombre,
        rol=rol,
        curso=curso,
        equipo=equipo,
        num_equipo=num_equipo,
        sede=sede,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final,
        gerente_sede=gerente_sede,
        logo_path=logo_path,
        bg_path=bg_path
    )

def exportar_pdf_playwright(html_content, output_pdf_path):
    import sys
    import asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        
        # Esperar a que las fuentes web (Google Fonts) estén completamente cargadas
        page.evaluate("document.fonts.ready")
        
        page.pdf(
            path=str(output_pdf_path),
            format="A4",
            landscape=True,
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        browser.close()

def generar_diploma_unico(nombre, rol, curso, equipo, num_equipo, sede, fecha_inicio, fecha_final, gerente_sede):
    """Genera un diploma y devuelve la ruta del PDF creado."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    template = get_template()
    logo_path = get_logo_uri()
    bg_path = get_bg_uri()
    
    html_content = render_html(template, logo_path, bg_path, nombre, rol, curso, equipo, num_equipo, sede, fecha_inicio, fecha_final, gerente_sede)
    
    rol_dir = OUTPUT_DIR / sede / rol
    rol_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{nombre.replace(' ', '_')}.pdf"
    pdf_path = rol_dir / filename
    
    exportar_pdf_playwright(html_content, pdf_path)
    return pdf_path

def generar_diplomas_masivo(csv_path):
    """Genera masivamente y devuelve la ruta a un archivo ZIP con todos los diplomas."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    template = get_template()
    logo_path = get_logo_uri()
    bg_path = get_bg_uri()
    
    # Directorio temporal para empacar el lote actual
    temp_dir = pathlib.Path(tempfile.mkdtemp())
    
    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            for row in reader:
                nombre = row['Nombre'].strip()
                rol = row['Rol'].strip()
                curso = row.get('Curso', 'Transformación Cuántica Global').strip()
                equipo = row.get('Equipo', '').strip()
                num_equipo = row.get('NumEquipo', '').strip()
                sede = row['Sede'].strip()
                fecha_inicio = row.get('FechaInicio', '').strip()
                fecha_final = row.get('FechaFinal', '').strip()
                gerente_sede = row.get('GerenteSede', '').strip()
                
                html_content = render_html(template, logo_path, bg_path, nombre, rol, curso, equipo, num_equipo, sede, fecha_inicio, fecha_final, gerente_sede)
                page.set_content(html_content, wait_until="networkidle")
                
                # Guardar en temp
                rol_dir = temp_dir / sede / rol
                rol_dir.mkdir(parents=True, exist_ok=True)
                filename = f"{nombre.replace(' ', '_')}.pdf"
                pdf_path = rol_dir / filename
                
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    landscape=True,
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
                )
                
                # Guardar copia permanente
                perm_dir = OUTPUT_DIR / sede / rol
                perm_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pdf_path, perm_dir / filename)
                
            browser.close()
            
    # Crear ZIP
    zip_path = OUTPUT_DIR / "lote_diplomas.zip"
    if zip_path.exists():
        zip_path.unlink()
        
    shutil.make_archive(str(OUTPUT_DIR / "lote_diplomas"), 'zip', str(temp_dir))
    shutil.rmtree(temp_dir)
    return zip_path

if __name__ == "__main__":
    csv_test = BASE_DIR / 'datos_diplomas.csv'
    if csv_test.exists():
        print("Iniciando generación masiva desde CSV...")
        zip_file = generar_diplomas_masivo(csv_test)
        print(f"Finalizado. ZIP creado en: {zip_file}")
