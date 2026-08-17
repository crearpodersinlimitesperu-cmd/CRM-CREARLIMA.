/**
 * =========================================================================
 * CREAR PODER SIN LÍMITES - BACKEND QUANTUM TEAM GLOBAL
 * Google Apps Script Web App Endpoint para Captura de Perfiles QT
 * =========================================================================
 * 
 * URL de Implementación Oficial Activa:
 * https://script.google.com/macros/s/AKfycbwt5xLxpVBCEOrBicBgcynOAMWTxYs75f_KLLtgE5UaDTo8VB-eqtZBSJCfgoTkntyS/exec
 */

function setupHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = [
    "Fecha y Hora (Timestamp)",
    "Sede Base",
    "Nombres y Apellidos",
    "Tipo de Documento",
    "Número de Documento",
    "Fecha de Nacimiento",
    "Género",
    "Correo Electrónico",
    "WhatsApp (Con Código)",
    "Estatura (cm)",
    "Peso Actual (kg)",
    "Peso Ideal Estimado (kg)",
    "Talla de Polo / Uniforme",
    "Ediciones en QT",
    "Instagram",
    "Declaración de Liderazgo y Compromiso",
    "Estado de Perfil"
  ];
  
  // Limpiar y escribir la primera fila
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setValues([headers]);
  headerRange.setBackground("#0a0f1c");
  headerRange.setFontColor("#00d2ff");
  headerRange.setFontWeight("bold");
  headerRange.setHorizontalAlignment("center");
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("QUANTUM_TEAM_GLOBAL") || ss.getActiveSheet();
    
    if (sheet.getLastRow() === 0) {
      setupHeaders();
    }
    
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
    var fechaNac = data.fecha_nac || "";
    var genero = data.genero || "";
    var email = data.email || "";
    var whatsapp = data.whatsapp || "";
    var estatura = data.estatura || "";
    var pesoActual = data.peso_actual || "";
    var pesoIdeal = data.peso_ideal || "";
    var tallaPolo = data.talla_polo || "";
    var edicionesQt = data.ediciones_qt || "";
    var instagram = data.instagram || "";
    var declaracion = data.declaracion || "";
    var estado = "ACTIVO - VERIFICADO";
    
    sheet.appendRow([
      timestamp,
      sede,
      nombreCompleto,
      tipoDoc,
      "'" + numDoc,
      fechaNac,
      genero,
      email,
      "'" + whatsapp,
      estatura,
      pesoActual,
      pesoIdeal,
      tallaPolo,
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
    message: "CREAR PODER SIN LÍMITES - API Quantum Team Global Activa",
    version: "2.0"
  })).setMimeType(ContentService.MimeType.JSON);
}
