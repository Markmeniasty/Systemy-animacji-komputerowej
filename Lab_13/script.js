import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// --- ELEMENTY INTERFEJSU I ZMIENNE GLOBALNE ---
const infoDiv = document.getElementById('info');
const canvas = document.getElementById('webgl');

let scene, camera, renderer, controls, clock;
let animatedMesh = null;
let modelRoot = null;

// Główne uruchomienie aplikacji asynchronicznej
async function init() {
    try {
        // 1. SCENA I ZEGAR
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050508); // Bardzo ciemny granat/czerń pod cyberpunk
        clock = new THREE.Clock();

        // 2. KAMERA
        camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(10, 10, 10);

        // 3. RENDERER 
        renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Ustawienia kolorów i tonowania (Wymagania na 4.0)
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2; // Lekko podbita ekspozycja
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        
        // Włączenie cieni (Opcja dla chętnych)
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // 4. KONTROLA KAMERY (OrbitControls - Wymagania na 5.0)
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; 
        controls.dampingFactor = 0.05;
        controls.minDistance = 0.5;
        controls.maxDistance = 100;

        // 5. DIAGNOSTYKA: POMOCNIKI WIZUALNE
        // AxesHelper: Czerwona = X, Zielona = Y, Niebieska = Z
        const axesHelper = new THREE.AxesHelper(5);
        scene.add(axesHelper);

        // GridHelper: Siatka podłoża, żeby widzieć gdzie jest punkt (0,0,0) i czy scena żyje
        const gridHelper = new THREE.GridHelper(20, 20, 0x00ffcc, 0x444444);
        scene.add(gridHelper);

        // 6. OŚWIETLENIE THREE-POINT (Mocno podbite wartości, żeby wyeliminować czarny ekran)
        // Ambient Light - ogólne jasne wypełnienie testowe
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
        scene.add(ambientLight);

        // Key Light - główne światło kierunkowe
        const keyLight = new THREE.DirectionalLight(0xffbb88, 3.5);
        keyLight.position.set(8, 12, 8);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 2048;
        keyLight.shadow.mapSize.height = 2048;
        scene.add(keyLight);

        // Wizualizator światła głównego
        const keyLightHelper = new THREE.DirectionalLightHelper(keyLight, 1);
        scene.add(keyLightHelper);

        // Fill Light - dopełniające chłodne
        const fillLight = new THREE.DirectionalLight(0x4477ff, 2.0);
        fillLight.position.set(-8, 4, -4);
        scene.add(fillLight);

        // Rim Light - konturowe, jaskrawe z tyłu
        const rimLight = new THREE.DirectionalLight(0x00ffcc, 3.0);
        rimLight.position.set(0, 6, -10);
        scene.add(rimLight);


        // 7. ŁADOWANIE MODELU GLTF (.glb)
        infoDiv.innerText = "Ładowanie modelu biomech13.glb...";
        const loader = new GLTFLoader();
        
        const gltf = await loader.loadAsync('biomech13.glb');
        
        modelRoot = gltf.scene;
        scene.add(modelRoot);

        let meshCount = 0;
        
        modelRoot.traverse((child) => {
            if (child.isMesh) {
                meshCount++;
                child.castShadow = true;
                child.receiveShadow = true;
                
                console.log(`Pomyślnie załadowano Mesh: "${child.name}"`);

                if (child.name.toLowerCase().includes('paczki') || child.name.toLowerCase().includes('rose') || child.name.toLowerCase().includes('archnobot')) {
                    animatedMesh = child;
                    console.log(`-> Znaleziono obiekt do animacji: ${child.name}`);
                }
            }
        });

        infoDiv.innerHTML = `Model załadowany!<br>Liczba mesh-y: ${meshCount}<br><small>Użyj myszy do obracania/zoomu</small>`;

        // 8. AUTOMATYCZNE KADROWANIE KAMERY (Wymagania na 5.0)
        fitCameraToModel(modelRoot);

        // 9. OBSŁUGA ZMIANY ROZMIARU OKNA (Wymagania na 5.0)
        window.addEventListener('resize', onWindowResize);

        // 10. URUCHOMIENIE PĘTLI ANIMACJI
        animate();

    } catch (error) {
        console.error("Błąd zainicjalizowania sceny:", error);
        infoDiv.classList.add('error');
        infoDiv.innerHTML = `<strong>Błąd ładowania sceny!</strong><br>${error.message}<br><small>Sprawdź konsolę F12.</small>`;
    }
}

// Funkcja centrująca i dopasowująca kamerę do gabarytów modelu (Box3)
function fitCameraToModel(rootObject) {
    const box = new THREE.Box3().setFromObject(rootObject);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    // Pobranie największego wymiaru modelu
    const maxDim = Math.max(size.x, size.y, size.z);
    
    // Zabezpieczenie na wypadek, gdyby model był pusty lub ekstremalnie mały
    if(maxDim === 0) {
        console.warn("Uwaga: Wykryto model o zerowym rozmiarze. Kamera ustawia się domyślnie.");
        camera.position.set(5, 5, 5);
        controls.target.set(0, 0, 0);
        return;
    }

    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    
    cameraZ *= 1.8; // Margines odsunięcia kamery

    // Przeniesienie środka obrotu kamery do wnętrza modelu
    controls.target.copy(center);
    
    // Ustawienie pozycji kamery w bezpiecznej odległości
    camera.position.set(center.x + cameraZ * 0.7, center.y + cameraZ * 0.5, center.z + cameraZ * 0.7);
    camera.lookAt(center);
    
    // Ograniczenia dla OrbitControls dostosowane do skali obiektu
    controls.minDistance = maxDim * 0.1;
    controls.maxDistance = maxDim * 10;
    controls.update();
}

// Dopasowanie wymiarów przy zmianie okna przeglądarki
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Pętla renderująca oparta o Delta Time 
function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const elapsedTime = clock.getElapsedTime();

    // 1. Powolna stała rotacja całej sceny wokół osi Y (skalowana przez delta)
    if (modelRoot) {
        modelRoot.rotation.y += 0.1 * delta; // 0.1 radiana na sekundę
    }

    // 2. Subtelne, sinusoidalne pulsowanie wybranego mesha (jeśli został dopasowany)
    if (animatedMesh) {
        const pulseFactor = 1.0 + Math.sin(elapsedTime * 3.0) * 0.04;
        animatedMesh.scale.set(pulseFactor, pulseFactor, pulseFactor);
    }

    // Aktualizacja sterowania kamery
    controls.update();

    // Render klatki
    renderer.render(scene, camera);
}

// Inicjalizacja po załadowaniu drzewa DOM
window.addEventListener('DOMContentLoaded', init);