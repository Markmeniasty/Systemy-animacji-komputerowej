# Wirtualne Środowisko 3D: Cyberpunk 

**Autor:** Marek Załęski 

**Kurs:** Systemy animacji komputerowej

**Środowisko:** Blender 5.1.2 

---

## 1. Opis sceny i założeń artystycznych
Projekt przedstawia dynamiczną, trójwymiarową makietę mrocznego, cyberpunkowego korytarza miejskiego w środku nocy. Głównym założeniem artystycznym było odtworzenie kinowego, dystopijnego nastroju ulewnego deszczu w neonowym mieście. 

* **Perspektywa:** Animacja zrealizowana jest z perspektywy pierwszej osoby (POV) pieszego idącego chodnikiem. Kamera wykonuje skryptowany ruch do przodu, wzbogacony o proceduralne, matematyczne kołysanie imitujące ludzki krok.
* **Oświetlenie:** Scena osadzona jest w warunkach absolutnej nocy (całkowicie czarne tło kosmiczne, brak światła słonecznego). Jedyne źródła światła to jaskrawe, losowo migoczące neony na wieżowcach, regularnie rozstawione latarnie sodowe oraz potężne, skupione reflektory (ksenonowe "iskry") pędzących pojazdów.
* **Klimat:** Centralnym punktem budującym nastrój jest zaawansowany, proceduralny materiał asfaltu. Droga została zaprogramowana tak, by imitować mokrą nawierzchnię z lustrzanymi kałużami, w których dynamicznie odbijają się neony oraz snopy świateł mijających nas samochodów, co w połączeniu z gęstą ścianą deszczu tworzy głębię i unikalną atmosferę.

---

## 2. Instrukcja uruchomienia projektu

Aby poprawnie uruchomić projekt, wygenerować scenę oraz wyrenderować animację, wykonaj poniższe kroki:

1.  **Otwarcie środowiska:** Uruchom program **Blender** (zalecana wersja 5.0 lub nowsza) z czystą, nową sceną (`General`).
2.  **Załadowanie skryptów:**
    * Przełącz przestrzeń roboczą na zakładkę **Scripting** (górny pasek Blendera).
    * Utwórz cztery nowe karty tekstowe (przycisk `New`) i nazwij je dokładnie:
        * `infrastruktura.py`
        * `animacja_sceny.py`
        * `deszcz.py`
        * `uruchom_projekt.py`
    * Wklej zawartość odpowiednich plików źródłowych z folderu `src/` do utworzonych kart.
3.  **Generowanie sceny:** * Wejdź do zakładki z plikiem `uruchom_projekt.py`.
    * Kliknij przycisk **Run Script** (ikona strzałki w edytorze tekstu). Scena zostanie automatycznie zbudowana i oświetlona w ułamku sekundy.
4.  **Podgląd animacji:** * Ustaw kursor w oknie widoku 3D i wciśnij **Numpad 0**, aby przełączyć się na widok z kamery POV.
    * Zmień tryb wyświetlania na **Rendered** (czwarta ikona kulki w prawym górnym rogu okna 3D).
    * Wciśnij **Spację**, aby odtworzyć animację ruchu w czasie rzeczywistym.


---

## 3. Opis architektury skryptu Python i parametryzacji
Projekt został zaprojektowany w sposób w pełni modularny, rozdzielając odpowiedzialność za poszczególne elementy sceny pomiędzy niezależne komponenty:

* **`uruchom_projekt.py`**: Główny koordynator (skrypt uruchomieniowy). Czyści pamięć podręczną sceny z poprzednich obiektów, definiuje parametry globalne i wywołuje funkcje budujące z pozostałych modułów. Wykorzystuje mechanizm wirtualnych modułów wewnętrznych w celu bezpiecznego mapowania kodu z zakładek edytora tekstowego Blendera.
* **`infrastruktura.py`**: Odpowiada za generowanie siatek (meshes) ulicy, pasów i chodników. Tworzy losowe bryły budynków i dokleja do nich neony. Zawiera również proceduralne shadery: zaawansowany materiał mokrego asfaltu (sterujący mapą chropowatości *Roughness* za pomocą węzła *Noise Texture* w celu wydzielenia kałuż) oraz automatyczną konfigurację silnika renderującego Eevee (Bloom, Screen Space Reflections, Motion Blur).
* **`animacja_sceny.py`**: Generuje kamerę POV i animuje jej ruch wzdłuż osi miejskiej wraz z wprowadzeniem szumu matematycznego (funkcje `sin` i `cos`) imitującego ludzki krok. Odpowiada także za generowanie samochodów i ich fizycznych, skupionych świateł reflektorów (`SPOT`) oraz widocznych, świecących kloszy (białych z przodu, czerwonych z tyłu).
* **`deszcz.py`**: Autorski, zoptymalizowany pod kątem pamięci podręcznej silnik cząsteczkowy napisany w oparciu o programowanie obiektowe. Wykorzystuje klasę `CzasteczkaDeszczu` posiadającą własną geometrię, prędkość opadania oraz cykl życia (skrypt po uderzeniu kropli w asfalt resetuje jej pozycję na górę, tworząc pętlę ciągłego deszczu).

