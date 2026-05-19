# Lab 12 – Hybryda: Materiały Bioluminescencji i Atmosfera Cząsteczek (bpy)

## Co zostało zrealizowane
W ramach laboratorium rozbudowano zautomatyzowaną scenę z Lab 11 o zaawansowaną kontrolę shaderów oraz autorski, proceduralny system cząsteczkowy sterowany z poziomu Python API (`bpy`). Zaimplementowano dwa niezależne skrypty:

1.  **`materialyanimacja.py` (Część A):**
    * Uzyskano bezpośredni dostęp do drzewa węzłów materiału `Roslina_Bioluminescencja` i zautomatyzowano suwaki shadera `Emission`.
    * Zaimplementowano sinusoidalne pulsowanie parametru `Strength` (mocy świecenia), które zostało **zsynchronizowane z czasem rozkwitu pąka** (klatki 30–90), gdzie maksymalna wartość skacze z bazowego 1.5 do 8.0.
    * Zaprogramowano płynną zmianę koloru emisji (`Color`) od kosmicznego błękitu na starcie do biotoksynowej zieleni na końcu osi czasu (klatka 125).
    * **Dodatek dla chętnych:** Skrypt automatycznie animuje tło świata (`World Background`), ściemniając je z domyślnej szarości do głębokiego mroku, co drastycznie podnosi kontrast wizualny całej sceny.

2.  **`czasteczki_atmosfera.py` (Część B):**
    * Stworzono obiektową strukturę minisilnika cząsteczkowego przy użyciu klasy `Czasteczka`, która zarządza pełnym cyklem życia 45 zarodników.
    * W celu uzyskania maksymalnej widoczności w ciemnej scenie, bazową średnicę pyłków **zwiększono do wartości 0.15**, a ich geometrię wygenerowano wydajnie w pamięci za pomocą modułu `bmesh`.
    * Pyłki są uwalniane falami (co 12 klatek) i symulują trójfazowy cykl życia: narodziny (skalowanie w górę od 0.0 do 1.0), pełne życie (dryft w osi X udający wiatr oraz sinusoidalne falowanie w osi Z) i śmierć (zanikanie skali do 0.0).
    * Wszystkie wygenerowane kule współdzielą jeden zoptymalizowany, złoty materiał o potężnej mocy świecenia (`Strength = 12.0`), co w połączeniu z efektem Bloom daje kinowy efekt poświaty.

Oba skrypty spełniają warunek **idempotentności** – ponowne uruchomienie kodu automatycznie czyści stare krzywe animacji (`F-Curves`) oraz usuwa obiekty z kolekcji `Pyl`, budując je od zera bez duplikowania danych. Zastosowanie stałego ziarna losowości (`random.seed(42)`) gwarantuje powtarzalność wyników.

## Uruchomienie
1.  Otwórz plik sceny z poprzedniego laboratorium i zapisz jako **`swiatozywiony12.blend`**.
2.  Przejdź do zakładki **Scripting** u góry ekranu.
3.  Otwórz lub wklej skrypt `materialyanimacja.py` i uruchom go za pomocą **Run Script** (`Alt + P`).
4.  Otwórz lub wklej skrypt `czasteczki_atmosfera.py` i również go uruchom (`Alt + P`).
5.  Aby zobaczyć pełne efekty poświaty, przełącz widok okna 3D na **Rendered Shading** (skrót `Z` $\rightarrow$ *Rendered*).
6.  Wyrenderuj gotowy plik wideo MP4 za pomocą skrótu **Ctrl + F12**.

## Trudności / refleksja
Głównym wyzwaniem w Części A było poprawne adresowanie zagnieżdżonych struktur danych w grafie shaderów z poziomu kodu (operowanie na cudzysłowach wewnątrz `data_path` dla węzła `Emission`). 

W Części B pierwotne zastosowanie operatorów `bpy.ops.mesh.primitive_uv_sphere_add()` powodowało błędy relacji z kolekcjami (`RuntimeError: Object not in collection`), ponieważ Blender domyślnie wrzucał sfery do aktywnego katalogu, uniemożliwiając ich późniejsze poprawne odlinkowanie z głównej sceny. Problem ten rozwiązano poprzez całkowitą rezygnację z operatorów na rzecz niskopoziomowej generacji meshu przez `bmesh` bezpośrednio w pamięci i linkowanie go wyłącznie do docelowej kolekcji `Pyl`. Ponadto, ze względu na specyfikę nowszych wersji Blendera, zrezygnowano z wymuszania efektu Bloom przez kod na rzecz łatwiejszego zarządzania nim z poziomu panelu ustawień renderowania w GUI.