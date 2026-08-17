/**
 * =========================================================================
 * CREAR PODER SIN LÍMITES - BACKEND QUANTUM TEAM GLOBAL
 * Motor de Estandarización & Saneamiento de Perfiles V5
 * =========================================================================
 * 
 * REGLAS DE ESTANDARIZACIÓN:
 * 1. Nombres y Apellidos: Formato Nombre Propio (Title Case), sin mayúsculas sostenidas ni espacios extra.
 * 2. WhatsApp: Formato internacional limpio E.164 (+593..., +51..., +57..., +52...) sin ceros intermedios.
 * 3. Instagram: Siempre con prefijo '@' (@usuario).
 * 4. Correo: Minúsculas estrictas.
 * 5. Género: Femenino | Masculino | Otro.
 * 6. Anti-Duplicados: Exactamente 1 fila única por DNI/Cédula o Correo.
 * 7. Función `estandarizarTodaLaHoja()`: Limpia y formatea toda la base de datos existente en 1 clic.
 */

// ==========================================
// FUNCIONES DE NORMALIZACIÓN & ESTANDARIZACIÓN
// ==========================================

function formatNombrePropio(str) {
  if (!str) return "";
  return str.toString().trim()
    .toLowerCase()
    .split(/\s+/)
    .map(function(w) {
      if (!w) return "";
      return w.charAt(0).toUpperCase() + w.slice(1);
    })
    .join(" ");
}

function formatWhatsApp(str, sede) {
  if (!str) return "";
  var clean = str.toString().replace(/[^\d+]/g, "").trim();
  if (!clean.startsWith("+")) {
    if (clean.startsWith("593") || clean.startsWith("51") || clean.startsWith("57") || clean.startsWith("52")) {
      clean = "+" + clean;
    } else {
      var s = (sede || "").toUpperCase();
      if (s === "LIM" || s === "PER" || s === "PERU") clean = "+51" + clean.replace(/^0+/, "");
      else if (s === "UIO" || s === "UIO1" || s === "GYE" || s === "CUE" || s === "ECU") clean = "+593" + clean.replace(/^0+/, "");
      else if (s === "MED" || s === "COL") clean = "+57" + clean.replace(/^0+/, "");
      else if (s === "MEX") clean = "+52" + clean.replace(/^0+/, "");
      else clean = "+" + clean;
    }
  }
  // Corregir anomalías comunes como prefijo de país + cero inicial (+593099... -> +59399...)
  clean = clean.replace(/^\+5930/, "+593");
  clean = clean.replace(/^\+510/, "+51");
  clean = clean.replace(/^\+570/, "+57");
  clean = clean.replace(/^\+520/, "+52");
  return clean;
}

function formatInstagram(str) {
  if (!str) return "";
  var clean = str.toString().trim().replace(/^@+/, "");
  if (!clean) return "";
  return "@" + clean;
}

