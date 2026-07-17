// Script Block 1

        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        crearDarker: '#030712',
                        crearDark: '#0b1329',
                        crearCard: '#111a36',
                        crearBorder: '#1f2e5a',
                        crearBlue: '#1a75bc',
                        crearBlueLight: '#3b82f6',
                        crearCyan: '#06b6d4',
                        crearGold: '#d4af37',
                    },
                    fontFamily: {
                        outfit: ['Outfit', 'sans-serif'],
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                    },
                    boxShadow: {
                        'glow-blue': '0 0 20px rgba(26, 117, 188, 0.35)',
                        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.35)',
                        'glow-gold': '0 0 20px rgba(212, 175, 55, 0.35)',
                    }
                }
            }
        }
    

// Script Block 2

        // Tab switching for Portal 1 (Operaciones)
        function switchTab(group, tabName) {
            document.querySelectorAll(`.tab-content-${group}`).forEach(el => el.classList.add('hidden'));
            document.querySelectorAll(`.tab-btn-${group}`).forEach(btn => {
                btn.classList.remove('bg-crearCard', 'border-2', 'border-crearBlue/40', 'text-white', 'shadow-glow-blue');
                btn.classList.add('bg-crearDark', 'border', 'border-crearBorder', 'text-gray-400');
            });
            document.getElementById(`content-${tabName}`).classList.remove('hidden');
            const activeBtn = document.getElementById(`tab-${tabName}`);
            if (activeBtn) {
                activeBtn.classList.remove('bg-crearDark', 'border', 'border-crearBorder', 'text-gray-400');
                activeBtn.classList.add('bg-crearCard', 'border-2', 'border-crearBlue/40', 'text-white', 'shadow-glow-blue');
            }
        }

        // Portal Switcher
        function switchPortal(portalId) {
            document.querySelectorAll('.portal-section').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.portal-btn').forEach(btn => {
                btn.classList.remove('bg-crearCard', 'border-2', 'border-crearBlue/40', 'text-white', 'shadow-glow-blue');
                btn.classList.add('bg-crearDark', 'border', 'border-crearBorder', 'text-gray-400');
            });
            
            document.getElementById(`portal-content-${portalId}`).classList.remove('hidden');
            const activeBtn = document.getElementById(`btn-portal-${portalId}`);
            if (activeBtn) {
                activeBtn.classList.remove('bg-crearDark', 'border', 'border-crearBorder', 'text-gray-400');
                activeBtn.classList.add('bg-crearCard', 'border-2', 'border-crearBlue/40', 'text-white', 'shadow-glow-blue');
            }
        }

        // 7-Levels Data
        const ranksData = {
            participante: {
                title: "Participante (Aprendiz)",
                role: "Nivel I",
                identity: "Aprende y se redescubre desde la vulnerabilidad y la honestidad.",
                learns: "Consciencia de sus conversaciones limitantes, distinción entre víctima y creador, y responsabilidad personal.",
                shows: "Apertura a recibir retroalimentación, respeto a las reglas del salón y puntualidad rigurosa.",
                results: "Completar los procesos del fin de semana, realizar sus llamadas del grupo de creación y matriculación al C2.",
                cert: "✔ Certificación C1: Líder en Consciencia Inicial",
                advance: "Hacer declaración de intenciones claras el domingo y asegurar su participación en el Capítulo 2.",
                mentorship: "Escuchar activamente, no juzgar, resguardar su espacio de vulnerabilidad y no intentar forzar su proceso."
            },
            aliados: {
                title: "Aliado de Creación",
                role: "Nivel II",
                identity: "Sostiene el espacio y sirve con amor incondicional para la transformación del participante.",
                learns: "Drills de puerta y sala, contención RCP (Responsable de Cuidar Presencia), y dinámicas grupales de viernes.",
                shows: "Excelencia en la ejecución de su rol, puntualidad absoluta, presencia silenciosa y vestimenta reglamentada.",
                results: "Directorio del grupo entregado el viernes antes del primer receso, 100% de pre-registro a C2 en su grupo de creación.",
                cert: "✔ Certificación Nivel II: Aliado de Creación Certificado",
                advance: "Acompañamiento exitoso (llamadas L-M-V) de su grupo por 2 semanas y evaluación favorable del Capitán.",
                mentorship: "Entrenar drills físicos en sala antes de abrir puertas. Alinear desde el ser y la postura corporal erguida."
            },
            managers: {
                title: "Manager",
                role: "Nivel III",
                identity: "Organiza, estructura y audita los recursos físicos y lógicos de la sala.",
                learns: "Administración de bases de datos, control de rotafolios con 10 hojas por lado, coordinación de iluminación y pasarelas de cobro.",
                shows: "Criterio de resolución rápida, orden milimétrico de mesa y simetría en la logística física del salón.",
                results: "Registro sin demoras el domingo, cero quiebres por falta de marcadores o material, y reportes de base de datos actualizados.",
                cert: "✔ Certificación Nivel III: Manager de Excelencia Operativa",
                advance: "Haber coordinado en excelencia al menos 2 fines de semana completos y recomendación directa del Capitán.",
                mentorship: "Dar retroalimentación rápida sin invalidar. Coordinar la alimentación e insumos del equipo a tiempo."
            },
            capitanes: {
                title: "Capitán",
                role: "Nivel IV",
                identity: "Lidera y guía en cancha a aliados y managers, cuidando la energía del equipo.",
                learns: "Grounding del equipo de aliados, conducción de la reunión de alineación pre-C1, y detección oportuna de quiebres de energía.",
                shows: "Contexto inquebrantable, comunicación empática y firme con el entrenador, y autoridad amorosa constante.",
                results: "Equipo de aliados alineado antes de abrir puertas, y cumplimiento de la meta del 50% de conversión a C2.",
                cert: "✔ Certificación Nivel IV: Capitán de Cancha Certificado",
                advance: "Tener al menos 3 aliados de su equipo ascendidos a Managers y recomendación del Quantum Team Senior.",
                mentorship: "Desarrollar y guiar al Manager. Enseñar a delegar tareas operativas para enfocarse en el cuidado de la energía humana."
            },
            qt: {
                title: "Quantum Team (QT)",
                role: "Nivel V",
                identity: "Asume la postura de un Master Coach y resguarda la integridad transformacional del proceso.",
                learns: "Lectura avanzada de resistencias de participantes, calibración energética del salón, y contención en catarsis.",
                shows: "Coherencia absoluta en sala y fuera de ella, protección comercial del contexto y contención ontológica.",
                results: "Mínimo 50% de conversión a C2, detección y acompañamiento a líderes potenciales del domingo.",
                cert: "🎓 Certificación Nivel V: Quantum Team Global (Custodio de Marca)",
                advance: "Efectividad en conversión, evaluación 360° aprobada, y cumplimiento estricto del plan de mantenimiento: participar como mínimo en 8 eventos de Capítulo Uno (C1) al año, manteniendo un constante entrenamiento, lectura activa del manual, uso riguroso de herramientas y entrega comprobada de resultados.",
                mentorship: "Entrenar al Capitán. Identificar líderes potenciales en sala y diseñar sus planes de desarrollo de legado."
            },
            qtsenior: {
                title: "Quantum Team Senior",
                role: "Nivel VI",
                identity: "Arquitecto de estándares y multiplicador de la cultura CREAR a nivel internacional.",
                learns: "Auditoría de sedes multisede, alineación de directores, y diseño de manuales operativos globales.",
                shows: "Liderazgo inspirador macro, criterio neutral ante quiebres organizacionales y protección hermética de marca.",
                results: "Certificación de nuevos Capitanes, y mantenimiento de estándares consistentes en las sedes a su cargo.",
                cert: "🏆 Certificación Nivel VI: Arquitecto Senior de Liderazgo CREAR",
                advance: "Haber certificado con éxito al menos a 5 Capitanes y tener una recomendación formal de la Junta Directiva de CREAR.",
                mentorship: "Formar a nuevos miembros del Quantum Team. Asegurar que las sedes sigan la directriz oficial y erradicar malas prácticas."
            },
            entrenador: {
                title: "Coordinador de Maestría / Entrenador",
                role: "Nivel VII",
                identity: "Diseñador de futuros. Conduce la transformación ontológica del participante desde el escenario.",
                learns: "Oratoria de alto impacto transformacional, gestión de catarsis grupales masivas y dinámicas raíz familiares.",
                shows: "Liderazgo extraordinario, presencia magnética, y maestría en la contención existencial del salón.",
                results: "Desarrollo de legados a gran escala, y retención e impacto del proceso transformacional del fin de semana.",
                cert: "👑 Certificación Nivel VII: Entrenador Oficial / Master Coach CREAR",
                advance: "Jubilación o transición a roles directivos/socios en la expansión global de CREAR.",
                mentorship: "El máximo escalafón de servicio. Mentoría personal a los QT Seniors y diseño del futuro de la organización."
            }
        };

        function selectRank(rankId) {
            document.querySelectorAll('.rank-btn').forEach(btn => {
                btn.className = "rank-btn w-full p-4 rounded-xl border text-left transition-all flex items-center justify-between cursor-pointer border-crearBorder/40 bg-crearDark/60 text-gray-400 hover:border-crearBorder/80";
                const topSpan = btn.querySelector('span:first-child');
                if (topSpan) topSpan.className = "text-[9px] font-bold uppercase tracking-wider block text-gray-500";
                const rightSpan = btn.querySelector('span:last-child');
                if (rightSpan) rightSpan.className = "text-[10px] font-medium text-gray-500 italic";
            });
            
            const activeBtn = document.getElementById(`rank-btn-${rankId}`);
            if (activeBtn) {
                activeBtn.className = "rank-btn w-full p-4 rounded-xl border-2 border-crearBlue/40 bg-crearCard text-white shadow-glow-blue cursor-pointer";
                const topSpan = activeBtn.querySelector('span:first-child');
                if (topSpan) topSpan.className = "text-[9px] font-bold uppercase tracking-wider block text-crearBlueLight";
                const rightSpan = activeBtn.querySelector('span:last-child');
                if (rightSpan) rightSpan.className = "text-[10px] font-medium text-crearGold italic font-semibold";
            }
            renderRankDetails(rankId);
        }

        function renderRankDetails(rankId) {
            const data = ranksData[rankId];
            if (!data) return;
            
            const html = `
                <div class="space-y-4">
                    <div class="border-b border-crearBorder pb-3 flex justify-between items-center">
                        <div>
                            <span class="text-[10px] font-bold text-crearCyan uppercase tracking-widest">Currículo de Liderazgo</span>
                            <h3 class="text-xl font-extrabold text-white mt-0.5">${data.title}</h3>
                        </div>
                        <span class="bg-crearBlue/10 border border-crearBlue/30 text-crearBlueLight text-[9px] px-2.5 py-1 rounded font-black uppercase tracking-widest">${data.role}</span>
                    </div>
                    
                    <div class="bg-crearDarker/60 p-4 rounded-xl border border-crearBorder/30">
                        <span class="text-[10px] font-black text-crearGold uppercase tracking-wider block mb-1">Identidad (El Ser)</span>
                        <p class="text-gray-300 text-xs font-light leading-relaxed italic border-l-2 border-crearGold pl-3">
                            "${data.identity}"
                        </p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div class="bg-crearDarker/40 p-4 rounded-xl border border-crearBorder/20">
                            <span class="text-crearCyan font-bold block mb-1.5">🧠 ¿Qué aprende?</span>
                            <p class="text-gray-400 text-[10px] font-light">${data.learns}</p>
                        </div>
                        <div class="bg-crearDarker/40 p-4 rounded-xl border border-crearBorder/20">
                            <span class="text-crearBlueLight font-bold block mb-1.5">⚖️ ¿Qué demuestra? (Competencias)</span>
                            <p class="text-gray-400 text-[10px] font-light">${data.shows}</p>
                        </div>
                        <div class="bg-crearDarker/40 p-4 rounded-xl border border-crearBorder/20">
                            <span class="text-green-400 font-bold block mb-1.5">📈 ¿Qué resultados produce?</span>
                            <p class="text-gray-400 text-[10px] font-light">${data.results}</p>
                        </div>
                        <div class="bg-crearDarker/40 p-4 rounded-xl border border-crearBorder/20">
                            <span class="text-crearGold font-bold block mb-1.5">🚀 Requisitos para avanzar</span>
                            <p class="text-gray-400 text-[10px] font-light">${data.advance}</p>
                        </div>
                    </div>
                    
                    <div class="bg-teal-950/20 border border-teal-900/30 rounded-xl p-4 space-y-1">
                        <span class="text-[10px] font-black text-teal-400 uppercase tracking-widest block mb-1">🤝 Sistema de Formación (Guía del Líder)</span>
                        <p class="text-gray-300 text-[10px] font-light leading-relaxed">
                            <strong>Cómo desarrollarlo:</strong> ${data.mentorship}
                        </p>
                    </div>
                </div>
            `;
            
            document.getElementById('rank-detail-container').innerHTML = html;
        }

        // Protocols Database
        const protocolsData = {
            operacion: [
                { title: "🍔 Principio de Estandarización Global", desc: "La experiencia de Medellín debe ser la misma que la de Lima, Quito o Chilpancingo. Las preferencias personales nunca están por encima del estándar global." },
                { title: "🖥️ Presentaciones Digitales Oficiales", desc: "Únicamente se usarán dos presentaciones autorizadas: Presentación General (invariable) y Presentación Particular del Entrenador. Prohibidos carteles físicos o versiones antiguas." },
                { title: "💻 Configuración de Computadora", desc: "Máximo 2 presentaciones abiertas al mismo tiempo en el ordenador de cabina. Eliminar versiones anteriores antes de iniciar." },
                { title: "⏰ Reunión de Alineación Pre-C1", desc: "Reunión obligatoria 1 hora antes del Grounding con el Capitán, Quantum Team, Oficina y Coordinación para alinear participantes, roles, logística y energía." }
            ],
            participantes: [
                { title: "🤝 Integridad y Redes de Mercadeo", desc: "Queda terminantemente prohibido dentro del salón la promoción de negocios personales, reclutamiento para multiniveles o distribución de publicidad personal." },
                { title: "🏷️ Accesorios Promocionales", desc: "No se permitirá portar pulseras, pines o distintivos comerciales de marcas o emprendimientos propios dentro del salón." },
                { title: "💼 Negocios con Participantes", desc: "La confianza del participante es sagrada. Está prohibido proponer negocios, realizar ventas o agendar reuniones comerciales durante el C1 o al finalizarlo." },
                { title: "👑 Inversión del Liderazgo", desc: "Identificar rápidamente a participantes con alta disposición y hambre para delegarles responsabilidades específicas sin necesidad de usar etiquetas como Co-capitán." }
            ],
            aliados: [
                { title: "📋 Tareas Obligatorias en Grupos de Creación", desc: "Todo Aliado de Creación debe realizar las 7 tareas el viernes: Presentación de Aliado (~1m), Presentación de Participantes (~1m c/u), Nombre del Grupo (con propósito), Grito de Poder, Reglas del Equipo (Puntualidad, etc.), Grupo de WhatsApp y Directorio Oficial (para entregar al Capitán antes del primer receso)." },
                { title: "🚪 Drills y Entrenamiento Previo", desc: "El QT debe ensayar físicamente los drills de sala con los aliados antes de abrir puertas, garantizando que conozcan el qué, cómo, cuándo y por qué de su rol." },
                { title: "👥 Sombra y Cohesión", desc: "Emparejar aliados sombra para que se sostengan energéticamente y evitar la dispersión o corrillos en el salón." }
            ],
            salon: [
                { title: "📝 Rotafolios del Salón", desc: "Cada rotafolio debe contar exactamente con 10 hojas por lado y disponer de tres marcadores en excelente estado: negro, azul y rojo." },
                { title: "💡 Iluminación de Sala", desc: "Habrá un responsable de luces exclusivo. Después de una catarsis, está prohibido encender las luces abruptamente; se debe respetar el espacio emocional." },
                { title: "🎵 Música de Sala", desc: "La música es obligatoria en todos los recesos y debe estar sincronizada en energía con el momento emocional y el objetivo del proceso." }
            ],
            emergencias: [
                { title: "🚪 Abandono del Salón", desc: "Si un participante intenta abandonar el salón, el Aliado debe escuchar en presencia sin debatir y notificar de inmediato al QT o Entrenador para su contención." },
                { title: "🚑 Descompensación Física Leve", desc: "Ante llanto intenso o ansiedad del participante, el Aliado se sienta al lado, asiste en respiraciones conscientes y avisa en silencio al QT de sala." },
                { title: "🚪 Ausencia de Aliado en Puerta", desc: "Redistribución inmediata: el Capitán o QT cubre la puerta vacía para evitar filtraciones de ruido o pérdida de contexto acústico." }
            ],
            seguimiento: [
                { title: "🏷️ Información Obligatoria de Gafetes", desc: "Todo Gafete debe tener al reverso: Teléfono del participante, Nombre de quien invitó, y Nombre del Aliado asignado. Se prohíbe retirar el gafete excepto en comidas y salida nocturna." },
                { title: "🛡️ Protocolo de Sostenimiento (L-M-V)", desc: "Acompañamiento obligatorio al participante durante dos semanas (Lunes, Miércoles y Viernes) para sostener compromisos y resolver dudas." },
                { title: "📈 KPIs y Conversión a C2", desc: "El Quantum Team evalúa su retención apuntando a una meta mínima del 50% de conversión. Un resultado menor indica debilidad en el seguimiento del equipo." }
            ]
        };

        function filterProtocols(category) {
            document.querySelectorAll('.proto-cat-btn').forEach(btn => {
                btn.className = "proto-cat-btn bg-crearDark border border-crearBorder text-gray-400 rounded-xl p-4 text-center transition-all hover:border-crearBorder/80 cursor-pointer";
            });
            const activeBtn = document.getElementById(`proto-btn-${category}`);
            if (activeBtn) {
                activeBtn.className = "proto-cat-btn bg-crearCard border-2 border-crearBlue/40 text-white rounded-xl p-4 text-center transition-all hover:border-crearBlue shadow-glow-blue cursor-pointer";
            }
            renderProtocols(category);
        }

        function renderProtocols(category) {
            const list = protocolsData[category];
            if (!list) return;
            const html = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${list.map((proto, idx) => `
                        <div class="bg-crearDarker/40 p-5 rounded-xl border border-crearBorder/20 space-y-2 hover:border-crearBorder/60 transition-all">
                            <span class="text-xs font-bold text-crearGold block flex items-center gap-1">
                                <span class="text-[10px] text-gray-500 font-normal">#	h${idx+1}</span> ${proto.title}
                            </span>
                            <p class="text-gray-400 text-xs font-light leading-relaxed">
                                ${proto.desc}
                            </p>
                        </div>
                    `).join('')}
                </div>
            `;
            document.getElementById('protocols-display-box').innerHTML = html.replace('#\th', '#');
        }

        // Scenarios Data (Simulador)
        const scenariosData = {
            1: {
                title: "Caso 1: Un participante se levanta enojado y quiere abandonar el salón",
                context: "Durante una dinámica de confrontación, un participante se siente expuesto, se levanta diciendo que esto es una pérdida de tiempo y se dirige firmemente a la salida trasera.",
                error: "Intentar debatir con él en la puerta, confrontarlo con agresividad o bloquearle físicamente el paso diciendo 'tienes que quedarte por tu bien'. Esto refuerza su victimización y escala el conflicto en sala.",
                official: "El Aliado de Puerta abre la puerta para evitar ruidos y contiene con postura firme pero amorosa. Escucha sin juzgar ni reaccionar ('Entiendo que esto es retador para ti, ¿qué te trajo aquí inicialmente?'). Paralelamente, otro aliado alerta en silencio al QT de sala o al Capitán. Si la persona decide irse, se le permite salir, pero se hace un reporte de inmediato al Entrenador para coordinar la llamada post-sala."
            },
            2: {
                title: "Caso 2: El Aliado asignado a la puerta de entrada no llega o se ausenta",
                context: "El proceso está en pleno ejercicio acústico sensible (RCP/Catarsis) y la puerta de la calle queda desatendida. Hay ruido en el pasillo exterior por parte de otros participantes y personal del local.",
                error: "Quejarse en voz alta del aliado ausente, dejar la puerta sola o ir a buscarlo abandonando otras responsabilidades de sala, permitiendo filtraciones de ruido.",
                official: "El Capitán de cancha o el QT de sala cubre la puerta de inmediato de manera automática para resguardar el hermetismo acústico de la sala. Posteriormente, el Capitán asigna un relevo oficial de puerta mediante el sistema 'parejas sombra' y se registra el quiebre del aliado ausente para su posterior retroalimentación y evaluación en la autopsia del día."
            },
            3: {
                title: "Caso 3: Un Manager de sala muestra desmotivación o energía baja frente al equipo",
                context: "Es el sábado por la tarde, la fatiga física empieza a golpear al equipo y el Manager encargado de la mesa de registro realiza comentarios de cansancio y apatía enfrente de los aliados jóvenes.",
                error: "Ignorarlo, regañarlo enfrente de los aliados o asumir sus tareas de forma pasivo-agresiva.",
                official: "El Capitán o un QT Senior se lo lleva a solas a un espacio privado (fuera de la vista de aliados y participantes). Sostiene una conversación de alineación ontológica desde el amor y la fuerza, reconectándolo con el 'para qué' de su servicio ('¿A quién estás eligiendo ser para tu equipo en este momento?'). Si la energía física es el problema, se le da un receso de 15 minutos para refrescarse y se le reasigna con un 'aliado sombra' de alta energía para contagiar el contexto."
            },
            4: {
                title: "Caso 4: El Capitán pierde el contexto transformacional y se enfoca solo en tareas",
                context: "El Capitán de cancha está obsesionado con la simetría de las sillas y el orden de los rotafolios, al punto de presionar y gritar a los aliados, olvidando sostener a un participante que está quebrado al fondo de la sala.",
                error: "Llamarle la atención de forma agresiva en sala, gritarle de vuelta o dejar que continúe desalineando la energía del equipo.",
                official: "El QT o el QT Senior interviene aplicando el principio de 'Inversión de Liderazgo'. Se acerca al Capitán en un receso o en silencio, le pone la mano en el hombro y lo reconecta con el ADN del manual: 'Capitán, tu excelencia no radica en acomodar sillas, radica en desarrollar líderes. Sostengamos el espacio'. Se le reorienta para que delegue las tareas logísticas al Manager y asuma su rol de contención de la sala."
            },
            5: {
                title: "Caso 5: Un participante declara con fuerza el domingo, pero desaparece y no contesta el lunes",
                context: "Un participante tuvo un quiebre y reconciliación profunda el domingo, declaró su pase al Capítulo 2 con lágrimas, pero el lunes por la tarde el Aliado reporta que no atiende llamadas ni WhatsApp.",
                error: "Dar de baja al participante de inmediato, regañarlo en WhatsApp o dejar que el aliado insista de forma molesta enviando mensajes automáticos de cobro.",
                official: "El Aliado no debe hablar de dinero ni de cobros en este primer contacto. Debe enviar un mensaje de sostenimiento centrado en la relación: 'Hola [Nombre], te llamaba para saludarte, saber cómo amaneciste hoy tras tu hermosa declaración del domingo y recordarte que estamos aquí para ti'. Si aun así no responde, el QT activa el círculo de influencia (el amigo/familiar que lo invitó o con quien conectó en sala) para conocer su estado emocional real y programar una visita/llamada empática de contención."
            }
        };

        function selectScenario(id) {
            document.querySelectorAll('.scen-btn').forEach(btn => {
                btn.className = "scen-btn bg-crearDark border border-crearBorder text-gray-400 rounded-xl p-4 text-left transition-all hover:border-crearBorder/80 cursor-pointer";
                const labelSpan = btn.querySelector('span:first-child');
                if (labelSpan) labelSpan.className = "text-[9px] font-bold text-gray-500 uppercase tracking-wider block mb-1";
            });
            
            const activeBtn = document.getElementById(`scen-btn-${id}`);
            if (activeBtn) {
                activeBtn.className = "scen-btn bg-crearCard border-2 border-crearBlue/40 text-white rounded-xl p-4 text-left transition-all hover:border-crearBlue cursor-pointer shadow-glow-blue";
                const labelSpan = activeBtn.querySelector('span:first-child');
                if (labelSpan) labelSpan.className = "text-[9px] font-bold text-crearBlueLight uppercase tracking-wider block mb-1";
            }
            renderScenario(id, false);
        }

        function renderScenario(id, revealAction = false) {
            const data = scenariosData[id];
            if (!data) return;
            const html = `
                <div class="space-y-6 flex-1 flex flex-col justify-between">
                    <div class="space-y-4">
                        <div class="border-b border-crearBorder pb-3 flex justify-between items-center">
                            <div>
                                <span class="text-[10px] font-bold text-crearCyan uppercase tracking-widest">Escenario de Conflicto Real</span>
                                <h3 class="text-base font-extrabold text-white mt-0.5">${data.title}</h3>
                            </div>
                        </div>
                        
                        <div class="bg-crearDarker/50 p-4 rounded-xl border border-crearBorder/20">
                            <span class="text-[10px] font-black text-crearGold uppercase tracking-wider block mb-1">El Suceso:</span>
                            <p class="text-gray-300 text-xs font-light leading-relaxed">
                                ${data.context}
                            </p>
                        </div>
                        
                        ${revealAction ? `
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="bg-red-950/20 border border-red-900/30 p-4 rounded-xl space-y-1">
                                    <span class="text-[10px] font-bold text-red-400 uppercase tracking-wider block mb-1">🚫 LO QUE NO SE DEBE HACER (Error Frecuente):</span>
                                    <p class="text-gray-300 text-xs font-light leading-relaxed">
                                        ${data.error}
                                    </p>
                                </div>
                                <div class="bg-green-950/20 border border-green-900/30 p-4 rounded-xl space-y-1">
                                    <span class="text-[10px] font-bold text-green-400 uppercase tracking-wider block mb-1">⚔️ ACCIÓN Y CORRECCIÓN OPERATIVA OFICIAL:</span>
                                    <p class="text-gray-300 text-xs font-light leading-relaxed">
                                        ${data.official}
                                    </p>
                                </div>
                            </div>
                        ` : `
                            <div class="flex justify-center py-6">
                                <button onclick="renderScenario(${id}, true)" class="bg-crearBlue hover:bg-crearBlue/80 text-white text-xs font-black uppercase tracking-wider px-6 py-3 rounded-xl transition-all shadow-glow-blue cursor-pointer">
                                    👁️ Revelar Acción Oficial QT
                                </button>
                            </div>
                        `}
                    </div>
                </div>
            `;
            document.getElementById('scenario-display-box').innerHTML = html;
        }



        // Page Load Init
                // Global Search Engine Logic (Professional Topic Search)
        const searchIndex = [
            // MODULES
            { title: "Módulo I: Identidad, ADN & Espíritu QT", type: "Módulo", portal: "operaciones", tab: "identidad", tags: "adn identidad espiritu promesa manifiesto" },
            { title: "Módulo II: Cultura Crear & 12 Principios del QT", type: "Módulo", portal: "operaciones", tab: "cultura", tags: "cultura principios honor excelencia" },
            { title: "Módulo III: Arquitectura & Mapa de Transformación del Capítulo 1", type: "Módulo", portal: "operaciones", tab: "arquitectura", tags: "arquitectura mapa transformacion viernes sabado domingo" },
            { title: "Módulo IV: Desarrollo de Aliados (Matriz de Cancha)", type: "Módulo", portal: "operaciones", tab: "aliados", tags: "aliados cancha grupos creacion whatsapp directorio" },
            { title: "Módulo V: Estándar de Seguimiento & Sostenimiento", type: "Módulo", portal: "operaciones", tab: "seguimiento", tags: "seguimiento sostenimiento llamadas w1 cronograma" },
            { title: "Módulo VI: Lectura de Participantes & Gestión de Energía", type: "Módulo", portal: "operaciones", tab: "lectura", tags: "lectura participantes energia perfiles resistencia" },
            { title: "Módulo VII: Presencia & Estándar Personal QT", type: "Módulo", portal: "operaciones", tab: "estandar-qt", tags: "presencia estandar personal postura vestimenta" },
            { title: "Módulo VIII: Estándares Globales Multisede", type: "Módulo", portal: "operaciones", tab: "global-multisede", tags: "estandares globales multisede rotafolios musica luces" },
            { title: "Módulo IX: Protocolos de Integridad & Ética Profesional", type: "Módulo", portal: "operaciones", tab: "etica", tags: "integridad etica conducta negocios participante" },
            { title: "Módulo X: Excelencia Operativa del Salón", type: "Módulo", portal: "operaciones", tab: "excelencia-salon", tags: "excelencia salon rotafolio marcadores catarsis" },
            { title: "Módulo XI: Momentos Críticos del Domingo", type: "Módulo", portal: "operaciones", tab: "domingo", tags: "domingo precios momentos conversion registro" },
            
            // RANKS
            { title: "Ruta de Liderazgo: Participante", type: "Rango", portal: "universidad", actionId: "participante", tags: "participante aprendiz nivel 1" },
            { title: "Ruta de Liderazgo: Aliado de Creación", type: "Rango", portal: "universidad", actionId: "aliados", tags: "aliados nivel 2 cancha" },
            { title: "Ruta de Liderazgo: Manager", type: "Rango", portal: "universidad", actionId: "managers", tags: "manager nivel 3 logistica" },
            { title: "Ruta de Liderazgo: Capitán de Cancha", type: "Rango", portal: "universidad", actionId: "capitanes", tags: "capitanes nivel 4 cancha" },
            { title: "Ruta de Liderazgo: Quantum Team (QT)", type: "Rango", portal: "universidad", actionId: "qt", tags: "qt quantum team nivel 5" },
            { title: "Ruta de Liderazgo: Quantum Team Senior", type: "Rango", portal: "universidad", actionId: "qtsenior", tags: "qtsenior senior nivel 6" },
            { title: "Ruta de Liderazgo: Coordinador de Maestría / Entrenador", type: "Rango", portal: "universidad", actionId: "entrenador", tags: "entrenador coordinador maestria nivel 7 coach" },

            // PROTOCOLS
            { title: "Protocolo: Estandarización Global", type: "Protocolo", portal: "simulador", actionId: "proto_operacion", tags: "estandarizacion global precios rotafolios" },
            { title: "Protocolo: Presentaciones y Loop Visual", type: "Protocolo", portal: "simulador", actionId: "proto_operacion", tags: "presentaciones loop infocus pantallas" },
            { title: "Protocolo: Grupos de WhatsApp y Gafetes", type: "Protocolo", portal: "simulador", actionId: "proto_participantes", tags: "gafetes whatsapp directorio grupo creacion" },
            { title: "Protocolo: Alimentación y Kit de Aseo", type: "Protocolo", portal: "simulador", actionId: "proto_aliados", tags: "alimentacion aliados kit aseo" },
            { title: "Protocolo: Luces y Música en Salón", type: "Protocolo", portal: "simulador", actionId: "proto_salon", tags: "luces musica breaks salon" },
            { title: "Protocolo: Catarsis y Postura en Sala", type: "Protocolo", portal: "simulador", actionId: "proto_salon", tags: "catarsis sala aliados rcp" },
            { title: "Protocolo: Pérdida de Foco y Deserciones", type: "Protocolo", portal: "simulador", actionId: "proto_emergencias", tags: "foco desercion abandonar desaparecido crisis" },
            { title: "Protocolo: Seguimiento Comercial del Domingo", type: "Protocolo", portal: "simulador", actionId: "proto_seguimiento", tags: "domingo momentos comercial conversion" },

            // SIMULATOR CASES
            { title: "Simulador: Caso 1 - Fuga de Sala", type: "Simulador", portal: "simulador", actionId: "scen_1", tags: "caso 1 fuga sala abandonar participante" },
            { title: "Simulador: Caso 2 - Puerta Vacía", type: "Simulador", portal: "simulador", actionId: "scen_2", tags: "caso 2 puerta vacia aliados abandono" },
            { title: "Simulador: Caso 3 - Líder Apagado", type: "Simulador", portal: "simulador", actionId: "scen_3", tags: "caso 3 staff apagado lider aliado" },
            { title: "Simulador: Caso 4 - Pérdida de Foco", type: "Simulador", portal: "simulador", actionId: "scen_4", tags: "caso 4 perdida foco participante celular" },
            { title: "Simulador: Caso 5 - Lunes Desaparecido", type: "Simulador", portal: "simulador", actionId: "scen_5", tags: "caso 5 lunes desaparecido seguimiento llamada" }
        ];

        function handleGlobalSearch() {
            const query = document.getElementById('global-search-input').value.toLowerCase().trim();
            const resultsBox = document.getElementById('global-search-results');
            
            if (!query) {
                resultsBox.classList.add('hidden');
                return;
            }
            
            const filtered = searchIndex.filter(item => 
                item.title.toLowerCase().includes(query) || 
                item.type.toLowerCase().includes(query) ||
                item.tags.toLowerCase().includes(query)
            );
            
            if (filtered.length === 0) {
                resultsBox.innerHTML = '<div class="p-3 text-[10px] text-gray-500 italic">No se encontraron resultados.</div>';
                resultsBox.classList.remove('hidden');
                return;
            }
            
            resultsBox.innerHTML = filtered.map((item, idx) => `
                <div onclick="selectSearchResult(${searchIndex.indexOf(item)})" class="p-3 text-[11px] hover:bg-crearBlue/20 cursor-pointer transition-all flex justify-between items-center text-gray-300">
                    <div>
                        <span class="font-bold text-white block">${item.title}</span>
                        <span class="text-[9px] text-gray-500 mt-0.5">${item.type}</span>
                    </div>
                    <span class="text-[8px] font-black uppercase bg-crearBorder/50 text-crearCyan px-1.5 py-0.5 rounded ml-2">${item.portal.toUpperCase()}</span>
                </div>
            `).join('');
            
            resultsBox.classList.remove('hidden');
        }

        function selectSearchResult(idx) {
            const item = searchIndex[idx];
            document.getElementById('global-search-results').classList.add('hidden');
            document.getElementById('global-search-input').value = '';
            
            switchPortal(item.portal);
            
            if (item.tab) {
                switchTab('philosophy', item.tab);
                // Scroll to top of content
                setTimeout(() => {
                    const el = document.getElementById(`content-${item.tab}`);
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            } else if (item.actionId) {
                setTimeout(() => {
                    if (item.actionId.startsWith("proto_")) {
                        const cat = item.actionId.replace("proto_", "");
                        filterProtocols(cat);
                        const el = document.getElementById('protocols-display-box');
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } else if (item.actionId.startsWith("scen_")) {
                        const id = parseInt(item.actionId.replace("scen_", ""));
                        selectScenario(id);
                        const el = document.getElementById('scenario-display-box');
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } else {
                        // Rank
                        selectRank(item.actionId);
                        const el = document.getElementById('rank-detail-container');
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 150);
            }
        }
        
        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#global-search-input') && !e.target.closest('#global-search-results')) {
                document.getElementById('global-search-results').classList.add('hidden');
            }
        });


window.addEventListener('DOMContentLoaded', () => {
            switchPortal('operaciones');
            switchTab('philosophy', 'identidad');
            selectRank('qt');
            filterProtocols('operacion');
            selectScenario(1);
        });
    

