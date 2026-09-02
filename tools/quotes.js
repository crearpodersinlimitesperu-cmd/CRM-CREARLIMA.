var transformationQuotes = window.transformationQuotes || [
    { text: "Tú y yo poseemos dentro de nosotros mismos en cada momento de nuestras vidas, bajo todas las circunstancias, el poder de transformar la calidad de nuestras vidas.", author: "Werner Erhard" },
    { text: "La transformación no es un evento futuro. Es una actividad actual.", author: "Jillian Michaels" },
    { text: "Cada experiencia negativa contiene la semilla de la transformación.", author: "Alan Cohen" },
    { text: "El amor es el catalizador de la transformación de la limitación a la libertad.", author: "Harold Becker" },
    { text: "Hermosos son aquellos cuyo quebrantamiento da origen a la transformación y la sabiduría.", author: "Juan Marcos Verde" },
    { text: "Nada sucede hasta que el dolor de permanecer igual supera el dolor del cambio.", author: "Arturo Burt" },
    { text: "Ya que no podemos cambiar la realidad, cambiemos los ojos que ven la realidad.", author: "Nikos Kazantzakis" },
    { text: "La vida y la muerte son ilusiones. Estamos en un constante estado de transformación.", author: "Alejandro González Iñárritu" },
    { text: "Debes ser el cambio que deseas ver en el mundo.", author: "Mahatma Gandhi" },
    { text: "Si no te gusta algo, cámbialo. Si no lo puedes cambiar, cambia tu actitud.", author: "Maya Angelou" },
    { text: "Si cambias el modo en que miras las cosas, las cosas que miras cambian.", author: "Wayne Dyer" },
    { text: "Eres tan joven como la última vez que cambiaste tu mente.", author: "Albert Einstein" },
    { text: "Existir es cambiar, cambiar es madurar, madurar es crearse a sí mismo sin cesar.", author: "Henri Bergson" },
    { text: "El cambio más efectivo es el autodirigido.", author: "Brian Tracy" },
    { text: "Ayer fui inteligente y quise cambiar el mundo; hoy soy sabio y voy a cambiarme a mí mismo.", author: "Rumi" },
    { text: "Cuando no somos capaces de cambiar una situación, nos enfrentamos al reto de cambiar nosotros mismos.", author: "Viktor Frankl" },
    { text: "Todo el mundo piensa en cambiar el mundo, pero nadie piensa en cambiarse a sí mismo.", author: "Alexei Tolstoi" },
    { text: "El cambio es la ley de la vida. Y aquellos que miran solo al pasado o al presente se perderán seguro el futuro.", author: "John F. Kennedy" },
    { text: "Mejorar es cambiar; ser perfecto es cambiar a menudo.", author: "Winston Churchill" },
    { text: "Todo cambia; nada es.", author: "Heráclito" },
    { text: "La vida es una serie de cambios naturales y espontáneos. No los resistas, eso solo crea dolor.", author: "Lao Tse" },
    { text: "El poder de la auto-transformación está en tus manos.", author: "Tony Robbins" },
    { text: "Cada día tienes la oportunidad de reinventarte.", author: "Oprah Winfrey" },
    { text: "Nada es eterno, todo cambia.", author: "Buda" },
    { text: "El cambio crea nuevos mundos.", author: "Marcel Proust" },
    { text: "El cambio es un asunto de perspectiva.", author: "Deepak Chopra" },
    { text: "Un cambio prepara otro.", author: "André Malraux" },
    { text: "Todo gran cambio es precedido por el caos.", author: "Deepak Chopra" },
    { text: "Cuando tomas una elección, cambias el futuro.", author: "Joe Dispenza" },
    { text: "El acto más creativo que jamás emprenderás es el acto de crearte a ti mismo.", author: "Deepak Chopra" },
    { text: "Cambia tu energía y cambiarás tu mente, tus emociones y tu realidad.", author: "Joe Dispenza" },
    { text: "La transformación comienza cuando decides ser quien realmente eres.", author: "Joe Dispenza" },
    { text: "Permite que la experiencia interior te convierta en una personalidad nueva.", author: "Joe Dispenza" },
    { text: "Cambiar tu vida es cambiar tu energía para poder generar un cambio en tu mente y en tus emociones.", author: "Joe Dispenza" },
    { text: "Cuando quien aparentas ser es quien eres realmente, es cuando eres libre de verdad.", author: "Joe Dispenza" },
    { text: "Los sentimientos y los pensamientos unidos en un estado del ser generan una realidad.", author: "Joe Dispenza" },
    { text: "Serás transformado por lo que lees, por lo que piensas y por lo que vives.", author: "Jim Rohn" },
    { text: "No importa quién seas, no importa lo que hayas hecho, no importa de dónde vengas, siempre puedes cambiar, convertirte en una versión mejor de ti mismo.", author: "Madonna" },
    { text: "El cambio es la puerta de entrada a la progresión y al crecimiento.", author: "Tony Robbins" },
    { text: "No podemos convertirnos en lo que queremos permaneciendo en lo que somos.", author: "Max DePree" },
    { text: "El primer paso hacia el cambio es la conciencia. El segundo paso es la aceptación.", author: "Nathaniel Branden" },
    { text: "No puedes tener un nuevo comienzo si disfrutas aferrado al pasado.", author: "Catherine Pulsifer" },
    { text: "El cambio no es solo una opción, es una necesidad para alcanzar el crecimiento y la felicidad.", author: "Jim Rohn" },
    { text: "No hay fuerza más poderosa que un individuo decidido a cambiar su vida.", author: "Les Brown" },
    { text: "Una pasión verdadera transforma de pronto al adolescente en hombre.", author: "Johann Wolfgang von Goethe" },
    { text: "Nada parece en el universo, cuanto en él acontece no pasa de meras transformaciones.", author: "Pitágoras" },
    { text: "Los filósofos no han hecho más que interpretar de diversos modos el mundo, pero de lo que se trata es de transformarlo.", author: "Karl Marx" },
    { text: "El hombre absurdo es el que no cambia nunca.", author: "Georges Clemenceau" },
    { text: "Cuando no se puede lograr lo que se quiere, mejor cambiar de actitud.", author: "Terencio" },
    { text: "El cambio no solamente es necesario en la vida, es la vida misma.", author: "Alvin Toffler" },
    { text: "Si quieres cambiar el mundo, cámbiate a ti mismo.", author: "Mahatma Gandhi" },
    { text: "Las personas cambian cuando se dan cuenta del potencial que tienen para cambiar las cosas.", author: "Gloria Steinem" },
    { text: "Nadie puede ser esclavo de su identidad: cuando surge una posibilidad de cambio, hay que cambiar.", author: "Elliot Gould" }
];

document.addEventListener('DOMContentLoaded', () => {
    const quoteElement = document.getElementById('random-quote');
    const authorElement = document.getElementById('random-author');
    
    if (quoteElement && authorElement) {
        const randomIndex = Math.floor(Math.random() * transformationQuotes.length);
        const randomQuote = transformationQuotes[randomIndex];
        
        quoteElement.textContent = `"${randomQuote.text}"`;
        authorElement.textContent = `— ${randomQuote.author}`;
    }
});
