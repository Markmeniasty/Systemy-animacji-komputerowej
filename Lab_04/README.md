# **Lab 04 – Proceduralna roślina biomechaniczna w Blenderze**

**Co zostało zrealizowane**

W ramach laboratorium zaimplementowałem w pełni proceduralny generator biomechanicznych roślin, spełniający wszystkie kryteria na ocenę 5.0 (bardzo dobrą) oraz realizujący zadania dodatkowe.

**Moje rozwiązanie obejmuje:**

* Modułową strukturę kodu: Zamiast jednego długiego skryptu, stworzyłem osobne, wyspecjalizowane funkcje do generowania łodygi, liści (stworz\_liscie\_rozlozone) oraz korzeni, co zapewnia czytelność i łatwą modyfikację parametrów.  
* Zaawansowaną parametryzację: Główna funkcja stworz\_rosline pozwala na dynamiczną zmianę wysokości, zagęszczenia liści oraz ich długości. Dzięki temu w jednej scenie wygenerowałem trzy zróżnicowane warianty roślin (małą, średnią i dużą).  
* Zadania dodatkowe (Trygonometria): Do rozmieszczenia liści i korzeni wykorzystałem funkcje math.sin() oraz math.cos(). Liście nie wyrastają z jednego punktu, lecz są rozłożone spiralnie wzdłuż łodygi (fyllotaksja), co nadaje im naturalny, a jednocześnie techniczny wygląd.  
* Styl biomechaniczny: Opracowałem proceduralne materiały z pionowymi gradientami i efektem emisji (neonowe krawędzie). Wykorzystałem silnik Eevee wraz z oświetleniem typu *Area* i *Rim Light*, aby uzyskać futurystyczny klimat.  
* Pełną hierarchię (Parenting): Wszystkie elementy (liście, korzenie) są automatycznie przypisywane do łodygi jako obiekty podrzędne, co pozwala na wygodne zarządzanie sceną w Outlinerze.  
* Automatyzację środowiska: Skrypt na starcie czyści scenę, a na końcu automatycznie ustawia kamerę, metaliczną podłogę z odbiciami oraz wymusza tryb widoku *Rendered*.  
    
    
    
  


**Najważniejsze elementy techniczne:**

* Geometria: Wykorzystałem prymitywy Cube i Cylinder, które odpowiednio przeskalowałem i obróciłem, aby nadać im organiczny, a zarazem technologiczny wygląd (liście przypominają smukłe panele lub ostrza).  
* Matematyka: Zastosowałem funkcje trygonometryczne sin i cos oraz tzw. złoty kąt, aby liście i korzenie układały się w naturalną spiralę wokół głównej osi, nie nachodząc na siebie.  
* Cieniowanie: Stworzyłem materiały z gradientami kolorów, które reagują na wysokość obiektu, oraz dodałem efekt emisji (świecenia), co podkreśla styl biomechaniczny.  
* Scena: Skrypt automatycznie ustawia oświetlenie (Area i Point Light), kamerę oraz metaliczną podłogę z odbiciami.

## **Uruchomienie**

Aby uruchomić projekt, wykonaj poniższe kroki:

1. Otwórz Blender (zalecana wersja 5.1.0).  
2. Przejdź do obszaru roboczego Scripting.  
3. Otwórz plik skrypt.py lub wklej jego zawartość do nowego edytora tekstowego wewnątrz Blendera.  
4. Kliknij przycisk Run Script (ikona "Play").  
5. Aby zobaczyć finalny efekt z neonami i gradientami, przełącz widok w oknie 3D na Rendered (skrót klawiszowy Z \-\> Rendered).

## **Trudności / refleksja**

Największym wyzwaniem okazało się poprawne ustawienie hierarchii obiektów (parenting) z poziomu kodu. Odkryłem, że samo przypisanie parent nie wystarczy i trzeba użyć matrix\_parent\_inverse, aby liście nie "odlatywały" od łodygi podczas zmiany jej skali. Ciekawe było również zderzenie z różnymi wersjami silnika Eevee – musiałem dodać w kodzie warunki sprawdzające, czy dana wersja Blendera obsługuje efekt *Bloom*, aby skrypt był uniwersalny i nie wyrzucał błędów na różnych komputerach w laboratorium.

