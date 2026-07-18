// ================================================================
// CREAR PODER SIN LIMITES - BACKEND API LOGISTICA GLOBAL v3.4 (UNIFICADO)
// Multi-pais + OCR + Tracking + Respaldo Automatico + Self-Healing
// ================================================================

const CONFIG = {
  SHEET_ID: '1u0tc4GeooPmSwNxZ0CErKGtRU4oD-mO3l--ZSQM-KPs',
  DRIVE_FOLDER_ID: '1oi7mUG619dQ2ZVzHzUyO5Xkwti-jgDFl', // ID de carpeta ACTUALIZADO
  AVIATIONSTACK_KEY: '9c8775ac594fe0204cfc138a7f835f2b',
  ALLOWED_USERS: [
    'admin@crearpsl.net',
    'jose.sanchez@crearpsl.net',
    'emily.campuzano@crearpsl.net',
    'fer.aragon@crearpsl.net',
    'paul.sosa@crearpsl.net',
    'oficina.mx@crearpsl.net',
    'evelyn.cedillo@crearpsl.net',
    'viviana.catota@crearpsl.net',
    'alfonso.trujillo@crearpsl.net',
    'kerly.carrillo@crearpsl.net',
    'juan.reinoso@crearpsl.net',
    'emely.leon@crearpsl.net',
    'asistente.facturacion@crearpsl.net',
    'asistente.contable@crearpsl.net',
    'contabilidad.lima@crearpsl.net',
    'contabilidad.medellin@crearpsl.net',
    'andres.gomez@crearpsl.net',
    'coodinacion.administrativa@crearpsl.net',
    'facturacion.cartera@crearpsl.net',
    'contabilidad.global@crearpsl.net',
    'leandro.brunis@crearpsl.net',
    'talento.humano@crearpsl.net',
    'Jonathan.larosa@crearpsl.net',
    'brenda.rodriguez@crearpsl.net',
    'diana.macas@crearpsl.net',
    'josue.vera@crearpsl.net',
    'diana.moscoso@crearpsl.net',
    'joyce.marin@crearpsl.net',
    'linid.valencia@crearpsl.net',
    'leyla.pasquel@crearpsl.net',
    'karla.pastrano@crearpsl.net',
    'adrianna.guarochico@crearpsl.net',
    'liliana.cubillo@crearpsl.net',
    'ibetancourth@crearpsl.net',
    'valentina.r@crearpsl.net',
    'yurany.gonzalez@crearpsl.net',
    'mauricio.ramirez@crearpsl.net',
    'erika.gavilanez@crearpsl.net',
    'freddy.sosa@crearpsl.net',
    'legal@crearpsl.net'
  ]
};

// ================================================================
// ENDPOINTS GET
// ================================================================
function doGet(e) {
  try {
    const action = e.parameter.action;
    let result;
    switch(action) {
      case 'getEventos':       result = getAllEventos(); break;
      case 'getVuelos':        result = getAllVuelos(); break;
      case 'getFlightStatus':    result = getFlightStatus(e.parameter.flightNumber); break;
      case 'getAuditLog':      result = getAuditLog(parseInt(e.parameter.limit) || 50); break;
      case 'getDashboardKPIs': result = getDashboardKPIs(); break;
      case 'listDriveFiles':   result = listDriveFiles(); break;
      case 'getDriveFile':     result = getDriveFile(e.parameter.fileId); break;
      case 'getLogistica':     result = getLogisticaRawData(); break; // Añadido para mantenimiento
      case 'health':           result = {status: 'ok', version: '3.4_unificada', timestamp: new Date().toISOString()}; break;
      default:                 result = {error: 'Accion no valida'};
    }
    return jsonResponse(result);
  } catch(err) {
    return jsonResponse({error: err.toString()});
  }
}

// ================================================================
// ENDPOINTS POST
// ================================================================
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const user = Session.getActiveUser().getEmail() || 'anon@crearpsl.com';
    let result;
    switch(data.action) {
      case 'updateLogistics': result = updateLogistics(data, user); break;
      case 'registerFlight':  result = registerFlight(data, user); break;
      case 'uploadTicket':    result = uploadTicket(data, user); break;
      case 'batchUpdate':     result = batchUpdate(data, user); break;
      case 'crearRespaldo':   result = crearRespaldoEnSheet(data.backupData); break;
      case 'replaceLogistica': result = replaceLogistica(data, user); break; // Añadido para deduplicación masiva
      default:                result = {error: 'Accion no valida'};
    }
    return jsonResponse(result);
  } catch(err) {
    return jsonResponse({error: err.toString()});
  }
}

