/**
 * * ZADANIE 4: Klasa Particle (Cząsteczka)
 * Odpowiedzialność: Pojedynczy element fizyczny, zarządzanie własnym cyklem życia.
 */
class Particle {
    constructor() {
        this.active = false; // Zadanie 4: Flaga aktywności (zarządzanie pamięcią)
    }

    /**
     * Zadanie 6 (*): Object Pooling - Metoda resetująca zamiast tworzenia nowej instancji.
     * Implementuje wymagania z Zadania 4: Pozycja, prędkość, kolor, przezroczystość.
     */
    reset(x, y, hue) {
        this.x = x;
        this.y = y;
        this.hue = hue + (Math.random() * 40 - 20); // Zadanie 4: Kolor hue z wariancją +/- 20
        this.alpha = 1.0; // Zadanie 4: Przezroczystość początkowa
        this.decay = Math.random() * 0.015 + 0.015; // Zadanie 4: Szybkość zanikania
        this.active = true;

        // Zadanie 4: Eksplozja we wszystkich kierunkach (pełne 360°)
        // Wykorzystanie współrzędnych biegunowych dla idealnie kulistego wybuchu.
        const angle = Math.random() * Math.PI * 2;
        const force = Math.sqrt(Math.random()) * 8 + 2; 
        
        this.vx = Math.cos(angle) * force;
        this.vy = Math.sin(angle) * force;
    }

    /**
     * Zadanie 4: Metoda update(gravity, canvasHeight)
     * Implementacja fizyki: grawitacja, opór powietrza, zanikanie, kolizja.
     */
    update(gravity, canvasHeight) {
        if (!this.active) return;

        this.x += this.vx; // Aktualizacja pozycji X
        this.y += this.vy; // Aktualizacja pozycji Y
        this.vy += gravity; // Zadanie 4: Stosowanie grawitacji
        
        // Zadanie 4: Stosuje opór powietrza (tłumienie)
        this.vx *= 0.98;
        this.vy *= 0.98;
        
        this.alpha -= this.decay; // Zadanie 4: Powoduje zanikanie

        // Zadanie 4: Kolizja z podłożem (Kryterium na ocenę 4.0)
        if (this.y >= canvasHeight) {
            this.y = canvasHeight;
            this.vy *= -0.4; // Odwrócenie składowej pionowej z tłumieniem
        }

        // Zadanie 4: Ustawia active = false, gdy alpha <= 0 (Koniec cyklu życia)
        if (this.alpha <= 0) this.active = false;
    }

    /**
     * Zadanie 4: Metoda draw(ctx)
     * Implementacja modelu kolorów HSLA.
     */
    draw(ctx) {
        if (!this.active) return;

        // Efekt dodatkowy: Przejście z białego jądra wybuchu do koloru docelowego
        const lightness = 50 + (this.alpha * 50); 
        
        // Zadanie 4: Ustawienie koloru przez hsla()
        ctx.fillStyle = `hsla(${this.hue}, 100%, ${lightness}%, ${this.alpha})`;
        ctx.beginPath();
        // Cząsteczka lekko maleje wraz z zanikaniem (dynamika wizualna)
        ctx.arc(this.x, this.y, 1 + this.alpha, 0, Math.PI * 2);
        ctx.fill();
    }
}

/**
 * Dodatkowa Klasa Flash
 * Wspiera efekt świetlny (Zadanie 6*) poprzez krótki rozbłysk tła przy eksplozji.
 */
class Flash {
    constructor() {
        this.active = false;
    }

    reset(x, y, hue) {
        this.x = x;
        this.y = y;
        this.hue = hue;
        this.alpha = 0.5; 
        this.active = true;
    }

    update() {
        if (!this.active) return;
        this.alpha -= 0.07; 
        if (this.alpha <= 0) this.active = false;
    }

    draw(ctx) {
        if (!this.active) return;
        const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, 250);
        grad.addColorStop(0, `hsla(${this.hue}, 100%, 95%, ${this.alpha})`);
        grad.addColorStop(1, 'transparent');
        
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 250, 0, Math.PI * 2);
        ctx.fill();
    }
}

/**
 * ZADANIE 4: Klasa Firework (Rakieta)
 * Odpowiedzialność: Zarządzanie fazą lotu i inicjowanie eksplozji.
 */
class Firework {
    constructor(targetX, targetY, startX, hue) {
        this.x = startX;
        this.y = window.innerHeight; // Start z dolnej krawędzi
        this.targetX = targetX;
        this.targetY = targetY;
        this.hue = hue;
        this.speed = 9; // Zadanie 4: Stała prędkość lotu
        this.active = true;
        this.exploded = false;

        // Zadanie 4: Wyznaczanie wektora prędkości do celu
        const angle = Math.atan2(targetY - this.y, targetX - this.x);
        this.vx = Math.cos(angle) * this.speed;
        this.vy = Math.sin(angle) * this.speed;
    }

    /**
     * Zadanie 4: Faza 1 — Lot
     */
    update() {
        this.x += this.vx;
        this.y += this.vy;

        // Zadanie 4: Detekcja osiągnięcia celu (odległość < progu)
        const dist = Math.hypot(this.targetX - this.x, this.targetY - this.y);
        if (dist < 10 || this.y < this.targetY) {
            this.exploded = true; // Zadanie 4: Faza 2 — Eksplozja
            this.active = false;
        }
    }

