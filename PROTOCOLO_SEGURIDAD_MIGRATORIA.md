# PROTOCOLO DE SEGURIDAD MIGRATORIA PARA ENTRENADORES INTERNACIONALES
**CREAR Poder Sin Límites**

Este documento establece las directrices innegociables para la generación de Cartas de Bienvenida y Cartas de Migraciones. Su objetivo es proteger legalmente a la empresa y asegurar el ingreso sin contratiempos de los entrenadores foráneos, evitando cualquier sospecha de trabajo irregular por parte de la Superintendencia Nacional de Migraciones.

---

## 1. REGLA DE NOMENCLATURA NO LABORAL (CERO HONORARIOS)
Bajo ninguna circunstancia se debe dar a entender que el entrenador ingresa al país a ejercer una labor remunerada, ya que esto requiere una Visa de Trabajo.

*   **Términos PROHIBIDOS en cartas de migraciones:** Trabajo, Empleo, Contrato, Honorarios, Sueldo, Pago, Staff, Trabajador.
*   **Términos OBLIGATORIOS a utilizar:** Invitado Internacional (Ad-Honorem), Participante Observador, Invitado de Honor, Intercambio Cultural y Vivencial.

## 2. REGLA DE CLÁUSULA DE PROTECCIÓN
La carta de migraciones **siempre** debe incluir la siguiente cláusula literal:
> *"Cabe resaltar que su visita tiene fines netamente de intercambio vivencial y no contempla ninguna relación laboral, subordinación ni remuneración económica dentro del territorio nacional."*

## 3. REGLA DE COINCIDENCIA EXACTA DE FECHAS (VUELOS)
Es un error crítico colocar en Migraciones únicamente los días del entrenamiento (ej. "Del 14 al 16"). Si el vuelo de regreso es el 17, el oficial de aduanas podría cuestionar el día extra.

*   **Acción requerida:** Las fechas declaradas en la carta de migraciones y en el link web deben abarcar **TODA LA ESTADÍA**, tomando como inicio la fecha del *Vuelo de Llegada* y como cierre la fecha del *Vuelo de Salida*.
*   *Ejemplo Correcto:* "Del 13 al 17 de Agosto de 2026" (cubriendo los vuelos).

## 4. REGLA DE GENERACIÓN AUTOMÁTICA (URL)
Al generar el botón de "Ver Carta para Migraciones" en las Cartas de Bienvenida, los parámetros del enlace deben ir blindados:

*   **Parámetro de Rol:** Siempre debe ser `rol=Invitado+Especial+Internacional`. **Nunca** pasar `rol=Entrenador` o `rol=Líder`.
*   **Parámetro de Fechas:** Siempre debe pasar el rango completo de los vuelos (ej. `fechas=Del+26+al+31+de+Agosto+2026`).

> **Nota para el equipo:** Estas reglas ya han sido inyectadas en el **Prompt Maestro de IA** dentro del generador de cartas (`tools/generator_ui.html`). Si utilizas dicho generador y sigues las instrucciones copiando el texto de la IA, el sistema construirá los enlaces y redactará los textos cumpliendo con este protocolo automáticamente.