### Kluczowe parametry globalne (Możliwe do edycji w `uruchom_projekt.py`):
* `LICZBA_BUDYNKOW_NA_STRONE = 5` – Gęstość zabudowy korytarza miejskiego.
* `DLUGOSC_SEKTORA = 90.0` – Całkowita długość generowanej ulicy (w metrach).
* `ILOSC_KLATEK_ANIMACJI = 160` – Czas trwania filmu (160 klatek przy 24fps daje ok. 6 sekund).
* `MAX_MOC_NEONU = 25.0` – Bazowa intensywność świecenia neonów budynkowych.
* `CZESTOTLIWOSC_MIGOTANIA = 0.35` – Prawdopodobieństwo (od 0 do 1), z jakim neony losowo gasną lub mrugają na osi czasu.
* `INTENSYWNOSC_DESZCZU = 450` – Gęstość ulewy (liczba kęp kropel generowanych przez system).
* `PREDKOSC_DESZCZU = 1.6` – Prędkość opadania strug deszczu na pojedynczą klatkę.

---

## 4. Lista użytych assetów zewnętrznych
W celu wzbogacenia detali makiety miejskiej oraz nadania jej autentycznego, cyberpunkowego klimatu, w scenie wykorzystano darmowe modele 3D pochodzące z platformy i bazy danych **BlenderKit**. 

Wszystkie assety zostały pobrane i zintegrowane ze sceną na licencjach darmowych/edukacyjnych (*BlenderKit Free Asset License / Creative Commons*):

| Nazwa assetu (Model) | Źródło (Platforma) | Licencja | Zastosowanie w scenie |
| :--- | :--- | :--- | :--- |
| **Cyberpunk Sign - ENTRY** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Neonowy szyld reklamowy na elewacji wieżowców |
| **Distressed Sci-Fi Cyberpunk Crates** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Detale otoczenia – skrzynie i kontenery w zaułkach |
| **Cyberpunk Sign - Turn Right** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Światło i oznaczenie kierunkowe nad jezdnią |
| **Cyberpunk Sign - Exit** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Reklama neonowa montowana bocznie na budynkach |
| **Cyberpunk Sign - Access Left/Right** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Szyldy informacyjne nad skrzyżowaniami |
| **Sci-fi electric scooter** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Element "clutteru" – porzucona hulajnoga na chodniku |
| **Neon Sign - Exit** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Klasyczne, mniejsze źródło światła emisyjnego przy bramach |
| **Neon Sign - Cyber Cafe** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Duży, klimatyczny neon usługowy na niższych piętrach |
| **Traffic Cone Orange** | BlenderKit (baza darmowa) | BlenderKit Free / CC | Pachołek drogowy rozstawiony na pasie awaryjnym jezdni |

*Uwaga: Geometria bazowa (ulice, chodniki, rusztowania budynków, system deszczu ) jest w 100% proceduralnie za pomocą autorskich modułów skryptu Python.*
---

## 5. Znane bugi i ograniczenia
* **Wsteczna kompatybilność silnika Eevee:** W związku z gruntowną przebudową API w Blenderze 4.2+, w funkcji konfiguracji renderu zastosowano automatyczny fallback. W wersjach Blender 4.0 oraz 4.1 skrypt automatycznie przełącza się na opcję `use_ssr` oraz natywny efekt `use_bloom`, natomiast w wersjach 4.2+ parametry te wymuszane są przez system Raytracingu. Efekt końcowy może się minimalnie różnić rozmyciem poświaty w zależności od posiadanej podwersji oprogramowania.
* **Zgłaszanie ostrzeżeń o braku kontekstu:** Jeśli skrypt zostanie uruchomiony w momencie, gdy okno podglądu 3D Blendera znajduje się w trybie edycji siatki (`EDIT_MODE`) zamiast trybu obiektowego (`OBJECT_MODE`), funkcja czyszcząca scenę wymusi przełączenie trybu, co w rzadkich przypadkach na starszych wersjach systemu Windows może wywołać ostrzeżenie w konsoli systemowej (nie wpływa to jednak na końcowy render).
* **Wydajność skryptowej ulewy:** Deszcz generowany jest za pomocą klasy Pythona tworzącej kępki geometrii. Podbicie parametru `INTENSYWNOSC_DESZCZU` powyżej wartości `1500` może skutkować drastycznym spadkiem płynności (klatek na sekundę) podczas odtwarzania podglądu w Viewporcie z powodu narzutu pamięciowego operacji `keyframe_insert()` na tysiącach obiektów. Do ostatecznego renderu zaleca się pozostanie przy wartościach domyślnych (400-500).