    draw(ctx) {
        ctx.fillStyle = `white`; 
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

/**
 * ZADANIE 4: Klasa FireworkShow (Menadżer)
 * Odpowiedzialność: Komunikacja z Canvas, obsługa zdarzeń, główna pętla symulacji.
 */
class FireworkShow {
    constructor() {
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.resize();

        this.rockets = [];
        this.particlesPool = []; // Zadanie 6 (*): Pula obiektów (Object Pooling)
        this.flashPool = [];
        
        this.gravity = 0.15; // Zadanie 4: Parametr symulacji
        this.particleCount = 100; // Zadanie 4: Liczba cząsteczek eksplozji

        this.lastTime = performance.now();
        this.fpsElement = document.getElementById('fps');

        this.initPools();
        this.setupEventListeners();
        this.autoFire(); // Zadanie 5 (5.0): Automatyczny pokaz
        this.render(); // Zadanie 4: Pętla główna
    }

    /**
     * Zadanie 6 (*): Object Pooling - Inicjalizacja stałych tablic instancji.
     */
    initPools() {
        for (let i = 0; i < 6000; i++) this.particlesPool.push(new Particle());
        for (let i = 0; i < 15; i++) this.flashPool.push(new Flash());
    }

    /**
     * Zadanie 4: Zarządzanie aktywacją blasku przy wybuchu.
     */
    spawnFlash(x, y, hue) {
        for (let f of this.flashPool) {
            if (!f.active) {
                f.reset(x, y, hue);
                break;
            }
        }
    }

    /**
     * Zadanie 4: Inicjowanie eksplozji (Faza 2)
     * Zamiast tworzyć tablicę, aktywujemy cząsteczki z puli (Object Pooling).
     */
    spawnParticles(x, y, hue) {
        let count = 0;
        for (let p of this.particlesPool) {
            if (!p.active) {
                p.reset(x, y, hue);
                count++;
                if (count >= this.particleCount) break;
            }
        }
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    /**
     * Zadanie 4: Obsługa zdarzeń (mousedown / click).
     * Zadanie 5 (5.0): Obsługa suwaków (Panel sterowania).
     */
    setupEventListeners() {
        window.addEventListener('resize', () => this.resize());
        this.canvas.addEventListener('mousedown', (e) => {
            this.rockets.push(new Firework(e.clientX, e.clientY, e.clientX, Math.random() * 360));
        });

        // Zadanie 5 (5.0): Zmiana parametrów symulacji w czasie rzeczywistym
        document.getElementById('gravity').addEventListener('input', (e) => {
            this.gravity = parseFloat(e.target.value);
            document.getElementById('grav-val').innerText = this.gravity;
        });
        document.getElementById('particleCount').addEventListener('input', (e) => {
            this.particleCount = parseInt(e.target.value);
            document.getElementById('part-val').innerText = this.particleCount;
        });
    }

    /**
     * Zadanie 5 (5.0): Automatyczny pokaz rakiet co N sekund.
     */
    autoFire() {
        setInterval(() => {
            if (this.rockets.length < 3) {
                const x = Math.random() * this.canvas.width;
                const y = Math.random() * (this.canvas.height * 0.4);
                this.rockets.push(new Firework(x, y, x, Math.random() * 360));
            }
        }, 1200);
    }

    /**
     * Zadanie 4: Pętla główna render() korzystająca z requestAnimationFrame.
     */
    render() {
        // Licznik FPS dla Zadania 6 (*)
        const now = performance.now();
        const delta = now - this.lastTime;
        this.lastTime = now;
        if (this.fpsElement && Math.random() < 0.1) {
            this.fpsElement.innerText = `FPS: ${Math.round(1000/delta)}`;
        }

        /**
         * Zadanie 6 (*): Efekt Trails.
         * Zamiast czyszczenia clearRect(), rysujemy półprzezroczysty prostokąt.
         */
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        /**
         * Zadanie 6 (*): GlobalCompositeOperation.
         * Tryb 'lighter' dla efektu Bloom i addytywnego mieszania kolorów.
         */
        this.ctx.globalCompositeOperation = 'lighter';

        // 1. Aktualizacja i rysowanie rakiet (Zadanie 4)
        for (let i = this.rockets.length - 1; i >= 0; i--) {
            const r = this.rockets[i];
            r.update();
            r.draw(this.ctx);
            if (r.exploded) {
                this.spawnFlash(r.x, r.y, r.hue);
                this.spawnParticles(r.x, r.y, r.hue);
                this.rockets.splice(i, 1); // Usuwanie rakiety po wybuchu
            }
        }

        // 2. Aktualizacja i rysowanie blasków
        this.flashPool.forEach(f => {
            if (f.active) {
                f.update();
                f.draw(this.ctx);
            }
        });

        // 3. Aktualizacja i rysowanie cząsteczek (Zadanie 4)
        this.particlesPool.forEach(p => {
            if (p.active) {
                p.update(this.gravity, this.canvas.height);
                p.draw(this.ctx);
            }
        });

        // Przywrócenie domyślnego trybu mieszania
        this.ctx.globalCompositeOperation = 'source-over';
        requestAnimationFrame(() => this.render());
    }
}

// Inicjalizacja systemu
new FireworkShow();