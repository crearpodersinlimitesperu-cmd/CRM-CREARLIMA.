// ================================================================
// CREAR PODER SIN LIMITES - BACKEND API LOGISTICA GLOBAL v3.2
// Multi-pais + OCR + Tracking + Respaldo Automatico + Self-Healing
// ================================================================

const CONFIG = {
  SHEET_ID: '1u0tc4GeooPmSwNxZ0CErKGtRU4oD-mO3l--ZSQM-KPs',
  DRIVE_FOLDER_ID: '1opVrJrmZBuiSYSlVvTwAXb2Q1_SydvT7',
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
      case 'getFlightStatus':  result = getFlightStatus(e.parameter.flightNumber); break;
      case 'getAuditLog':      result = getAuditLog(parseInt(e.parameter.limit) || 50); break;
      case 'getDashboardKPIs': result = getDashboardKPIs(); break;
      case 'listDriveFiles':   result = listDriveFiles(); break;
      case 'getDriveFile':     result = getDriveFile(e.parameter.fileId); break;
      case 'health':           result = {status: 'ok', version: '3.2', timestamp: new Date().toISOString()}; break;
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
function getAllEventos() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const eventSheet = ss.getSheetByName('Hoja 2');
  if (!eventSheet) {
    return [];
  }
  
  // Cargar eventos base desde Hoja 2
  const eventValues = eventSheet.getDataRange().getValues();
  const eventDisplayValues = eventSheet.getDataRange().getDisplayValues();
  if (eventValues.length < 2) return [];
  const eventHeaders = eventValues[0];
  
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
    
    // Obtener los valores mostrados para evitar traer "=+D285+1" en vez de "26"
    const sede = String(eventDisplayValues[i][1] || 'LIM').trim();
    const equipo = String(eventDisplayValues[i][2] || '').trim();
    const nombre = String(eventDisplayValues[i][3] || '').trim();
    const trainer = String(eventDisplayValues[i][4] || '').trim();
    
    // Generar ID del evento compatible con frontend
    const datePart = dateStr.split('T')[0].replace(/-/g, '');
    const eventId = `${sede.substring(0, 3).toUpperCase()}_E${equipo}_${datePart}`;
    
    const log = logisticsMap[eventId] || {};
    
    let place = "";
    let address = "";
    if (sede === 'LIM') { place = "Lima"; address = "Lima, Perú"; }
    else if (sede === 'GYE') { place = "Guayaquil"; address = "Guayaquil, Ecuador"; }
    else if (sede.startsWith('UIO')) { place = "Quito"; address = "Quito, Ecuador"; }
    else if (sede === 'MED') { place = "Medellín"; address = "Medellín, Colombia"; }
    else if (sede === 'MEX') { place = "Ciudad de México"; address = "México DF"; }
    else if (sede === 'CUE') { place = "Cuenca"; address = "Cuenca, Ecuador"; }
    else { place = sede; address = ""; }

    // Leer columna H (índice 7) para lugar personalizado
    const lugarPersonalizado = eventDisplayValues[i][7] ? String(eventDisplayValues[i][7]).trim() : '';
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
      eventoId: eventId,
      fecha_inicio: dateStr,
      fecha_fin: endDateStr,
      nombre: nombre,
      equipo: equipo,
      trainer: trainer,
      sede: sede,
      lugar: place,
      direccion: address,
      ticket: log.ticket || 'pending',
      hotel: log.hotel || 'pending',
      notified: log.trainer_notified === 'TRUE' || log.trainer_notified === true || log.notified === 'TRUE' || log.notified === true,
      arrival: log.trainer_arrival || log.arrival || '',
      ticket_url: log.ticket_url || ''
    });
  }
  
  return result;
}

function getAllVuelos() {
  const sheet = getOrCreateSheet('VUELOS', [
    'ID_VUELO','EVENTO_ID','ENTRENADOR','AEROLINEA','NUMERO_VUELO',
    'ORIGEN','DESTINO','FECHA_SALIDA','HORA_SALIDA','FECHA_LLEGADA',
    'HORA_LLEGADA','PNR','STATUS','LAST_UPDATED'
  ]);
  return sheetToObjects(sheet);
}