// ================================================================
// UTILERIAS SELF-HEALING DE HOJAS
// ================================================================
function getOrCreateSheet(sheetName, headers) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    if (headers && headers.length > 0) {
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
    }
  }
  return sheet;
}

// ================================================================
// LECTURA DE DATOS
// ================================================================
function getLogisticaRawData() {
  const logSheet = getOrCreateSheet('LOGISTICA', ['ID', 'JSON_DATA', 'LAST_UPDATED']);
  const data = logSheet.getDataRange().getValues();
  const result = {};
  for (let i = 1; i < data.length; i++) {
    const id = data[i][0];
    const jsonStr = data[i][1];
    if (id && jsonStr) {
      try {
        result[id] = JSON.parse(jsonStr);
      } catch (err) {}
    }
  }
  return { status: 'success', data: result };
}

function getAllEventos() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const eventSheet = ss.getSheetByName('Hoja 2');
  if (!eventSheet) {
    return [];
  }
  
  // Cargar eventos base desde Hoja 2
  const eventValues = eventSheet.getDataRange().getValues();
  if (eventValues.length < 2) return [];
  
  // Cargar logísticas desde LOGISTICA
  const logSheet = getOrCreateSheet('LOGISTICA', ['ID', 'JSON_DATA', 'LAST_UPDATED']);
  const logValues = logSheet.getDataRange().getValues();
  const logisticsMap = {};
  for (let i = 1; i < logValues.length; i++) {
    const id = String(logValues[i][0]);
    const jsonStr = logValues[i][1];
    if (id && jsonStr) {
      try {
        logisticsMap[id] = JSON.parse(jsonStr);
      } catch(e) {}
    }
  }
  
  const result = [];
  const seenEventIds = {}; // Deduplicación defensiva en tiempo de lectura
  
  // Columnas: Fecha (0), Sede (1), Equipo (2), Entrenamiento (3), Entrenador (4)
  for (let i = 1; i < eventValues.length; i++) {
    const row = eventValues[i];
    const rawDate = row[0];
    if (!rawDate) continue;
    
    let dateStr = "";
    if (rawDate instanceof Date) {
      dateStr = Utilities.formatDate(rawDate, Session.getScriptTimeZone(), "yyyy-MM-dd'T'HH:mm:ss");
    } else {
      dateStr = String(rawDate);
    }
    
    // Obtener los valores para evitar usar getDisplayValues() que es extremadamente lento
    const sede = String(row[1] || 'LIM').trim();
    const equipo = String(row[2] || '').trim();
    const nombre = String(row[3] || '').trim();
    const trainer = String(row[4] || '').trim();
    
    // Normalizar equipo eliminando caracteres no numéricos
    let equipoClean = equipo.replace(/[^0-9]/g, '');
    if (!equipoClean) equipoClean = equipo;
    
    // Normalizar sede
    let sedeNorm = sede.toUpperCase().trim();
    if (sedeNorm.indexOf('UIO C1') !== -1 || sedeNorm.indexOf('QUITO C1') !== -1) {
      sedeNorm = 'UIOC1';
    } else if (sedeNorm.indexOf('UIO C2') !== -1 || sedeNorm.indexOf('QUITO C2') !== -1) {
      sedeNorm = 'UIOC2';
    } else {
      sedeNorm = sedeNorm.substring(0, 3);
      if (sedeNorm === 'CDM') sedeNorm = 'MEX';
    }
    
    // Generar ID del evento compatible con frontend
    const datePart = dateStr.split('T')[0].replace(/-/g, '');
    const eventId = `${sedeNorm}_E${equipoClean}_${datePart}`;
    
    // Evitar renderizar filas duplicadas en el calendario
    if (seenEventIds[eventId]) continue;
    seenEventIds[eventId] = true;
    
    const log = logisticsMap[eventId] || {};
    // Soportar también si la data guardada tiene sub-objeto 'logistics'
    const cleanLog = log.logistics || log;
    
    let place = "";
    let address = "";
    if (sedeNorm === 'LIM') { place = "Lima"; address = "Lima, Perú"; }
    else if (sedeNorm === 'GYE') { place = "Guayaquil"; address = "Guayaquil, Ecuador"; }
    else if (sedeNorm.startsWith('UIO') || sedeNorm === 'QUI') { place = "Quito"; address = "Quito, Ecuador"; }
    else if (sedeNorm === 'MED') { place = "Medellín"; address = "Medellín, Colombia"; }
    else if (sedeNorm === 'MEX') { place = "Ciudad de México"; address = "México DF"; }
    else if (sedeNorm === 'CUE') { place = "Cuenca"; address = "Cuenca, Ecuador"; }
    else { place = sede; address = ""; }

    // Leer columna H (índice 7) para lugar personalizado
    const lugarPersonalizado = row[7] ? String(row[7]).trim() : '';
    if (lugarPersonalizado) {
      address = lugarPersonalizado;
    }

    let endDateStr = "";
    if (rawDate instanceof Date) {
      const endDate = new Date(rawDate.getTime() + 2 * 24 * 60 * 60 * 1000);
      endDateStr = Utilities.formatDate(endDate, Session.getScriptTimeZone(), "yyyy-MM-dd'T'HH:mm:ss");
    } else {
      endDateStr = dateStr;
    }

    result.push({
      id: eventId,
      sede: sede,
      fecha_inicio: dateStr,
      fecha_fin: endDateStr,
      nombre: nombre,
      equipo: equipoClean,
      trainer: trainer,
      lugar: place,
      direccion: address,
      ticket: cleanLog.ticket || 'pending',
      hotel: cleanLog.hotel || 'pending',
      notified: cleanLog.trainer_notified || cleanLog.notified || false,
      arrival: cleanLog.trainer_arrival || cleanLog.arrival || '',
      ticket_url: cleanLog.ticket_url || ''
    });
  }
  return result;
}

