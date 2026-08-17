/**
 * =========================================================================
 * CREAR PODER SIN LÍMITES - BACKEND QUANTUM TEAM GLOBAL
 * Google Apps Script Web App Endpoint para Captura de Perfiles QT
 * =========================================================================
 * 
 * INSTRUCCIONES DE INSTALACIÓN EN GOOGLE SHEETS:
 * 1. Crea una hoja de Google Sheets llamada "QUANTUM_TEAM_GLOBAL".
 * 2. Ve a Extensiones > Apps Script.
 * 3. Borra el código existente y pega este archivo completo.
 * 4. Haz clic en "Implementar" > "Nueva implementación".
 * 5. Tipo: "Aplicación web".
 * 6. Descripción: "Endpoint QT Global v1.0".
 * 7. Ejecutar como: "Yo" (tu cuenta de Google).
 * 8. Quién tiene acceso: "Cualquier persona" (Anyone).
 * 9. Haz clic en "Implementar", autoriza los permisos y copia la "URL de la aplicación web".
 * 10. Pega esa URL en el formulario web actualizacion_qt.html en la variable APPS_SCRIPT_URL.
 */

function setupHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = [
    "Fecha y Hora (Timestamp)",
    "Sede Base",
    "Nombres y Apellidos",
    "Tipo de Documento",
    "Número de Documento",
    "Correo Electrónico",
    "WhatsApp (Con Código)",
    "Fecha de Nacimiento",
    "Talla de Polo / Uniforme",
    "Rol / Especialidad QT",
    "Entrenamientos Vividos",
    "Ediciones en QT",
    "Instagram",
    "Declaración de Liderazgo Cuántico",
    "Estado de Perfil"
  ];
  
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    var headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setBackground("#0a0f1c");
    headerRange.setFontColor("#00d2ff");
    headerRange.setFontWeight("bold");
    headerRange.setHorizontalAlignment("center");
  }
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    // Esperar hasta 10 segundos para evitar colisiones de concurrencia
    lock.waitLock(10000);
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("QUANTUM_TEAM_GLOBAL") || ss.getActiveSheet();
    
    // Asegurar encabezados si está vacía
    if (sheet.getLastRow() === 0) {
      setupHeaders();
    }
    
    // Parsear payload (soporta JSON o Form Data)
    var data = {};
    if (e.postData && e.postData.contents) {
      try {
        data = JSON.parse(e.postData.contents);
      } catch (parseErr) {
        data = e.parameter || {};
      }
    } else {
      data = e.parameter || {};
    }
    
    var timestamp = Utilities.formatDate(new Date(), "GMT-5", "yyyy-MM-dd HH:mm:ss");
    var sede = data.sede || "";
    var nombreCompleto = data.nombre || "";
    var tipoDoc = data.tipo_doc || "";
    var numDoc = data.num_doc || "";
    var email = data.email || "";
    var whatsapp = data.whatsapp || "";
    var fechaNac = data.fecha_nac || "";
    var tallaPolo = data.talla_polo || "";
    var rolEspecialidad = data.rol_especialidad || "";
    var entrenamientos = Array.isArray(data.entrenamientos) ? data.entrenamientos.join(", ") : (data.entrenamientos || "");
    var edicionesQt = data.ediciones_qt || "";
    var instagram = data.instagram || "";
    var declaracion = data.declaracion || "";
    var estado = "ACTIVO - VERIFICADO";
    
    // Insertar fila
    sheet.appendRow([
      timestamp,
      sede,
      nombreCompleto,
      tipoDoc,
      "'" + numDoc, // Forzar texto para no perder ceros a la izquierda
      email,
      "'" + whatsapp,
      fechaNac,
      tallaPolo,
      rolEspecialidad,
      entrenamientos,
      edicionesQt,
      instagram,
      declaracion,
      estado
    ]);
    
    var response = {
      status: "success",
      message: "¡Perfil de Quantum Team registrado y sincronizado exitosamente!",
      timestamp: timestamp,
      nombre: nombreCompleto,
      sede: sede
    };
    
    return ContentService.createTextOutput(JSON.stringify(response))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: "Error procesando el registro: " + err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    message: "CREAR PODER SIN LÍMITES - API Quantum Team Activa",
    version: "1.0"
  })).setMimeType(ContentService.MimeType.JSON);
}
