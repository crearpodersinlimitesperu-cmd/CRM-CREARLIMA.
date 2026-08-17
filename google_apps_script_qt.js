/**
 * =========================================================================
 * CREAR PODER SIN LÍMITES - BACKEND QUANTUM TEAM GLOBAL
 * Motor Inteligente con Mapeo Dinámico de Columnas & Anti-Duplicados (V4)
 * =========================================================================
 * 
 * CARACTERÍSTICAS V4:
 * 1. MAPEO DINÁMICO: No importa el orden en que tengas las columnas en tu Sheet,
 *    el script detecta automáticamente los encabezados y coloca cada dato (Estatura,
 *    Peso Actual, Peso Ideal, Género, etc.) en su columna EXACTA.
 * 2. AUTO-CREACIÓN DE COLUMNAS: Si en tu hoja falta alguna columna, la agrega al final.
 * 3. ANTI-DUPLICADOS (UPSERT): Si el usuario ya existe por Documento o Correo,
 *    actualiza su fila sin duplicar.
 * 4. LIMPIADOR DE DUPLICADOS: Función `limpiarDuplicadosExistentes()`.
 */

function setupHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var defaultHeaders = [
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
  
  var headerRange = sheet.getRange(1, 1, 1, defaultHeaders.length);
  headerRange.setValues([defaultHeaders]);
  headerRange.setBackground("#0a0f1c");
  headerRange.setFontColor("#00d2ff");
  headerRange.setFontWeight("bold");
  headerRange.setHorizontalAlignment("center");
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
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
    
    // Extracción limpia y robusta de todos los campos
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
      return ContentService.createTextOutput(JSON.stringify({ status: "ignored" }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // =========================================================================
    // 1. LEER ENCABEZADOS REALES DE LA FILA 1 Y ASEGURAR COLUMNAS FALTANTES
    // =========================================================================
    var lastCol = Math.max(sheet.getLastColumn(), 1);
    var rawHeaders = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
    
    // Verificar si faltan columnas críticas en el Sheet del usuario
    var headerStr = rawHeaders.join(" ").toLowerCase();
    if (headerStr.indexOf("estatura") === -1) {
      sheet.getRange(1, rawHeaders.length + 1).setValue("Estatura (cm)");
      rawHeaders.push("Estatura (cm)");
    }
    headerStr = rawHeaders.join(" ").toLowerCase();
    if (headerStr.indexOf("peso actual") === -1 && headerStr.indexOf("peso (kg)") === -1) {
      sheet.getRange(1, rawHeaders.length + 1).setValue("Peso Actual (kg)");
      rawHeaders.push("Peso Actual (kg)");
    }
    headerStr = rawHeaders.join(" ").toLowerCase();
    if (headerStr.indexOf("peso ideal") === -1) {
      sheet.getRange(1, rawHeaders.length + 1).setValue("Peso Ideal Estimado (kg)");
      rawHeaders.push("Peso Ideal Estimado (kg)");
    }
    headerStr = rawHeaders.join(" ").toLowerCase();
    if (headerStr.indexOf("género") === -1 && headerStr.indexOf("genero") === -1) {
      sheet.getRange(1, rawHeaders.length + 1).setValue("Género");
      rawHeaders.push("Género");
    }
    
    // Recargar lista final de encabezados
    var finalHeaders = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var rowData = new Array(finalHeaders.length).fill("");
    var colDocIndex = -1;
    var colEmailIndex = -1;
    
    // Mapeo inteligente por coincidencia de nombre de columna
    for (var col = 0; col < finalHeaders.length; col++) {
      var h = finalHeaders[col].toString().toLowerCase().trim();
      
      if (h.indexOf("timestamp") !== -1 || h.indexOf("fecha y hora") !== -1 || h.indexOf("marca temporal") !== -1) {
        rowData[col] = timestamp;
      } else if (h.indexOf("sede") !== -1) {
        rowData[col] = sede;
      } else if (h.indexOf("nombre") !== -1 || h.indexOf("apellido") !== -1) {
        rowData[col] = nombreCompleto;
      } else if (h.indexOf("tipo") !== -1 && h.indexOf("doc") !== -1) {
        rowData[col] = tipoDoc;
      } else if (h.indexOf("número") !== -1 || h.indexOf("numero") !== -1 || h.indexOf("documento") !== -1 || h.indexOf("cédula") !== -1 || h.indexOf("dni") !== -1) {
        rowData[col] = "'" + numDoc;
        colDocIndex = col;
      } else if (h.indexOf("nacimiento") !== -1) {
        rowData[col] = fechaNac;
      } else if (h.indexOf("género") !== -1 || h.indexOf("genero") !== -1 || h.indexOf("sexo") !== -1) {
        rowData[col] = genero;
      } else if (h.indexOf("correo") !== -1 || h.indexOf("email") !== -1 || h.indexOf("electr") !== -1) {
        rowData[col] = email;
        colEmailIndex = col;
      } else if (h.indexOf("whatsapp") !== -1 || h.indexOf("tel") !== -1 || h.indexOf("celular") !== -1) {
        rowData[col] = "'" + whatsapp;
      } else if (h.indexOf("estatura") !== -1 || h.indexOf("altura") !== -1) {
        rowData[col] = estatura;
      } else if (h.indexOf("peso actual") !== -1 || (h.indexOf("peso") !== -1 && h.indexOf("ideal") === -1)) {
        rowData[col] = pesoActual;
      } else if (h.indexOf("peso ideal") !== -1 || h.indexOf("ideal") !== -1) {
        rowData[col] = pesoIdeal;
      } else if (h.indexOf("talla") !== -1 || h.indexOf("polo") !== -1 || h.indexOf("uniforme") !== -1) {
        rowData[col] = tallaPolo;
      } else if (h.indexOf("ediciones") !== -1) {
        rowData[col] = edicionesQt;
      } else if (h.indexOf("instagram") !== -1) {
        rowData[col] = instagram;
      } else if (h.indexOf("declaraci") !== -1 || h.indexOf("compromiso") !== -1) {
        rowData[col] = declaracion;
      } else if (h.indexOf("estado") !== -1) {
        rowData[col] = estado;
      }
    }
    
    // =========================================================================
    // 2. BÚSQUEDA ANTI-DUPLICADOS (UPSERT)
    // =========================================================================
    var lastRow = sheet.getLastRow();
    var existingRowIndex = -1;
    
    if (lastRow > 1) {
      var allData = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).getValues();
      for (var r = 0; r < allData.length; r++) {
        var row = allData[r];
        var rowDoc = colDocIndex >= 0 ? (row[colDocIndex] || "").toString().replace(/['"\s]/g, "").trim() : "";
        var rowMail = colEmailIndex >= 0 ? (row[colEmailIndex] || "").toString().trim().toLowerCase() : "";
        
        if ((numDoc && rowDoc && numDoc === rowDoc) || (email && rowMail && email === rowMail)) {
          existingRowIndex = r + 2; // Fila 1-based
          break;
        }
      }
    }
    
    if (existingRowIndex > 1) {
      // ACTUALIZAR FILA EXISTENTE (1 sola fila limpia por persona)
      sheet.getRange(existingRowIndex, 1, 1, rowData.length).setValues([rowData]);
    } else {
      // INSERTAR NUEVO REGISTRO
      sheet.appendRow(rowData);
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      modo: existingRowIndex > 1 ? "actualizado" : "creado",
      nombre: nombreCompleto,
      estatura: estatura,
      peso: pesoActual,
      peso_ideal: pesoIdeal
    })).setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

/**
 * Función para limpiar todos los duplicados históricos acumulados
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
      seen[key] = row; // Conserva el registro más reciente
    }
  }
  
  for (var k in seen) {
    uniqueRows.push(seen[k]);
  }
  
  sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
  if (uniqueRows.length > 0) {
    sheet.getRange(2, 1, uniqueRows.length, uniqueRows[0].length).setValues(uniqueRows);
  }
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    version: "4.0_SmartMapper"
  })).setMimeType(ContentService.MimeType.JSON);
}