function getAllVuelos() {
  const logSheet = getOrCreateSheet('LOGISTICA', ['ID', 'JSON_DATA', 'LAST_UPDATED']);
  const values = logSheet.getDataRange().getValues();
  const vuelos = [];
  for (let i = 1; i < values.length; i++) {
    try {
      const data = JSON.parse(values[i][1]);
      const cleanLog = data.logistics || data;
      const ticket = cleanLog.ticket || data.ticket;
      if (ticket && ticket !== 'pending') {
        vuelos.push({ id: values[i][0], ...data });
      }
    } catch(e) {}
  }
  return vuelos;
}

function getFlightStatus(flightNumber) {
  try {
    const url = `http://api.aviationstack.com/v1/flights?access_key=${CONFIG.AVIATIONSTACK_KEY}&flight_iata=${encodeURIComponent(flightNumber)}`;
    const res = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    if (res.getResponseCode() === 200) {
      return JSON.parse(res.getContentText());
    }
  } catch(e) {
    return {error: 'No se pudo contactar AviationStack'};
  }
  return null;
}

function getAuditLog(limit) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const logSheet = ss.getSheetByName('AUDITORIA_LOG');
  if (!logSheet) return [];
  const values = logSheet.getDataRange().getValues();
  const headers = values[0];
  const logs = [];
  const start = Math.max(1, values.length - limit);
  for (let i = values.length - 1; i >= start; i--) {
    const row = values[i];
    let logObj = {};
    for (let j = 0; j < headers.length; j++) {
      logObj[headers[j]] = row[j];
    }
    logs.push(logObj);
  }
  return logs;
}

function getDashboardKPIs() {
  const eventos = getAllEventos();
  let vuelosPendientes = 0;
  let vuelosComprados = 0;
  let presupuestoEstimado = 0;
  
  eventos.forEach(ev => {
    if (ev.ticket === 'pending') vuelosPendientes++;
    else vuelosComprados++;
  });
  
  // Costo promedio estandarizado
  presupuestoEstimado = vuelosPendientes * 450; 
  
  return {
    total_eventos: eventos.length,
    vuelos_pendientes: vuelosPendientes,
    vuelos_comprados: vuelosComprados,
    cobertura_logistica: eventos.length > 0 ? Math.round((vuelosComprados / eventos.length) * 100) : 0,
    presupuesto_requerido: presupuestoEstimado
  };
}