function getAuditLog(limit) {
  if (!limit) limit = 50;
  const sheet = getOrCreateSheet('AUDITORIA', [
    'TIMESTAMP','ACCION','SEDE','EVENTO_ID','USUARIO','DETALLES'
  ]);
  const data  = sheetToObjects(sheet);
  return data.slice(-limit).reverse();
}

function getDashboardKPIs() {
  const eventos = getAllEventos();
  const vuelos  = getAllVuelos();
  const hoy     = new Date();

  const kpis = {
    total_eventos:           eventos.length,
    eventos_proximos:        eventos.filter(function(e){ return new Date(e.fecha_inicio) > hoy; }).length,
    tiquetes_comprados:      eventos.filter(function(e){ return e.ticket === 'purchased'; }).length,
    tiquetes_pendientes:     eventos.filter(function(e){ return e.ticket === 'pending'; }).length,
    hoteles_reservados:      eventos.filter(function(e){ return e.hotel === 'booked'; }).length,
    hoteles_pendientes:      eventos.filter(function(e){ return e.hotel === 'pending'; }).length,
    entrenadores_avisados:   eventos.filter(function(e){ return e.notified === 'TRUE' || e.notified === true; }).length,
    entrenadores_sin_avisar: eventos.filter(function(e){ return e.notified !== 'TRUE' && e.notified !== true; }).length,
    vuelos_activos:          vuelos.filter(function(v){ return ['landed','cancelled'].indexOf(v.estado_real) === -1; }).length,
    por_sede:                {}
  };

  var sedes = [];
  eventos.forEach(function(e){ if (sedes.indexOf(e.sede) === -1) sedes.push(e.sede); });
  sedes.forEach(function(sede) {
    var evSede = eventos.filter(function(e){ return e.sede === sede; });
    kpis.por_sede[sede] = {
      total:    evSede.length,
      proximos: evSede.filter(function(e){ return new Date(e.fecha_inicio) > hoy; }).length
    };
  });

  return kpis;
}

// ================================================================
// ESCRITURA DE DATOS
// ================================================================
function updateLogistics(data, user) {
  try {
    const sheet = getOrCreateSheet('LOGISTICA', ['ID', 'JSON_DATA', 'LAST_UPDATED']);
    const values = sheet.getDataRange().getValues();
    const idCol = 0;
    
    const targetId = String(data.eventoId || data.id);
    if (!targetId) return {error: 'Falta eventoId'};
    
    let foundRowIdx = -1;
    let existingLog = {};
    
    for (let i = 1; i < values.length; i++) {
      if (String(values[i][idCol]) === targetId) {
        foundRowIdx = i + 1; // 1-based row index
        try {
          existingLog = JSON.parse(values[i][1]);
        } catch(e) {}
        break;
      }
    }
    
    // Mezclar nuevos campos en la estructura existente de logística
    Object.keys(data).forEach(function(key) {
      if (['action', 'eventoId', '_audit'].indexOf(key) === -1) {
        // Mapear nombres si la petición usa nombres del frontend
        if (key === 'trainer_notified') {
          existingLog['trainer_notified'] = data[key];
          existingLog['notified'] = data[key] ? 'TRUE' : 'FALSE';
        } else if (key === 'trainer_arrival') {
          existingLog['trainer_arrival'] = data[key];
          existingLog['arrival'] = data[key];
        } else {
          existingLog[key] = data[key];
        }
      }
    });
    
    const jsonStr = JSON.stringify(existingLog);
    const nowStr = new Date().toISOString();
    
    if (foundRowIdx !== -1) {
      sheet.getRange(foundRowIdx, 2).setValue(jsonStr);
      sheet.getRange(foundRowIdx, 3).setValue(nowStr);
    } else {
      sheet.appendRow([targetId, jsonStr, nowStr]);
    }

    logAudit({accion: 'updateLogistics', sede: data.sede || '-', detalle: JSON.stringify(data), evento_id: targetId}, user);
    return {success: true, eventoId: targetId};
  } catch(err) {
    return {error: err.toString()};
  }
}

