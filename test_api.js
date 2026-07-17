async function checkData() {
    const url = 'https://script.google.com/macros/s/AKfycbyp0HQHjZR9zuAkfprmTUgRBNZJFu7JYnpVXUnZC3XBwJoU43f0Nc0RY_kKw_DYnPxN/exec?action=getEventos';
    const res = await fetch(url);
    const data = await res.json();
    
    data.forEach(ev => {
        if (!ev.nombre || typeof ev.nombre !== 'string') {
            console.log(ev.id, 'nombre:', ev.nombre, 'type:', typeof ev.nombre);
        }
    });
}

checkData();