function formatGenero(str) {
  if (!str) return "";
  var s = str.toString().trim().toLowerCase();
  if (s.indexOf("fem") !== -1 || s === "f" || s === "mujer") return "Femenino";
  if (s.indexOf("masc") !== -1 || s === "m" || s === "hombre" || s === "varon") return "Masculino";
  if (s.indexOf("otro") !== -1 || s.indexOf("prefiero") !== -1) return "Otro";
  return str.toString().trim();
}

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
    
    // Extracción limpia y estandarizada
    var timestamp = Utilities.formatDate(new Date(), "GMT-5", "yyyy-MM-dd HH:mm:ss");
    var sede = (data.sede || "").toString().trim().toUpperCase();
    var nombreCompleto = formatNombrePropio(data.nombre || "");
    var tipoDoc = (data.tipo_doc || "DNI").toString().trim().toUpperCase();
    var numDoc = (data.num_doc || "").toString().trim().replace(/['"\s]/g, "");
    var fechaNac = (data.fecha_nac || "").toString().trim();
    var genero = formatGenero(data.genero || "");
    var email = (data.email || "").toString().trim().toLowerCase();
    var whatsapp = formatWhatsApp(data.whatsapp || "", sede);
    var estatura = (data.estatura || data.altura || "").toString().trim();
    var pesoActual = (data.peso_actual || data.peso || "").toString().trim();
    var pesoIdeal = (data.peso_ideal || data.ideal || "").toString().trim();
    var tallaPolo = (data.talla_polo || "").toString().trim().toUpperCase();
    var edicionesQt = (data.ediciones_qt || "").toString().trim();
    var instagram = formatInstagram(data.instagram || "");
    var declaracion = (data.declaracion || "").toString().trim();
    var estado = "ACTIVO - VERIFICADO";
    
    if (!nombreCompleto && !numDoc && !email) {
      return ContentService.createTextOutput(JSON.stringify({ status: "ignored" }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Asegurar columnas requeridas en encabezados
    var lastCol = Math.max(sheet.getLastColumn(), 1);
    var rawHeaders = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
    
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
    
    var finalHeaders = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var rowData = new Array(finalHeaders.length).fill("");
    var colDocIndex = -1;
    var colEmailIndex = -1;
    
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
    
    // BÚSQUEDA ANTI-DUPLICADOS (UPSERT)
    var lastRow = sheet.getLastRow();
    var existingRowIndex = -1;
    
    if (lastRow > 1) {
      var allData = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).getValues();
      for (var r = 0; r < allData.length; r++) {
        var row = allData[r];
        var rowDoc = colDocIndex >= 0 ? (row[colDocIndex] || "").toString().replace(/['"\s]/g, "").trim() : "";
        var rowMail = colEmailIndex >= 0 ? (row[colEmailIndex] || "").toString().trim().toLowerCase() : "";
        
        if ((numDoc && rowDoc && numDoc === rowDoc) || (email && rowMail && email === rowMail)) {
          existingRowIndex = r + 2;
          break;
        }
      }
    }
    
    if (existingRowIndex > 1) {
      sheet.getRange(existingRowIndex, 1, 1, rowData.length).setValues([rowData]);
    } else {
      sheet.appendRow(rowData);
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      modo: existingRowIndex > 1 ? "actualizado" : "creado",
      nombre: nombreCompleto,
      whatsapp: whatsapp,
      instagram: instagram,
      estatura: estatura,
      peso: pesoActual
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
 * =========================================================================
 * EJECUTA ESTA FUNCIÓN PARA ESTANDARIZAR Y LIMPIAR TODA LA HOJA EN 1 CLIC:
 * 1. Pone todos los nombres en formato Title Case.
 * 2. Limpia y estandariza todos los WhatsApps con código internacional.
 * 3. Añade '@' a todos los Instagrams.
 * 4. Limpia correos y documentos.
 * 5. Elimina filas duplicadas conservando la más reciente.
 * =========================================================================
 */
function estandarizarTodaLaHoja() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return;
  
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var range = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn());
  var values = range.getValues();
  
  // Identificar índices de columnas
  var colIdx = {};
  for (var c = 0; c < headers.length; c++) {
    var h = headers[c].toString().toLowerCase().trim();
    if (h.indexOf("sede") !== -1) colIdx.sede = c;
    else if (h.indexOf("nombre") !== -1) colIdx.nombre = c;
    else if (h.indexOf("número") !== -1 || h.indexOf("numero") !== -1 || h.indexOf("documento") !== -1) colIdx.numDoc = c;
    else if (h.indexOf("género") !== -1 || h.indexOf("genero") !== -1) colIdx.genero = c;
    else if (h.indexOf("correo") !== -1 || h.indexOf("email") !== -1) colIdx.email = c;
    else if (h.indexOf("whatsapp") !== -1) colIdx.whatsapp = c;
    else if (h.indexOf("instagram") !== -1) colIdx.instagram = c;
    else if (h.indexOf("talla") !== -1) colIdx.talla = c;
    else if (h.indexOf("estado") !== -1) colIdx.estado = c;
  }
  
  var seen = {};
  var standardizedRows = [];
  
  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    var sede = colIdx.sede !== undefined ? (row[colIdx.sede] || "").toString().trim().toUpperCase() : "";
    var numDoc = colIdx.numDoc !== undefined ? (row[colIdx.numDoc] || "").toString().replace(/['"\s]/g, "").trim() : "";
    var email = colIdx.email !== undefined ? (row[colIdx.email] || "").toString().trim().toLowerCase() : "";
    
    // Normalizar campos en la fila
    if (colIdx.nombre !== undefined) row[colIdx.nombre] = formatNombrePropio(row[colIdx.nombre]);
    if (colIdx.sede !== undefined) row[colIdx.sede] = sede;
    if (colIdx.numDoc !== undefined) row[colIdx.numDoc] = "'" + numDoc;
    if (colIdx.genero !== undefined) row[colIdx.genero] = formatGenero(row[colIdx.genero]);
    if (colIdx.email !== undefined) row[colIdx.email] = email;
    if (colIdx.whatsapp !== undefined) row[colIdx.whatsapp] = "'" + formatWhatsApp(row[colIdx.whatsapp], sede);
    if (colIdx.instagram !== undefined) row[colIdx.instagram] = formatInstagram(row[colIdx.instagram]);
    if (colIdx.talla !== undefined) row[colIdx.talla] = (row[colIdx.talla] || "").toString().trim().toUpperCase();
    if (colIdx.estado !== undefined) row[colIdx.estado] = "ACTIVO - VERIFICADO";
    
    // Clave de deduplicación
    var key = numDoc || email || (colIdx.nombre !== undefined ? (row[colIdx.nombre] || "").toString().trim().toLowerCase() : "");
    if (key) {
      seen[key] = row;
    }
  }
  
  for (var k in seen) {
    standardizedRows.push(seen[k]);
  }
  
  sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
  if (standardizedRows.length > 0) {
    sheet.getRange(2, 1, standardizedRows.length, standardizedRows[0].length).setValues(standardizedRows);
  }
  
  SpreadsheetApp.getUi().alert("✨ ¡Estandarización Completa!", "Se limpiaron los nombres a Title Case, se formatearon los WhatsApps internacionales, se agregaron los @ a Instagram y se eliminaron los duplicados.", SpreadsheetApp.getUi().ButtonSet.OK);
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    version: "5.0_Standardizer"
  })).setMimeType(ContentService.MimeType.JSON);
}
