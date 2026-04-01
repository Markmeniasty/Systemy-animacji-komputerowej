class Hand {
    // Definiujemy jak wygląda wskazówka: jej długość, grubość i kolor. 
    // "tail" to ten kawałek, który wystaje poza środek zegara (ładniej wygląda).
    constructor(length, width, color, tail = 20) {
        this.length = length;
        this.width = width;
        this.color = color;
        this.tail = tail;
    }

    draw(ctx) {
        ctx.lineCap = 'round'; // Zaokrąglone końce, żeby nie było kanciasto
        ctx.strokeStyle = this.color;
        ctx.lineWidth = this.width;
        ctx.beginPath();
        // Rysujemy od ogonka (dół) do czubka (góra). 
        // Na Canvasie "góra" to wartości ujemne na osi Y, stąd -this.length.
        ctx.moveTo(0, this.tail);
        ctx.lineTo(0, -this.length);
        ctx.stroke();
    }
}

class Clock {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.radius = this.canvas.width / 2;
        this.isPaused = false;

        // Trzy wskazówki o różnych proporcjach względem tarczy
        this.hands = {
            hour: new Hand(this.radius * 0.5, 8, '#2c3e50'),
            minute: new Hand(this.radius * 0.75, 5, '#34495e'),
            second: new Hand(this.radius * 0.85, 2, '#e74c3c', 30)
        };

        this.init();
    }

    init() {
        // Pauza pod spacją
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') this.isPaused = !this.isPaused;
        });
        this.loop();
    }

    drawFace() {
        const { ctx, radius } = this;
        
        ctx.strokeStyle = '#333';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = `${radius * 0.1}px Arial`;

        // Pętla rysująca 60 kresek (minuty i sekundy)
        for (let i = 0; i < 60; i++) {
            const angle = (i * Math.PI) / 30; // 360 stopni / 60 kresek = Math.PI / 30
            ctx.save();
            ctx.rotate(angle);
            
            // Co 5 kreska jest grubsza i ma cyferkę (godziny)
            if (i % 5 === 0) {
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(0, -radius + 10);
                ctx.lineTo(0, -radius + 30);
                ctx.stroke();
                
                // Rysowanie numerów godzin
                ctx.save();
                ctx.translate(0, -radius + 45);
                ctx.rotate(-angle); // Obracam tekst z powrotem, żeby nie był do góry nogami
                const hour = i === 0 ? 12 : i / 5;
                ctx.fillText(hour.toString(), 0, 0);
                ctx.restore();
            } else {
                // Zwykła, cienka kreska minutowa
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(0, -radius + 10);
                ctx.lineTo(0, -radius + 20);
                ctx.stroke();
            }
            ctx.restore();
        }
    }

    render() {
        const { ctx, canvas, radius } = this;
        const now = new Date();

        // *** ZADANIE DODATKOWE: Efekt Spirografu ***
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.save();
        ctx.translate(radius, radius); // Przesuwam środek układu współrzędnych na środek zegara

        this.drawFace();

        // Pobieram czas i przeliczam na płynne ruchy (uwzględniam milisekundy)
        const ms = now.getMilliseconds();
        const s = now.getSeconds() + ms / 1000;
        const m = now.getMinutes() + s / 60;
        const h = (now.getHours() % 12) + m / 60;

        // Rysuje wskazówki z odpowiednim obrotem
        this.drawHand(this.hands.hour, (h * Math.PI) / 6);     // 360 stopni / 12h = PI/6
        this.drawHand(this.hands.minute, (m * Math.PI) / 30);  // 360 stopni / 60m = PI/30
        this.drawHand(this.hands.second, (s * Math.PI) / 30);

        // Środkowa kropka, żeby zakryć łączenie wskazówek
        ctx.beginPath();
        ctx.arc(0, 0, 7, 0, Math.PI * 2);
        ctx.fillStyle = '#2c3e50';
        ctx.fill();
        
        // Jeszcze mniejsza biała kropka w środku dla lepszego detalu
        ctx.beginPath();
        ctx.arc(0, 0, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();

        ctx.restore();
    }

    drawHand(hand, angle) {
        this.ctx.save();
        this.ctx.rotate(angle);
        hand.draw(this.ctx);
        this.ctx.restore();
    }

    loop() {
        // Pętla animacji. Jeśli nie ma pauzy, rysujemy klatkę.
        if (!this.isPaused) this.render();
        requestAnimationFrame(() => this.loop());
    }
}

new Clock('clock');