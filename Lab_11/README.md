# Lab 11 – Hybryda: Animacja Geometrii Rośliny przez bpy

**Ważną zmianą względem pierwotnych założeń było **użycie innej rośliny** niż ten przygotowany bezpośrednio w Lab 07. Decyzja ta wynikała z faktu, że pierwotny model był w dużej mierze jedną bryłą (pojedynczym meshem). Aby umożliwić niezależną animację każdego liścia i pąka przez skrypt Python, konieczne było zastosowanie modelu o rozbitej strukturze obiektów (oddzielne obiekty dla liści, łodygi i części kwiatu).** 

## Co zostało zrealizowane
W ramach laboratorium zrealizowano automatyzację procesu animacji assetu 3D przy użyciu skryptu Python (`bpy`). Główne funkcjonalności obejmują:
*   **Importowanie danych:** Skrypt automatycznie importuje kolekcję z zewnętrznego pliku `.blend` przy użyciu funkcji `bpy.ops.wm.append()`.
*   **Animacja proceduralna liści:** Zaimplementowano pętlę iterującą po obiektach o nazwie `Material_5`, która nakłada na nie klatki kluczowe rotacji (oś Y). Każdy liść kołysze się sinusoidalnie z indywidualnie wyliczoną fazą, co tworzy naturalny, asynchroniczny ruch.
*   **Otwieranie pąka:** Obiekty pąka (`Material`, `Material_2`, `Material_3`) zostały zaanimowane w skali (od 0.1 do 1.0) w określonym przedziale klatek (30-90), symulując proces rozkwitania.
*   **Idempotentność:** Skrypt zawiera funkcję czyszczącą istniejące klatki kluczowe przed ponownym uruchomieniem, co zapobiega dublowaniu się danych animacji.
*   **Środowisko:** Dodano proceduralne tło (Studio Backdrop) oraz konfigurację parametrów renderowania do formatu MP4 (H.264).

## Uruchomienie
1.  Otwórz program **Blender** (zalecana wersja 4.0 lub nowsza).
2.  Upewnij się, że plik źródłowy rośliny znajduje się w ścieżce zdefiniowanej w zmiennej `SCIEZKA_LAB07`.
3.  Przejdź do zakładki **Scripting**.
4.  Otwórz plik `roslinaanimacjageometrii.py` i kliknij **Run Script** (Alt+P).
5.  Aby wygenerować plik wideo, naciśnij **Ctrl+F12**.

## Trudności / refleksja
Największą trudnością techniczną było dostosowanie skryptu do specyficznego nazewnictwa obiektów w nowym assecie (gdzie nazwy obiektów odpowiadały nazwom materiałów, np. `Material_5`) oraz rozwiązanie błędu związanego z nieistniejącym atrybutem `use_glowing_effects` w nowszych wersjach silnika EEVEE.