function registerFlight(data, user) {
  try {
    const sheet = getOrCreateSheet('VUELOS', [
      'ID_VUELO','EVENTO_ID','ENTRENADOR','AEROLINEA','NUMERO_VUELO',
      'ORIGEN','DESTINO','FECHA_SALIDA','HORA_SALIDA','FECHA_LLEGADA',
      'HORA_LLEGADA','PNR','STATUS','LAST_UPDATED'
    ]);

    sheet.appendRow([
      data.id_vuelo     || Utilities.getUuid(),
      data.evento_id    || '-',
      data.entrenador   || '-',
      data.aerolinea    || '-',
      data.numero_vuelo || '-',
      data.origen       || '-',
      data.destino      || '-',
      data.fecha_salida || '-',
      data.hora_salida  || '-',
      data.fecha_llegada || '-',
      data.hora_llegada  || '-',
      data.pnr          || '-',
      'scheduled',
      new Date().toISOString()
    ]);

    logAudit({accion: 'registerFlight', sede: data.sede || '-', detalle: data.numero_vuelo, evento_id: data.evento_id}, user);
    return {success: true, id_vuelo: data.id_vuelo};
  } catch(err) {
    return {error: err.toString()};
  }
}

function uploadTicket(data, user) {
  try {
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    const blob   = Utilities.newBlob(Utilities.base64Decode(data.base64), data.mimeType, data.fileName);
    const file   = folder.createFile(blob);
    logAudit({accion: 'uploadTicket', sede: data.sede || '-', detalle: data.fileName, evento_id: data.evento_id}, user);
    return {success: true, fileId: file.getId(), fileName: file.getName()};
  } catch(err) {
    return {error: err.toString()};
  }
}

function batchUpdate(data, user) {
  try {
    let count = 0;
    if (Array.isArray(data.updates)) {
      data.updates.forEach(function(upd) {
        updateLogistics(upd, user);
        count++;
      });
    }
    return {success: true, count: count};
  } catch(err) {
    return {error: err.toString()};
  }
}

function crearRespaldoEnSheet(backupData) {
  try {
    const sheet = getOrCreateSheet('RESPALDOS', [
      'TIMESTAMP','VERSION','EVENTOS_JSON','LOGISTICS_JSON','DRIVE_FILES_JSON'
    ]);
    sheet.appendRow([
      new Date().toISOString(),
      backupData.version || '2.0',
      JSON.stringify(backupData.allEventsData || {}),
      JSON.stringify(backupData.logistics || {}),
      JSON.stringify(backupData.processedDriveFiles || [])
    ]);
    return {success: true};
  } catch(err) {
    return {error: err.toString()};
  }
}

// ================================================================
// AUDITORIA Y PROXY DE GOOGLE DRIVE / FLIGHTS
// ================================================================
function logAudit(data, user) {
  try {
    const sheet = getOrCreateSheet('AUDITORIA', [
      'TIMESTAMP','ACCION','SEDE','EVENTO_ID','USUARIO','DETALLES'
    ]);
    sheet.appendRow([
      new Date().toISOString(),
      data.accion    || '-',
      data.sede      || '-',
      data.evento_id || '-',
      user           || 'anon@crearpsl.com',
      data.detalle   || '-'
    ]);
  } catch(e) {}
}

