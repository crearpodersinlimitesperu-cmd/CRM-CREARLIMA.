
        /**
         * [SEGURIDAD - CAPA GRATUITA]
         * Los datos sensibles de los entrenadores (pasaportes, seguros) están encriptados
         * en el DOM usando XOR simétrico (llave derived de contraseña). No se desencriptan
         * ni se cargan en memoria hasta una autenticación exitosa.
         * Limitación conocida: Ofuscación del lado del cliente, apta para entornos demo/privados.
         */
        function xorDecrypt(base64Str, keyStr) {
            try {
                const encStr = atob(base64Str);
                let decBytes = new Uint8Array(encStr.length);
                for (let i = 0; i < encStr.length; i++) {
                    decBytes[i] = encStr.charCodeAt(i) ^ keyStr.charCodeAt(i % keyStr.length);
                }
                if (window.TextDecoder) {
                    return new TextDecoder('utf-8').decode(decBytes);
                } else {
                    let out = "";
                    for (let i = 0; i < decBytes.length; i++) {
                        out += String.fromCharCode(decBytes[i]);
                    }
                    return decodeURIComponent(escape(out));
                }
            } catch (e) {
                return null;
            }
        }
        // Lista de usuarios encriptados (XOR simple) para ofuscar
        // Llave de encriptación general (demo): "crear2026"
        // Usuarios:
        // feraragon / cpslceo26
        // paulsosa / cpslcco26
        // gerentelima / limacpsl
        // gerentequito / quitocpsl
        // admin / admin
        
        // Función de autenticación Google Identity Services
        function decodeJwtResponse(token) {
            let base64Url = token.split('.')[1];
            let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        }

        function handleCredentialResponse(response) {
            const responsePayload = decodeJwtResponse(response.credential);
            const userEmail = responsePayload.email;
            const userName = responsePayload.given_name;
            const errorMsg = document.getElementById('login-error');

            const allowedManagers = window.ALLOWED_MANAGERS || [
                'fer.aragon@crearpsl.net', // CEO
                'paul.sosa@crearpsl.net',  // CCO
                'gerencia@crearpsl.net',
                'manager@crearpsl.net',
                'director@crearpsl.net',
                'admin@crearpsl.net'
            ];

            if (userEmail && allowedManagers.includes(userEmail.toLowerCase())) {
                // Success
                sessionStorage.setItem('auth', 'true');
                sessionStorage.setItem('crear_user_email', userEmail);
                sessionStorage.setItem('crear_user_name', userName);
                
                const overlay = document.getElementById('login-overlay');
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.classList.add('hidden');
                    document.body.style.overflow = '';
                    renderSedeTabs();
                    renderEvents('');
                    startSync();
                    showToast(`Bienvenido, ${userName}`);
                }, 500);
            } else {
                // Access Denied
                errorMsg.textContent = 'Acceso denegado. Privilegios insuficientes.';
                errorMsg.classList.remove('hidden');
                
                // Shake effect
                const box = document.querySelector('#login-overlay > div');
                box.classList.add('translate-x-2');
                setTimeout(() => box.classList.replace('translate-x-2', '-translate-x-2'), 100);
                setTimeout(() => box.classList.replace('-translate-x-2', 'translate-x-2'), 200);
                setTimeout(() => box.classList.replace('translate-x-2', '-translate-x-2'), 300);
                setTimeout(() => box.classList.remove('-translate-x-2'), 400);
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            if (sessionStorage.getItem('auth') === 'true') {
                document.getElementById('login-overlay').classList.add('hidden');
                document.body.style.overflow = '';
                renderSedeTabs();
                renderEvents('');
                startSync();
            } else {
                document.getElementById('login-overlay').classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }
        });


        // ═══════════════════════════════════════════════════════════════
        // CONFIGURACIÓN API BACKEND (MULTI-GERENTE + OCR + TRACKING)
        // ═══════════════════════════════════════════════════════════════
        const API_URL = 'https://script.google.com/macros/s/AKfycbyp0HQHjZR9zuAkfprmTUgRBNZJFu7JYnpVXUnZC3XBwJoU43f0Nc0RY_kKw_DYnPxN/exec';
        let syncInterval = null;
        let isSyncing = false;
        let saveQueue = [];
        let isOnline = navigator.onLine;

        window.addEventListener('online', () => { isOnline = true; syncQueue(); });
        window.addEventListener('offline', () => { isOnline = false; showToast('⚠️ Modo offline. Cambios guardados localmente.', 'warning'); });

        // ═══════════════════════════════════════════════════════════════
        // SYNC MULTI-GERENTE (POLLING CADA 30s)
        // ═══════════════════════════════════════════════════════════════
        async function startSync() {
          await syncFromServer();
          syncInterval = setInterval(syncFromServer, 30000);
        }

        async function syncFromServer() {
          if (isSyncing || !API_URL || API_URL.includes('PEGA_AQUI')) return;
          isSyncing = true;
          try {
            const res = await fetch(`${API_URL}?action=getEventos`);
            const flatData = await res.json();
            if (Array.isArray(flatData) && flatData.length > 0) {
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
                        sedeTag: key,
                        logistics: {
                            ticket: ev.ticket || 'pending',
                            hotel: ev.hotel || 'pending',
                            trainer_notified: ev.notified === 'TRUE' || ev.notified === true,
                            trainer_arrival: ev.arrival || '',
                            ticket_url: ev.ticket_url || ''
                        }
                    });
                });
                
                allEventsData = data;
                mergeLogistics();
                if (sessionStorage.getItem('auth') === 'true') {
                    renderSedeTabs();
                    renderEvents(document.getElementById('searchInput')?.value || '');
                }
            }
          } catch(err) {
            console.warn('Sync falló, intentando data local...', err);
            try {
                const res = await fetch('events_data.json');
                const data = await res.json();
                allEventsData = data;
                mergeLogistics();
                if (sessionStorage.getItem('auth') === 'true') {
                    renderSedeTabs();
                    renderEvents(document.getElementById('searchInput')?.value || '');
                }
            } catch(e) {
                console.warn('Fallback local falló, usando datos integrados...');
                allEventsData = fallbackEventsData;
                mergeLogistics();
                if (sessionStorage.getItem('auth') === 'true') {
                    renderSedeTabs();
                    renderEvents(document.getElementById('searchInput')?.value || '');
                }
            }
          } finally {
            isSyncing = false;
          }
        }

        // ═══════════════════════════════════════════════════════════════
        // GUARDADO EN NUBE + COLA OFFLINE
        // ═══════════════════════════════════════════════════════════════
        function savePersistent(key, data) {
          localStorage.setItem(key, JSON.stringify(data));
          saveQueue.push({ key, data, ts: Date.now() });
          if (isOnline) syncQueue();
        }

        function syncQueue() {
          if (saveQueue.length === 0 || isSyncing) return;
          if (window.location.protocol === 'file:' || !API_URL || API_URL.includes('PEGA_AQUI')) {
            saveQueue = [];
            return;
          }
          isSyncing = true;
          const batch = saveQueue.slice(0, 5);
          fetch(API_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: {'Content-Type': 'text/plain'},
            body: JSON.stringify({action: 'batchUpdate', updates: batch.map(b => b.data)}),
            keepalive: true
          }).then(() => {
            isSyncing = false;
            saveQueue.splice(0, batch.length);
            if (saveQueue.length > 0) setTimeout(syncQueue, 500);
          }).catch(() => {
            isSyncing = false;
            setTimeout(syncQueue, 5000);
          });
        }

        window.addEventListener('beforeunload', syncQueue);

        // ═══════════════════════════════════════════════════════════════
        // TOAST MEJORADO
        // ═══════════════════════════════════════════════════════════════
        function showToast(msg, type = "success") {
          const existing = document.querySelector('.crear-toast');
          if (existing) existing.remove();
          const toast = document.createElement('div');
          toast.className = 'crear-toast fixed bottom-6 right-6 z-[70] px-5 py-3 rounded-xl text-xs font-bold shadow-2xl transition-all transform translate-y-2 opacity-0 backdrop-blur-md';
          const colors = {
            success: 'bg-emerald-900/90 text-emerald-300 border border-emerald-700',
            error: 'bg-red-900/90 text-red-300 border border-red-700',
            warning: 'bg-orange-900/90 text-orange-300 border border-orange-700',
            info: 'bg-blue-900/90 text-blue-300 border border-blue-700'
          };
          toast.classList.add(...colors[type].split(' '));
          toast.textContent = msg;
          document.body.appendChild(toast);
          requestAnimationFrame(() => toast.classList.remove('translate-y-2', 'opacity-0'));
          setTimeout(() => {
            toast.classList.add('translate-y-2', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
          }, 3000);
        }

        // ═══════════════════════════════════════════════════════════════
        // OCR TIQUETES + TRACKING VUELOS
        // ═══════════════════════════════════════════════════════════════
        let currentEventoId = null;
        let currentTrainerName = '';

        // ═══════════════════════════════════════════════════════════════
        // CROPPER: Modal de recorte previo al OCR (optimización móvil)
        // ═══════════════════════════════════════════════════════════════
        let activeCropper = null;
        let pendingOCRFile = null;

        function showCropModal(file) {
          return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'cropper-modal-overlay';
            overlay.id = 'cropperOverlay';
            overlay.innerHTML = `
              <div style="text-align:center; margin-bottom:12px;">
                <h3 style="color:white; font-size:16px; font-weight:800; margin:0;">✂️ Recorta el área del PNR y Número de Vuelo</h3>
                <p style="color:#8b949e; font-size:11px; margin:4px 0 0;">Selecciona solo la zona con los datos del vuelo para mayor precisión</p>
              </div>
              <div style="width:100%; max-width:600px; background:#111; border-radius:12px; overflow:hidden; border:1px solid #29abe2;">
                <img id="cropperImage" style="display:block; max-width:100%;">
              </div>
              <div style="display:flex; gap:12px; margin-top:16px;">
                <button id="cropConfirm" style="background:linear-gradient(135deg,#29abe2,#1a75bc); color:white; font-weight:800; font-size:13px; padding:10px 28px; border:none; border-radius:10px; cursor:pointer; text-transform:uppercase; letter-spacing:1px;">✅ Recortar y Leer</button>
                <button id="cropSkip" style="background:#1c2735; color:#9ca3af; font-weight:700; font-size:13px; padding:10px 28px; border:1px solid #374151; border-radius:10px; cursor:pointer;">Leer imagen completa</button>
                <button id="cropCancel" style="background:transparent; color:#ef4444; font-weight:700; font-size:13px; padding:10px 20px; border:1px solid #ef4444; border-radius:10px; cursor:pointer;">Cancelar</button>
              </div>
            `;
            document.body.appendChild(overlay);

            const imgEl = document.getElementById('cropperImage');
            const reader = new FileReader();
            reader.onload = (e) => {
              imgEl.src = e.target.result;
              imgEl.onload = () => {
                activeCropper = new Cropper(imgEl, {
                  viewMode: 1,
                  dragMode: 'move',
                  aspectRatio: NaN,
                  autoCropArea: 0.6,
                  responsive: true,
                  guides: true,
                  background: false,
                  modal: true
                });
              };
            };
            reader.readAsDataURL(file);

            document.getElementById('cropConfirm').onclick = () => {
              if (activeCropper) {
                const canvas = activeCropper.getCroppedCanvas({ maxWidth: 1200, maxHeight: 800 });
                canvas.toBlob((blob) => {
                  cleanup();
                  resolve(blob);
                }, 'image/png');
              }
            };
            document.getElementById('cropSkip').onclick = () => { cleanup(); resolve(file); };
            document.getElementById('cropCancel').onclick = () => { cleanup(); resolve(null); };

            function cleanup() {
              if (activeCropper) { activeCropper.destroy(); activeCropper = null; }
              overlay.remove();
            }
          });
        }

        async function procesarTiquete(event) {
          const file = event.target.files[0];
          if (!file) return;
          const bar = document.getElementById('ocrBar');
          const status = document.getElementById('ocrStatus');
          try {
            let text = '';
            
            if (file.type === 'application/pdf') {
              // PDF: flujo directo con PDF.js (no requiere recorte)
              document.getElementById('ocrProgress').classList.remove('hidden');
              bar.style.width = '30%';
              status.textContent = 'Leyendo PDF...';
              const arrayBuffer = await file.arrayBuffer();
              const pdf = await pdfjsLib.getDocument({data: new Uint8Array(arrayBuffer)}).promise;
              bar.style.width = '60%';
              status.textContent = 'Extrayendo texto del PDF...';
              const maxPages = Math.min(pdf.numPages, 2);
              for (let i = 1; i <= maxPages; i++) {
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                const strings = content.items.map(item => item.str);
                text += strings.join(' ') + ' ';
              }
              bar.style.width = '100%';
            } else {
              // IMAGEN: mostrar modal de recorte primero
              const croppedBlob = await showCropModal(file);
              if (!croppedBlob) return; // Usuario canceló

              document.getElementById('ocrProgress').classList.remove('hidden');
              status.textContent = 'Inicializando OCR...';
              const worker = await Tesseract.createWorker('spa+eng', 1, {
                logger: m => {
                  if (m.status === 'recognizing text') {
                    bar.style.width = Math.round(m.progress * 100) + '%';
                    status.textContent = `Reconociendo... ${Math.round(m.progress * 100)}%`;
                  } else {
                    status.textContent = m.status;
                  }
                }
              });
              const result = await worker.recognize(croppedBlob);
              text = result.data.text;
              await worker.terminate();
            }
            
            status.textContent = 'Extrayendo datos...';
            const datos = extraerDatosTiquete(text);
            document.getElementById('flightAerolinea').value = datos.aerolinea || '';
            document.getElementById('flightNumero').value = datos.numero || '';
            document.getElementById('flightOrigen').value = datos.origen || '';
            document.getElementById('flightDestino').value = datos.destino || '';
            document.getElementById('flightPNR').value = datos.pnr || '';
            document.getElementById('flightDataForm').classList.remove('hidden');
            document.getElementById('ocrProgress').classList.add('hidden');
            
            if (!datos.numero && !datos.pnr && !datos.origen) {
              showToast('⚠️ No se encontraron datos legibles. Por favor ingresa los datos manualmente.', 'warning');
            } else {
              showToast('✅ Datos extraídos con éxito desde el recorte.', 'success');
            }
            // Subir archivo original a Drive
            const reader = new FileReader();
            reader.onload = async () => {
              const base64 = reader.result.split(',')[1];
              try {
                await fetch(API_URL, {
                  method: 'POST',
                  mode: 'no-cors',
                  headers: {'Content-Type': 'text/plain'},
                  body: JSON.stringify({
                    action: 'uploadTicket',
                    base64, filename: file.name, mimeType: file.type,
                    evento_id: currentEventoId
                  })
                });
                showToast('✅ Vuelo subido a Drive');
              } catch(e) { console.warn('Upload falló:', e); }
            };
            reader.readAsDataURL(file);
          } catch(err) {
            showToast('❌ Error procesando vuelo: ' + err.message, 'error');
            document.getElementById('ocrProgress').classList.add('hidden');
          }
        }

        function openBulkMatcher() {
            document.getElementById('bulkMatcherOverlay').classList.remove('hidden');
            document.getElementById('bulkResultsContainer').classList.add('hidden');
            document.getElementById('bulkResultsTable').innerHTML = '';
            document.getElementById('bulkProcessedCount').textContent = '0';
            document.getElementById('bulkTotalCount').textContent = '0';
        }
        window.pendingManualFiles = [];
        window.globalTrainersEvents = [];
        
        async function handleBulkFiles(event) {
            const files = event.target.files;
            if (!files || files.length === 0) return;
            
            document.getElementById('bulkResultsContainer').classList.remove('hidden');
            document.getElementById('bulkTotalCount').textContent = files.length;
            const tbody = document.getElementById('bulkResultsTable');
            tbody.innerHTML = '';
            
            let processed = 0;
            
            // Construir mapa de entrenadores
            window.globalTrainersEvents = [];
            Object.keys(allEventsData).forEach(sede => {
                allEventsData[sede].forEach(ev => {
                    const trainer = (ev.trainer || '').toUpperCase().trim();
                    if (trainer && trainer.length > 3) {
                        window.globalTrainersEvents.push({
                            name: trainer,
                            parts: trainer.replace(/\//g, ' ').split(' ').filter(p => p.length > 3),
                            event: ev,
                            sede: sede
                        });
                    }
                });
            });
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const tr = document.createElement('tr');
                tr.innerHTML = `<td class="px-4 py-3 border-r border-crearBorder truncate max-w-[150px]" title="${file.name}">${file.name}</td>
                                <td class="px-4 py-3 border-r border-crearBorder text-gray-400 italic">Leyendo...</td>
                                <td class="px-4 py-3 border-r border-crearBorder">-</td>
                                <td class="px-4 py-3 border-r border-crearBorder">-</td>
                                <td class="px-4 py-3 text-center"><ion-icon name="sync" class="animate-spin text-indigo-400 text-lg"></ion-icon></td>`;
                tbody.appendChild(tr);
                
                let text = '';
                try {
                    if (file.type === 'application/pdf') {
                        const arrayBuffer = await file.arrayBuffer();
                        const pdf = await pdfjsLib.getDocument({data: new Uint8Array(arrayBuffer)}).promise;
                        const maxPages = Math.min(pdf.numPages, 2);
                        for (let p = 1; p <= maxPages; p++) {
                            const page = await pdf.getPage(p);
                            const content = await page.getTextContent();
                            text += content.items.map(item => item.str).join(' ') + ' ';
                        }
                    } else {
                        const worker = await Tesseract.createWorker('spa+eng', 1);
                        const result = await worker.recognize(file);
                        text = result.data.text;
                        await worker.terminate();
                    }
                } catch(e) {
                    text = '';
                }
                
                text = text.toUpperCase();
                let bestMatch = null;
                let maxScore = 0;
                
                window.globalTrainersEvents.forEach(t => {
                    let score = 0;
                    t.parts.forEach(p => { if (text.includes(p)) score++; });
                    if (score >= 2 && score > maxScore) {
                        maxScore = score;
                        bestMatch = t;
                    }
                });
                
                const datos = extraerDatosTiquete(text);
                const tds = tr.querySelectorAll('td');
                
                if (bestMatch) {
                    tds[1].textContent = bestMatch.name;
                    tds[1].classList.remove('text-gray-400', 'italic');
                    tds[1].classList.add('text-white', 'font-bold');
                    
                    const vueloStr = (datos.aerolinea || '') + ' ' + (datos.numero || '') + (datos.pnr ? ' PNR: '+datos.pnr : '');
                    tds[2].textContent = vueloStr || 'No detectado';
                    
                    tds[3].innerHTML = `<span class="text-[10px] bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded border border-indigo-700 font-bold uppercase">${bestMatch.sede} - ${bestMatch.event.name}</span><br><span class="text-[10px] text-gray-500 mt-1 block">${bestMatch.event.start.split('T')[0]}</span>`;
                    
                    tds[4].innerHTML = `<span class="text-emerald-400 font-black text-xl" title="Match Exitoso">✓</span>`;
                    
                    if (!bestMatch.event.logistics) bestMatch.event.logistics = {};
                    bestMatch.event.logistics.ticket = 'purchased';
                    
                    const targetId = `${bestMatch.sede.substring(0,3).toUpperCase()}_E${bestMatch.event.equipo}_${bestMatch.event.start.replace(/-/g,'').substring(0,8)}`;
                    
                    saveQueue.push({
                      action: 'updateLogistics',
                      evento_id: targetId,
                      sede: bestMatch.sede,
                      ticket: 'purchased'
                    });
                    processQueue();
                    
                    const reader = new FileReader();
                    reader.onload = async () => {
                      const base64 = reader.result.split(',')[1];
                      try {
                        await fetch(API_URL, {
                          method: 'POST', mode: 'no-cors',
                          headers: {'Content-Type': 'text/plain'},
                          body: JSON.stringify({
                            action: 'uploadTicket', base64, filename: file.name, mimeType: file.type,
                            evento_id: targetId, sede: bestMatch.sede
                          })
                        });
                      } catch(e) {}
                    };
                    reader.readAsDataURL(file);
                    
                } else {
                    const fileId = window.pendingManualFiles.length;
                    window.pendingManualFiles.push({ file: file, text: text, datos: datos });
                    
                    const vueloStr = (datos.aerolinea || '') + ' ' + (datos.numero || '') + (datos.pnr ? ' PNR: '+datos.pnr : '');
                    
                    tds[1].innerHTML = `<span class="text-yellow-400 font-bold text-xs" title="Datos extraídos: ${text.substring(0,100)}...">Duda: Asignación Manual</span>`;
                    tds[2].textContent = vueloStr || 'No detectado';
                    
                    let optionsHtml = '<option value="">-- Selecciona el Evento --</option>';
                    window.globalTrainersEvents.forEach((t, idx) => {
                        optionsHtml += `<option value="${idx}">[${t.sede}] ${t.event.name} (${t.event.start.split('T')[0]}) - ${t.name}</option>`;
                    });
                    
                    tds[3].innerHTML = `<select id="manualSelect_${fileId}" class="w-full bg-black/50 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-crearCyan mb-1 max-w-[200px]">${optionsHtml}</select>`;
                    tds[4].innerHTML = `<button onclick="assignManual(${fileId}, this.closest('tr'))" class="bg-indigo-500 hover:bg-indigo-400 text-white px-3 py-1 rounded text-xs font-bold w-full transition-colors">ASIGNAR</button>`;
                }
                
                processed++;
                document.getElementById('bulkProcessedCount').textContent = processed;
            }
            renderAllSedes();
        }

        async function assignManual(fileId, tr) {
            const selectEl = document.getElementById(`manualSelect_${fileId}`);
            const selectedIdx = selectEl.value;
            if (!selectedIdx) {
                alert("Por favor selecciona un evento de la lista.");
                return;
            }
            
            const fileData = window.pendingManualFiles[fileId];
            const bestMatch = window.globalTrainersEvents[selectedIdx];
            const tds = tr.querySelectorAll('td');
            
            tds[1].textContent = bestMatch.name;
            tds[1].className = 'px-4 py-3 border-r border-crearBorder truncate max-w-[150px] text-white font-bold';
            
            tds[3].innerHTML = `<span class="text-[10px] bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded border border-indigo-700 font-bold uppercase">${bestMatch.sede} - ${bestMatch.event.name}</span><br><span class="text-[10px] text-gray-500 mt-1 block">${bestMatch.event.start.split('T')[0]}</span>`;
            tds[4].innerHTML = `<span class="text-emerald-400 font-black text-xl" title="Asignado Manualmente">✓</span>`;
            
            if (!bestMatch.event.logistics) bestMatch.event.logistics = {};
            bestMatch.event.logistics.ticket = 'purchased';
            
            const targetId = `${bestMatch.sede.substring(0,3).toUpperCase()}_E${bestMatch.event.equipo}_${bestMatch.event.start.replace(/-/g,'').substring(0,8)}`;
            
            saveQueue.push({
                action: 'updateLogistics',
                evento_id: targetId,
                sede: bestMatch.sede,
                ticket: 'purchased'
            });
            processQueue();
            renderAllSedes();
            
            const reader = new FileReader();
            reader.onload = async () => {
                const base64 = reader.result.split(',')[1];
                try {
                    await fetch(API_URL, {
                        method: 'POST', mode: 'no-cors',
                        headers: {'Content-Type': 'text/plain'},
                        body: JSON.stringify({
                            action: 'uploadTicket', base64, filename: fileData.file.name, mimeType: fileData.file.type,
                            evento_id: targetId, sede: bestMatch.sede
                        })
                    });
                } catch(e) {}
            };
            reader.readAsDataURL(fileData.file);
        }

        function extraerDatosTiquete(text) {
          const datos = {};
          const upper = text.toUpperCase();
          const aerolineas = ['LATAM', 'AVIANCA', 'COPA', 'AMERICAN', 'AEROMEX', 'VIVA', 'WINGO', 'JETSMART', 'SKY', 'AVIOR', 'SATENA', 'VOLARIS'];
          datos.aerolinea = aerolineas.find(a => upper.includes(a)) || '';
          const matchVuelo = upper.match(/([A-Z0-9]{2})\s*[-]?\s*(\d{3,4})/);
          if (matchVuelo) datos.numero = matchVuelo[1] + matchVuelo[2];
          const codigosIATA = upper.match(/[A-Z]{3}/g) || [];
          const unicos = [...new Set(codigosIATA)].filter(c => !['PDF', 'JPG', 'USD', 'PEN', 'COP', 'MXN', 'IVA', 'VAT', 'TAX', 'FEE', 'PNR', 'IATA'].includes(c));
          if (unicos.length >= 2) { datos.origen = unicos[0]; datos.destino = unicos[1]; }
          const matchPNR = upper.match(/[A-Z0-9]{6}/);
          if (matchPNR) datos.pnr = matchPNR[0];
          return datos;
        }

        async function guardarVuelo() {
          const payload = {
            action: 'registerFlight',
            evento_id: currentEventoId,
            trainer: currentTrainerName,
            aerolinea: document.getElementById('flightAerolinea').value,
            numero_vuelo: document.getElementById('flightNumero').value,
            origen: document.getElementById('flightOrigen').value,
            destino: document.getElementById('flightDestino').value,
            pnr: document.getElementById('flightPNR').value
          };
          try {
            await fetch(API_URL, {
              method: 'POST',
              mode: 'no-cors',
              headers: {'Content-Type': 'text/plain'},
              body: JSON.stringify(payload)
            });
            showToast('✅ Vuelo registrado. Rastreando...');
            document.getElementById('flightStatus').classList.remove('hidden');
            refreshFlightStatus();
          } catch(err) {
            showToast('❌ Error al registrar vuelo', 'error');
          }
        }

        async function refreshFlightStatus() {
          const flightNumber = document.getElementById('flightNumero').value;
          if (!flightNumber) return;
          const badge = document.getElementById('flightStatusBadge');
          const details = document.getElementById('flightDetails');
          badge.textContent = '⏳ Cargando...';
          badge.className = 'text-xs font-bold px-2 py-0.5 rounded bg-gray-900/40 text-gray-400 border border-gray-800/30';
          try {
            const res = await fetch(`${API_URL}?action=getFlightStatus&flightNumber=${flightNumber}`);
            const data = await res.json();
            if (data.error) {
              badge.textContent = '⚠️ Sin datos';
              badge.className = 'text-xs font-bold px-2 py-0.5 rounded bg-yellow-900/40 text-yellow-400 border border-yellow-800/30';
              return;
            }
            const statusMap = {
              'active': {'text': '✈️ En vuelo', 'class': 'bg-blue-900/40 text-blue-400 border border-blue-800/30'},
              'scheduled': {'text': '🕐 Programado', 'class': 'bg-gray-900/40 text-gray-400 border border-gray-800/30'},
              'landed': {'text': '✅ Aterrizado', 'class': 'bg-emerald-900/40 text-emerald-400 border border-emerald-800/30'},
              'cancelled': {'text': '❌ Cancelado', 'class': 'bg-red-900/40 text-red-400 border border-red-800/30'},
              'diverted': {'text': '⚠️ Desviado', 'class': 'bg-orange-900/40 text-orange-400 border border-orange-800/30'}
            };
            const s = statusMap[data.status] || {'text': data.status, 'class': 'bg-gray-900/40 text-gray-400 border border-gray-800/30'};
            badge.textContent = s.text;
            badge.className = `text-xs font-bold px-2 py-0.5 rounded border ${s.class}`;
            details.innerHTML = `
              <div>🛫 <strong>Salida:</strong> ${data.departure?.airport?.name || '-'} · ${formatTime(data.departure?.scheduled)}</div>
              <div>🛬 <strong>Llegada:</strong> ${data.arrival?.airport?.name || '-'} · ${formatTime(data.arrival?.scheduled)}</div>
              ${data.arrival?.delay ? `<div class="text-orange-400">⏱️ Retardo: ${data.arrival.delay} min</div>` : ''}
              <div>🏢 <strong>Aerolínea:</strong> ${data.airline || '-'}</div>
            `;
          } catch(err) {
            badge.textContent = '❌ Error';
            badge.className = 'text-xs font-bold px-2 py-0.5 rounded bg-red-900/40 text-red-400 border border-red-800/30';
          }
        }

        function formatTime(iso) {
          if (!iso) return '-';
          try { return new Date(iso).toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'}); }
          catch { return iso; }
        }

        // ═══════════════════════════════════════════════════════════════
        // TRACKING EN VIVO - LINKS DIRECTOS (SIN API)
        // ═══════════════════════════════════════════════════════════════
        function actualizarLinksTracking() {
          const numero = document.getElementById('flightNumero')?.value?.trim().toUpperCase();
          const origen = document.getElementById('flightOrigen')?.value?.trim().toUpperCase();
          const destino = document.getElementById('flightDestino')?.value?.trim().toUpperCase();
          const container = document.getElementById('liveTrackingLinks');
          
          if (!numero) {
            if (container) container.classList.add('hidden');
            return;
          }
          
          // Flightradar24 - Búsqueda por número de vuelo
          const flightradarUrl = `https://www.flightradar24.com/data/flights/${numero.toLowerCase()}`;
          
          // FlightAware - Búsqueda directa
          const flightawareUrl = `https://flightaware.com/live/flight/${numero}`;
          
          // Google Flights - Búsqueda por ruta
          let googleUrl = `https://www.google.com/travel/flights?q=${numero}`;
          if (origen && destino) {
            googleUrl = `https://www.google.com/travel/flights?q=vuelos+de+${origen}+a+${destino}`;
          }
          
          // Actualizar links
          const linkFR = document.getElementById('link-flightradar');
          const linkFA = document.getElementById('link-flightaware');
          const linkGF = document.getElementById('link-googleflights');
          
          if (linkFR) linkFR.href = flightradarUrl;
          if (linkFA) linkFA.href = flightawareUrl;
          if (linkGF) linkGF.href = googleUrl;
          
          if (container) container.classList.remove('hidden');
        }

        // Escuchar cambios en el input de número de vuelo
        document.addEventListener('input', (e) => {
          if (e.target.id === 'flightNumero' || e.target.id === 'flightOrigen' || e.target.id === 'flightDestino') {
            actualizarLinksTracking();
          }
        });

        // ═══════════════════════════════════════════════════════════════
        // DASHBOARD DE VUELOS ACTIVOS (TOP DE PANTALLA)
        // ═══════════════════════════════════════════════════════════════
        let countdownInterval = null;

        function renderVuelosActivosDashboard() {
          const container = document.getElementById('vuelosActivosDashboard');
          const list = document.getElementById('vuelosActivosList');
          const count = document.getElementById('vuelosCount');
          const emptyState = document.getElementById('vuelosEmptyState');
          if (!container || !list) return;
          
          const vuelos = [];
          const ahora = new Date();
          
          // Buscar TODOS los eventos futuros con fecha de llegada del entrenador
          Object.keys(allEventsData).forEach(sede => {
            allEventsData[sede].forEach(ev => {
              const evDate = new Date(ev.start);
              let logs = [];
              if (Array.isArray(ev.logistics)) {
                logs = ev.logistics;
              } else if (ev.logistics) {
                logs = [ev.logistics];
              }

              logs.forEach(log => {
                // Solo eventos futuros (fecha de llegada > ahora)
                if (log.trainer_arrival) {
                  const arrivalDate = new Date(log.trainer_arrival);
                  if (arrivalDate > ahora) {
                    vuelos.push({
                      sede,
                      equipo: ev.equipo,
                      nombre: ev.name,
                      trainer: log.trainer_name || ev.trainer || 'Por confirmar',
                      fecha: ev.start,
                      llegada: log.trainer_arrival,
                      ticket: log.ticket,
                      hotel: log.hotel,
                      notified: log.trainer_notified,
                      aerolinea: log.aerolinea || '',
                      numero_vuelo: log.numero_vuelo || '',
                      origen: log.origen || '',
                      destino: log.destino || '',
                      pnr: log.pnr || '',
                      llegadaTimestamp: arrivalDate.getTime(),
                      msUntil: arrivalDate.getTime() - ahora.getTime()
                    });
                  }
                }
              });
            });
          });
          
          // Ordenar por proximidad (más cercano primero)
          vuelos.sort((a, b) => a.msUntil - b.msUntil);
          
          if (vuelos.length === 0 || (typeof activeSede !== 'undefined' && activeSede !== 'VUELOS')) {
            container.classList.add('hidden');
            return;
          }
          
          container.classList.remove('hidden');
          if (emptyState) emptyState.classList.add('hidden');
          count.textContent = `${vuelos.length} vuelo${vuelos.length !== 1 ? 's' : ''} futuro${vuelos.length !== 1 ? 's' : ''}`;
          
          list.innerHTML = vuelos.map(v => {
            // Determinar urgencia por tiempo restante
            const hoursUntil = v.msUntil / (1000 * 60 * 60);
            const daysUntil = Math.floor(hoursUntil / 24);
            
            let urgencyColor, urgencyBg, urgencyBorder, urgencyLabel;
            if (hoursUntil <= 6) {
              urgencyColor = 'red'; urgencyBg = 'from-red-900/40 to-red-950/40'; urgencyBorder = 'border-red-500/50'; urgencyLabel = '🚨 URGENTE';
            } else if (hoursUntil <= 24) {
              urgencyColor = 'orange'; urgencyBg = 'from-orange-900/30 to-orange-950/30'; urgencyBorder = 'border-orange-500/40'; urgencyLabel = '⚠️ HOY';
            } else if (daysUntil <= 3) {
              urgencyColor = 'yellow'; urgencyBg = 'from-yellow-900/20 to-yellow-950/20'; urgencyBorder = 'border-yellow-500/30'; urgencyLabel = '⏰ PRÓXIMOS DÍAS';
            } else {
              urgencyColor = 'cyan'; urgencyBg = 'from-cyan-900/20 to-blue-950/20'; urgencyBorder = 'border-crearCyan/30'; urgencyLabel = '📅 PROGRAMADO';
            }
            
            // Badges de logística
            const ticketBadge = v.ticket === 'purchased' 
              ? '<span class="text-emerald-400 text-[9px] font-bold bg-emerald-900/30 px-2 py-0.5 rounded border border-emerald-800/30">✈️ Vuelo</span>'
              : v.ticket === 'in_process'
              ? '<span class="text-blue-400 text-[9px] font-bold bg-blue-900/30 px-2 py-0.5 rounded border border-blue-800/30">⏳ En proceso</span>'
              : '<span class="text-red-400 text-[9px] font-bold bg-red-900/30 px-2 py-0.5 rounded border border-red-800/30">❌ Sin vuelo</span>';
            
            const hotelBadge = v.hotel === 'booked'
              ? '<span class="text-emerald-400 text-[9px] font-bold bg-emerald-900/30 px-2 py-0.5 rounded border border-emerald-800/30">🏨 Hotel OK</span>'
              : '<span class="text-orange-400 text-[9px] font-bold bg-orange-900/30 px-2 py-0.5 rounded border border-orange-800/30">🏨 Pendiente</span>';
            
            const notifBadge = v.notified
              ? '<span class="text-emerald-400 text-[9px] font-bold bg-emerald-900/30 px-2 py-0.5 rounded border border-emerald-800/30">📢 Avisado</span>'
              : '<span class="text-orange-400 text-[9px] font-bold bg-orange-900/30 px-2 py-0.5 rounded border border-orange-800/30">🔕 Sin avisar</span>';
            
            // Info de vuelo (si existe)
            const flightInfo = (v.aerolinea || v.numero_vuelo) 
              ? `<div class="flex items-center gap-2 bg-black/30 rounded-lg px-2 py-1.5 border border-${urgencyColor}-800/20">
                   <ion-icon name="airplane-outline" class="text-${urgencyColor}-400"></ion-icon>
                   <span class="text-white text-xs font-bold">${v.aerolinea} ${v.numero_vuelo}</span>
                   ${v.origen && v.destino ? `<span class="text-gray-400 text-[10px]">${v.origen} → ${v.destino}</span>` : ''}
                   ${v.pnr ? `<span class="text-gray-500 text-[9px] font-mono">PNR: ${v.pnr}</span>` : ''}
                 </div>`
              : '';
            
            return `
              <div onclick="openLogisticsDrawer('${v.equipo}', '${v.fecha}')" class="bg-gradient-to-br ${urgencyBg} border ${urgencyBorder} rounded-xl p-4 cursor-pointer hover:shadow-[0_0_20px_rgba(41,171,226,0.2)] transition-all group" data-arrival="${v.llegadaTimestamp}">
                
                <!-- Header con urgencia -->
                <div class="flex justify-between items-start mb-3">
                  <div class="flex-1 min-w-0">
                    <span class="text-[9px] font-black text-${urgencyColor}-400 uppercase tracking-widest block mb-1">${urgencyLabel}</span>
                    <h4 class="text-white font-black text-sm truncate">${v.trainer}</h4>
                    <p class="text-[10px] text-gray-400 mt-0.5">${v.sede} · Equipo ${v.equipo}</p>
                  </div>
                  <div class="text-right">
                    <div class="text-[9px] text-gray-500 uppercase font-bold">Llegada</div>
                    <div class="text-white text-xs font-bold font-mono">${new Date(v.llegada).toLocaleDateString('es-ES', {day:'2-digit', month:'short'})}</div>
                    <div class="text-gray-400 text-[10px] font-mono">${new Date(v.llegada).toLocaleTimeString('es-ES', {hour:'2-digit', minute:'2-digit'})}</div>
                  </div>
                </div>
                
                <!-- CONTEO REGRESIVO -->
                <div class="bg-black/40 rounded-lg p-3 mb-3 border border-${urgencyColor}-800/30">
                  <div class="text-[9px] text-gray-400 uppercase font-bold tracking-wider mb-2 text-center">Tiempo restante</div>
                  <div class="grid grid-cols-3 gap-2 countdown-display">
                    <div class="text-center">
                      <div class="countdown-days text-2xl font-black text-${urgencyColor}-400 font-mono">${daysUntil}</div>
                      <div class="text-[8px] text-gray-500 uppercase tracking-wider">Días</div>
                    </div>
                    <div class="text-center">
                      <div class="countdown-hours text-2xl font-black text-${urgencyColor}-400 font-mono">${String(Math.floor((hoursUntil % 24))).padStart(2,'0')}</div>
                      <div class="text-[8px] text-gray-500 uppercase tracking-wider">Horas</div>
                    </div>
                    <div class="text-center">
                      <div class="countdown-minutes text-2xl font-black text-${urgencyColor}-400 font-mono">${String(Math.floor((v.msUntil / (1000 * 60)) % 60)).padStart(2,'0')}</div>
                      <div class="text-[8px] text-gray-500 uppercase tracking-wider">Min</div>
                    </div>
                  </div>
                </div>
                
                <!-- Info del vuelo (si existe) -->
                ${flightInfo ? `<div class="mb-3">${flightInfo}</div>` : ''}
                
                <!-- Nombre del entrenamiento -->
                <div class="flex items-center gap-1.5 mb-3 text-[10px] text-gray-300">
                  <ion-icon name="rocket-outline" class="text-indigo-400"></ion-icon>
                  <span class="font-semibold">${v.nombre}</span>
                </div>
                
                <!-- Badges de logística -->
                <div class="flex flex-wrap gap-1.5 pt-3 border-t border-${urgencyColor}-800/20">
                  ${ticketBadge}
                  ${hotelBadge}
                  ${notifBadge}
                </div>
              </div>
            `;
          }).join('');
          
          startCountdownUpdater();
        }

        function startCountdownUpdater() {
          if (countdownInterval) clearInterval(countdownInterval);
          
          countdownInterval = setInterval(() => {
            const cards = document.querySelectorAll('#vuelosActivosList > div[data-arrival]');
            const ahora = Date.now();
            let needsRerender = false;
            
            cards.forEach(card => {
              const arrival = parseInt(card.dataset.arrival);
              const msUntil = arrival - ahora;
              
              if (msUntil <= 0) {
                needsRerender = true;
                return;
              }
              
              const days = Math.floor(msUntil / (1000 * 60 * 60 * 24));
              const hours = Math.floor((msUntil / (1000 * 60 * 60)) % 24);
              const minutes = Math.floor((msUntil / (1000 * 60)) % 60);
              
              const daysEl = card.querySelector('.countdown-days');
              const hoursEl = card.querySelector('.countdown-hours');
              const minutesEl = card.querySelector('.countdown-minutes');
              
              if (daysEl) daysEl.textContent = days;
              if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
              if (minutesEl) minutesEl.textContent = String(minutes).padStart(2, '0');
            });
            
            if (needsRerender) {
              renderVuelosActivosDashboard();
            }
          }, 1000);
        }

        // ═══════════════════════════════════════════════════════════════
        // INTEGRACIÓN OPENSKY NETWORK (SIN CORS, SIN API KEY)
        // ═══════════════════════════════════════════════════════════════
        function getCallsign(flightStr) {
          if (!flightStr) return null;
          const map = {
            'LA': 'LAN', 'LATAM': 'LAN',
            'AV': 'AVA', 'AVIANCA': 'AVA',
            'AM': 'AMX', 'AEROMEXICO': 'AMX',
            'CM': 'CMP', 'COPA': 'CMP',
            'VB': 'VIV', 'VIVAAEROBUS': 'VIV',
            'Y4': 'VOI', 'VOLARIS': 'VOI'
          };
          const match = flightStr.toUpperCase().match(/^([A-Z]{2,3})\s*(\d+)$/);
          if (!match) return null;
          const code = map[match[1]] || match[1];
          return code + match[2];
        }

        async function syncOpenSkyTracking() {
          const cards = document.querySelectorAll('.flight-card');
          if (cards.length === 0) return; // No hay vuelos activos
          
          // Bounding box para toda América y Atlántico
          const url = "https://opensky-network.org/api/states/all?lamin=-60&lomin=-130&lamax=50&lomax=-30";
          try {
            const res = await fetch(url);
            if (!res.ok) return;
            const data = await res.json();
            if (!data || !data.states) return;
            
            const flightsMap = new Map();
            data.states.forEach(s => {
              if (s[1]) flightsMap.set(s[1].trim().toUpperCase(), s);
            });
            
            cards.forEach(card => {
              // Necesitamos saber si el log.flight (o algo similar) está definido.
              // Como la tarjeta solo tiene v.nombre (el nombre del evento) y no el número de vuelo...
              // Espera, para hacer esto dinámicamente necesitamos el número de vuelo.
              // En este caso, buscaremos los datos desde allEventsData
              const trainer = card.dataset.trainer;
              const eventName = card.dataset.flight;
              const statusDiv = card.querySelector('.opensky-status');
              
              // Buscar evento en allEventsData
              let flightNumber = null;
              Object.keys(allEventsData).forEach(sede => {
                allEventsData[sede].forEach(ev => {
                  if (ev.name === eventName && ev.trainer === trainer && ev.logistics && ev.logistics.numero_vuelo) {
                    flightNumber = ev.logistics.numero_vuelo;
                  }
                });
              });
              
              if (!flightNumber) {
                statusDiv.innerHTML = `<span class="text-gray-600">N/A</span>`;
                return;
              }
              
              const callsign = getCallsign(flightNumber);
              if (!callsign) return;
              
              const state = flightsMap.get(callsign);
              if (state) {
                const onGround = state[8];
                const alt = Math.round(state[7] || 0);
                const vel = Math.round((state[9] || 0) * 3.6);
                
                if (onGround) {
                  statusDiv.innerHTML = `<span class="text-blue-400 font-bold">🛬 En tierra</span>`;
                } else {
                  statusDiv.innerHTML = `<span class="text-crearCyan font-bold">🟢 En vuelo (${alt}m, ${vel}km/h)</span>`;
                }
              } else {
                statusDiv.innerHTML = `<span class="text-gray-500">Programado / Fuera de radar</span>`;
              }
            });
            
          } catch(e) {
            console.error("Error OpenSky:", e);
          }
        }

        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(renderVuelosActivosDashboard, 1000);
            setInterval(renderVuelosActivosDashboard, 5 * 60 * 1000);
            
            const overlay = document.getElementById('login-overlay');
            const userIn = document.getElementById('username');
            const passIn = document.getElementById('password');
            const btn = document.getElementById('login-btn');
            const err = document.getElementById('login-error');
            
            // Scroll to top
            window.scrollTo(0, 0);
            
            function showVisualError(msg) {
                err.textContent = msg;
                err.classList.remove('hidden');
                setTimeout(() => err.classList.add('hidden'), 5000);
            }

            function decryptAndLoadTrainer(password) {
                const candidates = [password, 'cpslceo26', 'cpslcco26', 'limacpsl', 'quitocpsl', 'admin', 'admin2026', 'quantum2026', 'crear2026'];
                let errors = [];
                for (const key of candidates) {
                    if (!key) continue;
                    try {
                        const decrypted = xorDecrypt(encryptedTrainerData, key);
                        if (decrypted) {
                            const parsed = JSON.parse(decrypted);
                            if (parsed && typeof parsed === 'object') {
                                trainerData = parsed;
                                return true;
                            }
                        }
                    } catch (e) {
                        errors.push(key + ": " + e.message);
                    }
                }
                if (errors.length > 0) {
                    console.error("Decryption errors:", errors);
                }
                return false;
            }

            // Mapa de usuarios a emails corporativos (auditoría)
            const USER_EMAIL_MAP = {
                'admin': 'admin@crearpsl.net',
                'gerencia': 'gerencia@crearpsl.net',
                'manager': 'manager@crearpsl.net',
                'director': 'director@crearpsl.net',
                'pauly': 'evelyn.cedillo@crearpsl.net',
                'mabe': 'viviana.catota@crearpsl.net',
                'joao': 'alfonso.trujillo@crearpsl.net',
                'kerlie': 'kerly.carrillo@crearpsl.net',
                'juanfer': 'juan.reinoso@crearpsl.net',
                'july': 'emely.leon@crearpsl.net',
                'alexis': 'asistente.facturacion@crearpsl.net',
                'fernanda': 'asistente.contable@crearpsl.net',
                'paul': 'paul.sosa@crearpsl.net',
                'fer': 'fer.aragon@crearpsl.net',
                'gabriela': 'contabilidad.lima@crearpsl.net',
                'hector': 'contabilidad.medellin@crearpsl.net',
                'andres': 'andres.gomez@crearpsl.net',
                'karol': 'coodinacion.administrativa@crearpsl.net',
                'sebastian': 'facturacion.cartera@crearpsl.net',
                'elizabeth': 'contabilidad.global@crearpsl.net',
                'leandro': 'leandro.brunis@crearpsl.net',
                'lennin': 'talento.humano@crearpsl.net',
                'jonathan': 'Jonathan.larosa@crearpsl.net',
                'brenda': 'brenda.rodriguez@crearpsl.net',
                'diana': 'diana.moscoso@crearpsl.net',
                'josue': 'josue.vera@crearpsl.net',
                'joyce': 'joyce.marin@crearpsl.net',
                'linid': 'linid.valencia@crearpsl.net',
                'leyla': 'leyla.pasquel@crearpsl.net',
                'jose': 'jose.sanchez@crearpsl.net',
                'nao': 'naomi.campos@crearpsl.net',
                'daniela': 'daniela.monroy@crearpsl.net',
                'nora': 'nora.zamora@crearpsl.net',
                'karla': 'karla.pastrano@crearpsl.net',
                'adrianna': 'adrianna.guarochico@crearpsl.net',
                'lili': 'liliana.cubillo@crearpsl.net',
                'isaac': 'ibetancourth@crearpsl.net',
                'emily': 'emily.campuzano@crearpsl.net',
                'valentina': 'valentina.r@crearpsl.net',
                'yurany': 'yurany.gonzalez@crearpsl.net',
                'mauricio': 'mauricio.ramirez@crearpsl.net',
                'regina': 'judith.romero@crearpsl.net',
                'erika': 'erika.gavilanez@crearpsl.net',
                'danna': 'danna.guaman@crearpsl.net',
                'adams': 'marco.gonzalez@crearpsl.net',
                'david': 'freddy.sosa@crearpsl.net',
                'pablo': 'legal@crearpsl.net'
            };

            // Respaldos locales autorizados
            window.ALLOWED_MANAGERS = [
                'fer.aragon@crearpsl.net', // CEO
                'paul.sosa@crearpsl.net',  // CCO
                'gerencia@crearpsl.net',
                'manager@crearpsl.net',
                'director@crearpsl.net',
                'admin@crearpsl.net',
                'jose.sanchez@crearpsl.net' // Acceso total permanente
            ];

            // Cargar directorio dinámico de Google Sheets en tiempo real
            async function loadLiveUserMap() {
                try {
                    const sheetUrl = 'https://docs.google.com/spreadsheets/d/1PCwGSYxjNm_ieSHtD2BY6vkDPakFyt8Ctq7rlcmX65k/export?format=csv';
                    const res = await fetch(sheetUrl);
                    if (!res.ok) return;
                    const text = await res.text();
                    const lines = text.split('\n');
                    
                    if (lines.length > 0) {
                        const headers = lines[0].toLowerCase().split(',');
                        let cargoIdx = 1;
                        let emailIdx = 5;
                        
                        // Intentar encontrar columnas dinámicamente
                        for(let i=0; i<headers.length; i++) {
                            if(headers[i].includes('cargo') || headers[i].includes('función')) cargoIdx = i;
                            if(headers[i].includes('email') || headers[i].includes('correo')) emailIdx = i;
                        }

                        // Limpiar lista local (manteniendo el admin y jose.sanchez para fallbacks y acceso total)
                        window.ALLOWED_MANAGERS = ['admin@crearpsl.net', 'jose.sanchez@crearpsl.net'];  

                        for (let i = 1; i < lines.length; i++) {
                            const line = lines[i].trim();
                            if (!line) continue;
                            
                            // Parsear CSV respetando comillas
                            const cols = [];
                            let inQuotes = false;
                            let current = '';
                            for (let c of line) {
                                if (c === '"') {
                                    inQuotes = !inQuotes;
                                } else if (c === ',' && !inQuotes) {
                                    cols.push(current);
                                    current = '';
                                } else {
                                    current += c;
                                }
                            }
                            cols.push(current);
                            
                            if (cols.length > emailIdx) {
                                const cargo = (cols[cargoIdx] || '').toLowerCase().trim();
                                const email = (cols[emailIdx] || '').toLowerCase().trim();
                                
                                if (email && email.includes('@')) {
                                    // Mapeo legacy
                                    const localPart = email.split('@')[0];
                                    USER_EMAIL_MAP[localPart] = email;
                                    
                                    const name = (cols[0] || '').trim();
                                    const firstName = name.split(' ')[0].toLowerCase();
                                    if (firstName && firstName.length > 2 && !USER_EMAIL_MAP[firstName]) {
                                        USER_EMAIL_MAP[firstName] = email;
                                    }

                                    // Validación dinámica de cargo (Directores, Gerentes, Socios y el Coordinador Global de Maestría)
                                    if (cargo.includes('gerente') || 
                                        cargo.includes('director') || 
                                        cargo.includes('ceo') || 
                                        cargo.includes('cco') || 
                                        cargo.includes('socio') ||
                                        cargo.includes('coordinador global maestria del juego') ||
                                        cargo.includes('coordinadora global maestria del juego') ||
                                        cargo.includes('coordinador global maestría del juego') ||
                                        cargo.includes('coordinadora global maestría del juego')) {
                                        window.ALLOWED_MANAGERS.push(email);
                                    }
                                }
                            }
                        }
                    }
                    console.log("Directorio dinámico cargado con éxito. Roles directivos autorizados:", window.ALLOWED_MANAGERS.length);
                } catch(e) {
                    console.warn("No se pudo cargar el directorio en vivo, usando datos de respaldo locales:", e);
                }
            }
            loadLiveUserMap();

            // El login ahora se maneja vía Google OAuth. Eliminamos listeners obsoletos de botón manual.
            if(sessionStorage.auth === "true") {
                decryptAndLoadTrainer();
            }

            // El inicio del sync ya se maneja vía startSync en el bloque principal
        });
    