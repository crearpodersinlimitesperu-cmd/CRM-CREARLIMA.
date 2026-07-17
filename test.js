const fs = require('fs');
const url = 'https://script.google.com/macros/s/AKfycbyp0HQHjZR9zuAkfprmTUgRBNZJFu7JYnpVXUnZC3XBwJoU43f0Nc0RY_kKw_DYnPxN/exec?action=getEventos';
fetch(url).then(r => r.json()).then(flatData => {
    const sedeMap = {
        'Lima': 'LIM',
        'Quito': 'UIO C1',
        'Guayaquil': 'GYE',
        'Cuenca': 'CUE',
        'Medellin': 'MED',
        'Mexico': 'MEX'
    };
    const data = {};
    const uniqueEvents = new Map();
    flatData.forEach(ev => {
        const dedupKey = `${ev.sede}|${ev.fecha_inicio}|${ev.nombre}|${ev.trainer}`;
        if (!uniqueEvents.has(dedupKey)) {
            uniqueEvents.set(dedupKey, ev);
        } else {
            const existing = uniqueEvents.get(dedupKey);
            if (existing.equipo !== ev.equipo && !existing.equipo.includes(ev.equipo)) {
                existing.equipo += ' / ' + ev.equipo;
            }
        }
    });
    Array.from(uniqueEvents.values()).forEach(ev => {
        let key = sedeMap[ev.sede] || ev.sede;
        if (!data[key]) data[key] = [];
        data[key].push({
            start: ev.fecha_inicio,
            end: ev.fecha_fin,
            name: ev.nombre,
            equipo: ev.equipo,
            trainer: ev.trainer,
            place: ev.lugar,
            address: ev.direccion,
            logistics: {
                ticket: ev.ticket,
                hotel: ev.hotel,
                trainer_notified: ev.notified,
                trainer_arrival: ev.arrival,
                ticket_url: ev.ticket_url
            }
        });
    });
    fs.writeFileSync('test_data.json', JSON.stringify(data, null, 2));
    console.log('Success, data written to test_data.json. Keys:', Object.keys(data));
}).catch(console.error);
