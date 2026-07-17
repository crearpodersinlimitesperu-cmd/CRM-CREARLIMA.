// ═══════════════════════════════════════════════════════════════
// MIGRACIÓN DE EVENTOS AL GOOGLE SHEET
// Ejecutar en la consola del navegador con el calendario abierto
// ═══════════════════════════════════════════════════════════════
(function migrarEventosASheet() {
  const eventos = [];
  Object.keys(allEventsData).forEach(sede => {
    allEventsData[sede].forEach(ev => {
      const id = `${sede.substring(0,3).toUpperCase()}_E${ev.equipo}_${ev.start.replace(/-/g,'').substring(0,8)}`;
      eventos.push({
        id,
        sede,
        nombre: ev.name,
        equipo: ev.equipo,
        trainer: ev.trainer || '',
        fecha_inicio: ev.start.split('T')[0],
        fecha_fin: ev.end.split('T')[0],
        lugar: ev.place || '',
        direccion: ev.address || '',
        ticket: ev.logistics?.ticket || 'pending',
        hotel: ev.logistics?.hotel || 'pending',
        notified: ev.logistics?.trainer_notified ? 'TRUE' : 'FALSE',
        arrival: ev.logistics?.trainer_arrival || '',
        ticket_url: ev.logistics?.ticket_url || ''
      });
    });
  });
  
  // Generar CSV con BOM para Excel
  const headers = ['id','sede','nombre','equipo','trainer','fecha_inicio','fecha_fin','lugar','direccion','ticket','hotel','notified','arrival','ticket_url'];
  const csv = [
    headers.join(','),
    ...eventos.map(e => headers.map(h => `"${String(e[h]).replace(/"/g,'""')}"`).join(','))
  ].join('\n');
  
  const blob = new Blob(["\ufeff" + csv], {type: 'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `CREAR_Eventos_Migracion_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  
  console.log(`✅ ${eventos.length} eventos exportados. Importa este CSV en tu Google Sheet (Hoja EVENTOS).`);
})();
