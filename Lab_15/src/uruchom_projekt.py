import bpy
import sys
import os

# ==============================================================================
# INTELIGENTNE WYKRYWANIE I ŁADOWANIE KART TEKSTOWYCH W BLENDERZE
# ==============================================================================
dostepne_karty = [karta.name.strip().lower() for karta in bpy.data.texts]

ma_infra = any("infrastruktura" in nazwa for nazwa in dostepne_karty)
ma_anim = any("animacja_sceny" in nazwa for nazwa in dostepne_karty)
ma_deszcz = any("deszcz" in nazwa for nazwa in dostepne_karty)

if ma_infra and ma_anim and ma_deszcz:
    nazwa_infra = [k.name for k in bpy.data.texts if "infrastruktura" in k.name.lower()][0]
    nazwa_anim = [k.name for k in bpy.data.texts if "animacja_sceny" in k.name.lower()][0]
    nazwa_deszcz = [k.name for k in bpy.data.texts if "deszcz" in k.name.lower()][0]

    exec(bpy.data.texts[nazwa_infra].as_string(), globals())
    exec(bpy.data.texts[nazwa_anim].as_string(), globals())
    exec(bpy.data.texts[nazwa_deszcz].as_string(), globals())


    class WirtualnyModul:
        def __init__(self, funkcje):
            self.__dict__.update(funkcje)


    infrastruktura = WirtualnyModul(globals())
    animacja_sceny = WirtualnyModul(globals())
    deszcz = WirtualnyModul(globals())
    print(f"-> Załadowano wirtualne moduły: [{nazwa_infra}], [{nazwa_anim}], [{nazwa_deszcz}]")
else:
    opcja_sciezki = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else ""
    if opcja_sciezki and opcja_sciezki not in sys.path:
        sys.path.append(opcja_sciezki)
    import infrastruktura
    import animacja_sceny
    import deszcz

# ==============================================================================
# PARAMETRY GLOBALNE
# ==============================================================================
LICZBA_BUDYNKOW_NA_STRONE = 10
DLUGOSC_SEKTORA = 90.0
ILOSC_KLATEK_ANIMACJI = 160

SZEROKOSC_PASA = 3.5
SZEROKOSC_CHODNIKA = 2.5
SZEROKOSC_PRZECZNICY = 4.0

MIN_WYSOKOSC = 20.0
MAX_WYSOKOSC = 45.0

CZESTOTLIWOSC_MIGOTANIA = 0.35
MAX_MOC_NEONU = 25.0

# NOWE: Parametry sterujące deszczem
INTENSYWNOSC_DESZCZU = 450  # Liczba generowanych skryptowo kropel
PREDKOSC_DESZCZU = 1.3  # Jak szybko kropla opada w dół na klatkę animacji
# ==============================================================================

SZEROKOSC_ULICY_TOTAL = (SZEROKOSC_PASA * 2) + (SZEROKOSC_CHODNIKA * 2)


def wyczysc_scene():
    """Usuwa stare siatki (meshes), kamery oraz źródła światła w bezpieczny sposób."""
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    for typ_obj in ['MESH', 'CAMERA', 'LIGHT']:
        bpy.ops.object.select_by_type(type=typ_obj)

    if bpy.context.selected_objects:
        bpy.ops.object.delete()


def main():
    # 1. Przygotowanie czystego środowiska
    wyczysc_scene()

    # 2. Budowa świata (Moduł: infrastruktura)
    infrastruktura.generuj_ulice_i_chodniki(SZEROKOSC_PASA, SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA)
    infrastruktura.generuj_budynki_i_neony(
        LICZBA_BUDYNKOW_NA_STRONE, DLUGOSC_SEKTORA, SZEROKOSC_ULICY_TOTAL,
        SZEROKOSC_PRZECZNICY, MIN_WYSOKOSC, MAX_WYSOKOSC,
        ILOSC_KLATEK_ANIMACJI, CZESTOTLIWOSC_MIGOTANIA, MAX_MOC_NEONU
    )

    # Generowanie latarń ulicznych
    infrastruktura.generuj_latarnie(SZEROKOSC_PASA, SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA)

    # Ustawienie kosmicznie czarnej nocy i silnika renderującego
    infrastruktura.ustaw_nocne_srodowisko_i_render()

    # 3. Dodanie ruchu i perspektywy
    animacja_sceny.generuj_kamere_pov(SZEROKOSC_PASA, SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA, ILOSC_KLATEK_ANIMACJI)
    animacja_sceny.generuj_samochody(SZEROKOSC_PASA, DLUGOSC_SEKTORA, ILOSC_KLATEK_ANIMACJI,
                                     infrastruktura.stworz_material)

    # 4. DODANIE DESZCZU
    deszcz.generuj_system_deszczu(
        DLUGOSC_SEKTORA, SZEROKOSC_ULICY_TOTAL, ILOSC_KLATEK_ANIMACJI,
        INTENSYWNOSC_DESZCZU, PREDKOSC_DESZCZU, infrastruktura.stworz_material
    )

    # 5. Globalne ustawienia osi czasu w Blenderze
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = ILOSC_KLATEK_ANIMACJI

    print("PEŁNY PROJEKT SFINALIZOWANY! Absolutna ciemność, neony, latarnie i głębokie odbicia reflektorów działają!")


if __name__ == "__main__":
    main()