// Modificado para que retorne tambien imagenes y le asigne el mimetype correcto
function listDriveFiles() {
  const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
  const files = folder.getFiles();
  const result = [];
  while(files.hasNext()) {
    const file = files.next();
    const mime = file.getMimeType();
    
    // Filtramos solo PDF o Imagenes
    if (mime === MimeType.PDF || mime.indexOf('image') !== -1) {
      result.push({
        id: file.getId(),
        name: file.getName(),
        mimeType: mime,
        url: file.getUrl(),
        date: file.getDateCreated()
      });
    }
  }
  return result;
}

// Modificado para descargar la imagen directamente en un formato que el navegador puede leer
function getDriveFile(fileId) {
  try {
    const file = DriveApp.getFileById(fileId);
    const blob = file.getBlob();
    return {
      name: file.getName(),
      mimeType: file.getMimeType(),
      base64: Utilities.base64Encode(blob.getBytes())
    };
  } catch(e) {
    return {error: 'Archivo no encontrado'};
  }
}

// ================================================================
// OPERACIONES DE ESCRITURA (POST)
// ================================================================
function logAuditoria(user, action, details) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = getOrCreateSheet('AUDITORIA_LOG', ['TIMESTAMP', 'USER', 'ACTION', 'DETAILS']);
  sheet.appendRow([new Date().toISOString(), user, action, JSON.stringify(details)]);
}

function updateLogistics(data, user) {
  const logSheet = getOrCreateSheet('LOGISTICA', ['ID', 'JSON_DATA', 'LAST_UPDATED']);
  const values = logSheet.getDataRange().getValues();
  let rowIndex = -1;
  let existingData = {};
  
  const targetId = String(data.eventId);
  for (let i = 1; i < values.length; i++) {
    if (String(values[i][0]) === targetId) {
      rowIndex = i + 1;
      try {
        existingData = JSON.parse(values[i][1]);
      } catch (err) {}
      break;
    }
  }
  
  // Fusionar campos si ya existía información para no pisar campos no enviados
  const currentLogs = existingData.logistics || existingData || {};
  const newLogs = data.logistics || {};
  
  const mergedLogistics = {
    ticket: newLogs.ticket !== undefined ? newLogs.ticket : (currentLogs.ticket || 'pending'),
    hotel: newLogs.hotel !== undefined ? newLogs.hotel : (currentLogs.hotel || 'pending'),
    trainer_notified: newLogs.trainer_notified !== undefined ? (newLogs.trainer_notified === true || newLogs.trainer_notified === 'TRUE') : (currentLogs.trainer_notified === true || currentLogs.trainer_notified === 'TRUE'),
    trainer_arrival: newLogs.trainer_arrival !== undefined ? newLogs.trainer_arrival : (currentLogs.trainer_arrival || ''),
    ticket_url: newLogs.ticket_url !== undefined ? newLogs.ticket_url : (currentLogs.ticket_url || '')
  };
  
  // Compatibilidad con ambos formatos de guardado (plano y estructurado)
  const finalObject = {
    sede: data.sede || existingData.sede || 'LIM',
    fecha_inicio: data.fecha_inicio || existingData.fecha_inicio || '',
    fecha_fin: data.fecha_fin || existingData.fecha_fin || '',
    nombre: data.nombre || existingData.nombre || '',
    equipo: data.equipo || existingData.equipo || '',
    trainer: data.trainer || existingData.trainer || '',
    lugar: data.lugar || existingData.lugar || '',
    direccion: data.direccion || existingData.direccion || '',
    logistics: mergedLogistics,
    // Atributos planos para compatibilidad retrospectiva
    ticket: mergedLogistics.ticket,
    hotel: mergedLogistics.hotel,
    notified: mergedLogistics.trainer_notified,
    arrival: mergedLogistics.trainer_arrival,
    ticket_url: mergedLogistics.ticket_url
  };
  
  const payload = JSON.stringify(finalObject);
  const timestamp = new Date().toISOString();
  
  if (rowIndex > -1) {
    logSheet.getRange(rowIndex, 2, 1, 2).setValues([[payload, timestamp]]);
  } else {
    logSheet.appendRow([targetId, payload, timestamp]);
  }
  
  logAuditoria(user, 'UPDATE_LOGISTICS', data);
  return {success: true, message: 'Logística actualizada'};
}

