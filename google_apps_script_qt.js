/**
 * =========================================================================
 * CREAR PODER SIN LÍMITES - BACKEND QUANTUM TEAM GLOBAL
 * Google Apps Script Web App Endpoint para Captura de Perfiles QT
 * =========================================================================
 * 
 * URL de Implementación Oficial Activa:
 * https://script.google.com/macros/s/AKfycbwt5xLxpVBCEOrBicBgcynOAMWTxYs75f_KLLtgE5UaDTo8VB-eqtZBSJCfgoTkntyS/exec
 * 
 * CARACTERÍSTICAS:
 * 1. ANTI-DUPLICADOS: Si el usuario ya existe (mismo Número de Documento o Correo),
 *    ACTUALIZA su fila existente en vez de crear filas duplicadas.
 * 2. CERO PÉRDIDA: Cada líder tiene exactamente UNA fila única y actualizada.
 * 3. LIMPIADOR AUTOMÁTICO: Función `limpiarDuplicadosExistentes()` para sanear la hoja.
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
    // Esperar hasta 15 segundos para evitar colisiones concurrentes
    lock.waitLock(15000);
    
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
    var sede = (data.sede || "").toString().trim();
    var nombreCompleto = (data.nombre || "").toString().trim();
    var tipoDoc = (data.tipo_doc || "DNI").toString().trim();
    var numDoc = (data.num_doc || "").toString().trim().replace(/['"\s]/g, "");
    var fechaNac = (data.fecha_nac || "").toString().trim();
    var genero = (data.genero || "").toString().trim();
    var email = (data.email || "").toString().trim().toLowerCase();
    var whatsapp = (data.whatsapp || "").toString().trim();
    var estatura = (data.estatura || data.altura || "").toString().trim();
    var pesoActual = (data.peso_actual || data.peso || "").toString().trim();
    var pesoIdeal = (data.peso_ideal || data.ideal || "").toString().trim();
    var tallaPolo = (data.talla_polo || "").toString().trim();
    var edicionesQt = (data.ediciones_qt || "").toString().trim();
    var instagram = (data.instagram || "").toString().trim();
    var declaracion = (data.declaracion || "").toString().trim();
    var estado = "ACTIVO - VERIFICADO";
    
    if (!nombreCompleto && !numDoc && !email) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "ignored",
        message: "Payload vacío ignorado"
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    var rowData = [
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
    ];
    
    // =========================================================================
    // LÓGICA ANTI-DUPLICADOS (UPSERT): BUSCAR SI YA EXISTE ESTE USUARIO
    // =========================================================================
    var lastRow = sheet.getLastRow();
    var existingRowIndex = -1;
    
    if (lastRow > 1) {
      var allData = sheet.getRange(2, 1, lastRow - 1, 9).getValues(); // Columnas A hasta I
      for (var i = 0; i < allData.length; i++) {
        var rowNumDoc = (allData[i][4] || "").toString().replace(/['"\s]/g, "").trim(); // Col E: Num Doc
        var rowEmail = (allData[i][7] || "").toString().trim().toLowerCase();          // Col H: Email
        
        if ((numDoc && rowNumDoc && numDoc === rowNumDoc) || (email && rowEmail && email === rowEmail)) {
          existingRowIndex = i + 2; // Fila real en la hoja (base 1)
          break;
        }
      }
    }
    
    if (existingRowIndex > 1) {
      // ACTUALIZAR FILA EXISTENTE (CERO DUPLICADOS)
      sheet.getRange(existingRowIndex, 1, 1, rowData.length).setValues([rowData]);
      var responseMsg = "Perfil actualizado exitosamente (sin duplicados).";
    } else {
      // INSERTAR NUEVA FILA
      sheet.appendRow(rowData);
      var responseMsg = "Nuevo perfil registrado exitosamente.";
    }
    
    var response = {
      status: "success",
      message: responseMsg,
      timestamp: timestamp,
      nombre: nombreCompleto,
      sede: sede,
      modo: existingRowIndex > 1 ? "actualizado" : "creado"
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

/**
 * Función utilitaria para limpiar todos los duplicados históricos existentes en la hoja.
 * Puedes ejecutarla manualmente desde el editor de Google Apps Script.
 */
function limpiarDuplicadosExistentes() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  if (lastRow <= 2) return;
  
  var range = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn());
  var values = range.getValues();
  
  var seen = {};
  var uniqueRows = [];
  
  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    var numDoc = (row[4] || "").toString().replace(/['"\s]/g, "").trim();
    var email = (row[7] || "").toString().trim().toLowerCase();
    var key = numDoc || email || (row[2] || "").toString().trim().toLowerCase();
    
    if (key) {
      // Guardar la versión más reciente (sobrescribe con la última)
      seen[key] = row;
    }
  }
  
  for (var k in seen) {
    uniqueRows.push(seen[k]);
  }
  
  // Limpiar y reescribir solo registros únicos
  sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
  if (uniqueRows.length > 0) {
    sheet.getRange(2, 1, uniqueRows.length, uniqueRows[0].length).setValues(uniqueRows);
  }
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    message: "CREAR PODER SIN LÍMITES - API Quantum Team Global Activa (Motor Anti-Duplicados V3)",
    version: "3.0"
  })).setMimeType(ContentService.MimeType.JSON);
}
