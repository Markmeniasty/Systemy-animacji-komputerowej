# Lab 13 – Eksport z Blendera, Scena i GLTFLoader w Three.js

## Co zostało zrealizowane
W ramach laboratorium pomyślnie przeniosłem trójwymiarowy, biomechaniczny świat stworzony we wcześniejszych zadaniach w Blenderze (roślina, pająk *Archnobot* oraz cząsteczki) prosto do przeglądarki internetowej. 

Zrealizowałem pełny pipeline eksportu: od przygotowania geometrii w Blenderze (czyszczenie transformacji za pomocą *Apply All Transforms*, optymalizacja siatek i ustawienie osi `+Y Up`), aż po asynchroniczne załadowanie pliku `.glb` przy użyciu komponentu `GLTFLoader` z wykorzystaniem mechanizmu `async/await`. 

Scena w Three.js została zbudowana bez użycia bundlerów (Webpack/Vite), w oparciu o natywne moduły ESM i `<script type="importmap">` pobierany z CDN (unpkg). Aplikacja spełnia najwyższe wymagania jakościowe:
* Zaimplementowałem pełne oświetlenie typu **Three-Point Light** (Key, Fill, Rim) wspierane przez delikatne światło otoczenia (`AmbientLight`).
* Skonfigurowałem mapowanie tonów (`ACESFilmicToneMapping`) oraz przestrzeń barw (`SRGBColorSpace`), aby kolory i cienie były odwzorowane identycznie jak w renderach z Blendera.
* Dodałem automatyczne kadrowanie i centrowanie kamery na podstawie gabarytów modelu przy użyciu klasy `THREE.Box3`.
* Scena posiada pełną obsługę responsywności (resize okna), kontrolę orbitalną (`OrbitControls` z włączonym tłumieniem `enableDamping`) oraz płynną animację obrotu świata i pulsowania pąków rośliny skalowaną przez `delta time` z `THREE.Clock`.

## Uruchomienie
Projekt nie wymaga instalacji Node.js ani żadnych pakietów `npm`. Ze względu na zabezpieczenia przeglądarek przed błędami CORS przy asynchronicznym pobieraniu plików lokalnych (protokół `file://`), projekt **musi** być uruchamiany przez lokalny serwer HTTP.

1.  Otwórz folder `lab13/` w programie **VS Code**.
2.  Upewnij się, że masz zainstalowane rozszerzenie **Live Server**.
3.  Kliknij prawym przyciskiem myszy na plik `index.html` i wybierz opcję **Open with Live Server** (lub kliknij przycisk *Go Live* w prawym dolnym rogu edytora).
4.  Strona otworzy się automatycznie w przeglądarce pod adresem `http://127.0.0.1:5500/`.

## Trudności / refleksja
Głównym wyzwaniem na tym etapie okazało się poprawne przygotowanie modelu przed samym eksportem z Blendera. Brak wcześniejszego wywołania operacji *Apply Transforms* powodował błędy w skali po załadowaniu do Three.js, przez co model stawał się niewidoczny dla kamery. 

Dodatkowo, kluczowe było zrozumienie polityki CORS nowoczesnych przeglądarek – próba standardowego otwarcia pliku `index.html` podwójnym kliknięciem z poziomu eksploratora plików całkowicie blokowała ładowanie modułów JavaScript oraz pliku `.glb`, co wymusiło stałe korzystanie z lokalnego serwera deweloperskiego. Bardzo pomocne przy debugowaniu ciemnej sceny okazało się wdrożenie pomocników wizualnych, takich jak `AxesHelper` oraz `DirectionalLightHelper`.