function registerFlight(data, user) {
  // Envuelve updateLogistics
  const logisticsData = {
    eventId: data.eventId,
    logistics: {
      ticket: data.flightNumber || 'MATCHED',
      hotel: data.hotel || 'pending',
      ticket_url: data.ticket_url || '',
      trainer_notified: false
    }
  };
  return updateLogistics(logisticsData, user);
}

function uploadTicket(data, user) {
  try {
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    const blob = Utilities.newBlob(Utilities.base64Decode(data.base64), data.mimeType, data.filename);
    const file = folder.createFile(blob);
    
    // Si se envía el eventId, lo asignamos automáticamente
    if (data.eventId) {
      registerFlight({
        eventId: data.eventId,
        flightNumber: 'PDF EN DRIVE',
        ticket_url: file.getUrl()
      }, user);
    }
    
    logAuditoria(user, 'UPLOAD_TICKET', {filename: data.filename, fileId: file.getId()});
    return {success: true, url: file.getUrl(), id: file.getId()};
  } catch (err) {
    return {error: 'Fallo al subir archivo: ' + err.toString()};
  }
}

function batchUpdate(data, user) {
  if (!data.updates || !Array.isArray(data.updates)) {
    return {error: 'Formato batch inválido'};
  }
  let successCount = 0;
  data.updates.forEach(upd => {
    try {
      if (upd.eventId && upd.logistics) {
        // Individual update format
        updateLogistics(upd, user);
        successCount++;
      } else {
        // frontend map format: we extract each event's logistics and update them
        Object.keys(upd).forEach(sede => {
          if (Array.isArray(upd[sede])) {
            upd[sede].forEach(ev => {
              const startStr = ev.start || ev.fecha_inicio;
              if (startStr && ev.equipo) {
                const datePart = startStr.substring(0, 10).replace(/-/g, '');
                let SedePart = String(sede).toUpperCase().trim();
                if (SedePart.indexOf('UIO C1') !== -1 || SedePart.indexOf('QUITO C1') !== -1) {
                  SedePart = 'UIOC1';
                } else if (SedePart.indexOf('UIO C2') !== -1 || SedePart.indexOf('QUITO C2') !== -1) {
                  SedePart = 'UIOC2';
                } else {
                  SedePart = SedePart.substring(0, 3);
                  if (SedePart === 'CDM') SedePart = 'MEX';
                }
                
                // Clean team and extract digits
                let equipoRaw = String(ev.equipo || '').trim();
                let equipoClean = equipoRaw.replace(/[^0-9]/g, '');
                if (!equipoClean) equipoClean = equipoRaw;
                
                const targetId = `${SedePart}_E${equipoClean}_${datePart}`;
                
                const logistics = {
                  ticket: ev.ticket || 'pending',
                  hotel: ev.hotel || 'pending',
                  trainer_notified: ev.notified === true || ev.notified === 'TRUE',
                  trainer_arrival: ev.arrival || '',
                  ticket_url: ev.ticket_url || ''
                };
                
                updateLogistics({ eventId: targetId, logistics: logistics }, user);
                successCount++;
              }
            });
          }
        });
      }
    } catch(e) {}
  });
  logAuditoria(user, 'BATCH_UPDATE', {count: successCount});
  return {success: true, updated: successCount};
}

function replaceLogistica(data, user) {
  if (!data.updates || !Array.isArray(data.updates)) {
    return {error: 'Formato replace inválido'};
  }
  const sheet = getOrCreateSheet('LOGISTICA', ['ID', 'JSON_DATA', 'LAST_UPDATED']);
  sheet.clear();
  sheet.appendRow(['ID', 'JSON_DATA', 'LAST_UPDATED']);
  sheet.getRange('A1:C1').setFontWeight('bold');
  
  const rows = data.updates.map(u => [u.id, JSON.stringify(u.data), u.ts || new Date().getTime()]);
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, 3).setValues(rows);
  }
  logAuditoria(user, 'REPLACE_LOGISTICA', {count: rows.length});
  return {success: true, replaced: rows.length};
}

function crearRespaldoEnSheet(backupData) {
  try {
    const backupSheet = getOrCreateSheet('RESPALDO_GLOBAL', ['TIMESTAMP', 'JSON_BACKUP']);
    backupSheet.appendRow([new Date().toISOString(), JSON.stringify(backupData)]);
    return {success: true};
  } catch(err) {
    return {error: err.toString()};
  }
}

// ================================================================
// HELPER PARA CORS Y JSON
// ================================================================
function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