function getFlightStatus(flightNumber) {
  try {
    if (!flightNumber || flightNumber === '-') return {error: 'Numero de vuelo invalido'};
    const cleaned = flightNumber.replace(/\s+/g, '');
    const url = 'http://api.aviationstack.com/v1/flights?access_key=' + CONFIG.AVIATIONSTACK_KEY + '&flight_iata=' + cleaned;
    const res = UrlFetchApp.fetch(url);
    const data = JSON.parse(res.getContentText());
    if (data && data.data && data.data.length > 0) {
      const f = data.data[0];
      return {
        aerolinea:   f.airline ? f.airline.name : '-',
        numero:      cleaned,
        origen:      f.departure ? f.departure.airport : '-',
        destino:     f.arrival ? f.arrival.airport : '-',
        estado_real: f.flight_status || 'scheduled',
        salida_est:  f.departure ? f.departure.estimated : '-',
        llegada_est: f.arrival ? f.arrival.estimated : '-'
      };
    }
    return {error: 'No se encontraron datos en Aviationstack'};
  } catch(err) {
    return {error: err.toString()};
  }
}

function listDriveFiles() {
  try {
    const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
    const files  = folder.getFiles();
    const fileList = [];
    let count = 0;
    while (files.hasNext() && count < 100) {
      const file = files.next();
      fileList.push({
        id:       file.getId(),
        name:     file.getName(),
        mimeType: file.getMimeType(),
        created:  file.getDateCreated().toISOString()
      });
      count++;
    }
    return {files: fileList, count: fileList.length, total_scanned: count};
  } catch(err) {
    return {error: err.toString(), files: []};
  }
}

function getDriveFile(fileId) {
  try {
    const file   = DriveApp.getFileById(fileId);
    const blob   = file.getBlob();
    const base64 = Utilities.base64Encode(blob.getBytes());
    return {
      id:       fileId,
      name:     file.getName(),
      mimeType: file.getMimeType(),
      base64:   base64
    };
  } catch(err) {
    return {error: err.toString()};
  }
}

// ================================================================
// UTILIDADES COMUNES
// ================================================================
function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

function sheetToObjects(sheet) {
  if (!sheet) return [];
  const values  = sheet.getDataRange().getValues();
  if (values.length < 2) return [];
  const headers = values[0];
  const result  = [];
  for (let i = 1; i < values.length; i++) {
    const obj = {};
    headers.forEach(function(h, j){ obj[h] = values[i][j]; });
    result.push(obj);
  }
  return result;
}

// Trigger automatico de vuelos (A ejecutar cada 10 min)
function checkAllVuelosAutomatic() {
  try {
    const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
    const sheet = getOrCreateSheet('VUELOS', [
      'ID_VUELO','EVENTO_ID','ENTRENADOR','AEROLINEA','NUMERO_VUELO',
      'ORIGEN','DESTINO','FECHA_SALIDA','HORA_SALIDA','FECHA_LLEGADA',
      'HORA_LLEGADA','PNR','STATUS','LAST_UPDATED'
    ]);
    const values = sheet.getDataRange().getValues();
    const headers = values[0];
    const numCol = headers.indexOf('NUMERO_VUELO');
    const statusCol = headers.indexOf('STATUS');
    
    if (numCol === -1 || statusCol === -1) return;
    
    for (let i = 1; i < values.length; i++) {
      const flightNum = values[i][numCol];
      const status = values[i][statusCol];
      
      if (flightNum && flightNum !== '-' && ['landed','cancelled'].indexOf(status) === -1) {
        const info = getFlightStatus(flightNum);
        if (info && !info.error && info.estado_real) {
          sheet.getRange(i + 1, statusCol + 1).setValue(info.estado_real);
          const updCol = headers.indexOf('LAST_UPDATED');
          if (updCol !== -1) {
            sheet.getRange(i + 1, updCol + 1).setValue(new Date().toISOString());
          }
        }
      }
    }
  } catch(e) {}
}

function createTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  let found = false;
  triggers.forEach(function(t) {
    if (t.getHandlerFunction() === 'checkAllVuelosAutomatic') found = true;
  });
  if (!found) {
    ScriptApp.newTrigger('checkAllVuelosAutomatic')
      .timeBased()
      .everyMinutes(5)
      .create();
  }
}

function initialize() {
  createTrigger();
  Logger.log('Sistema inicializado correctamente - v3.2');
}
