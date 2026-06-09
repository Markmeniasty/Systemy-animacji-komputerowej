# lab_15/src/deszcz.py
import bpy
import random


class CzasteczkaDeszczu:
    def __init__(self, start_x, start_y, max_wysokosc, predkosc_opadania):
        """Klasa reprezentująca gęstą strugę deszczu."""
        self.start_x = start_x
        self.start_y = start_y
        self.max_wysokosc = max_wysokosc
        self.predkosc = predkosc_opadania
        self.kropla_obj = None

    def stworz_geometrie(self, indeks, material_deszczu):
        """Tworzy kępę kropel (kilka linii w jednym obiekcie) dla gęstszego efektu."""
        # Tworzymy główną kroplę-bazę
        bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=1.2,
                                            location=(self.start_x, self.start_y, self.max_wysokosc))
        self.kropla_obj = bpy.context.active_object
        self.kropla_obj.name = f"StrugaDeszczu_{indeks}"
        self.kropla_obj.data.materials.append(material_deszczu)

        # Aby deszcz był gęstszy bez obciążania procesora, duplikuje geometrię wewnątrz tego samego obiektu
        bpy.ops.object.mode_set(mode='EDIT')
        for _ in range(3):
            ox = random.uniform(-0.5, 0.5)
            oy = random.uniform(-0.5, 0.5)
            oz = random.uniform(-2.0, 2.0)
            bpy.ops.mesh.duplicate_move(TRANSFORM_OT_translate={"value": (ox, oy, oz)})
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.transform_apply(scale=True)

    def animuj_lot(self, klatka_startowa, ILOSC_KLATEK_ANIMACJI):
        """Animuje opadanie strugi deszczu."""
        if not self.kropla_obj:
            return

        aktualne_z = self.max_wysokosc

        for klatka in range(klatka_startowa, ILOSC_KLATEK_ANIMACJI + 1):
            self.kropla_obj.location = (self.start_x, self.start_y, aktualne_z)
            self.kropla_obj.keyframe_insert(data_path="location", frame=klatka)

            aktualne_z -= self.predkosc

            # Zapętlenie opadania (gdy spadnie na ziemię, wraca na górę)
            if aktualne_z < -5.0:
                aktualne_z = self.max_wysokosc + random.uniform(0.0, 7.0)


def generuj_system_deszczu(DLUGOSC_SEKTORA, SZEROKOSC_ULICY_TOTAL, ILOSC_KLATEK_ANIMACJI, INTENSYWNOSC_DESZCZU,
                           PREDKOSC_DESZCZU, zewnetrzny_kreator_mat):
    """Generuje ścianę deszczu na podstawie zoptymalizowanych cząsteczek."""
    mat_deszcz = zewnetrzny_kreator_mat("Mat_Deszcz_Sygnalny", (0.8, 0.8, 0.95), roughness=0.1, emission=2.0)

    zasięg_x = SZEROKOSC_ULICY_TOTAL / 2 + 5.0
    zasięg_y = DLUGOSC_SEKTORA / 2
    wysokosc_chmury = 30.0

    for i in range(INTENSYWNOSC_DESZCZU):
        x = random.uniform(-zasięg_x, zasięg_x)
        y = random.uniform(-zasięg_y, zasięg_y)
        z = random.uniform(wysokosc_chmury * 0.4, wysokosc_chmury)
        v = PREDKOSC_DESZCZU * random.uniform(0.9, 1.3)

        kropla = CzasteczkaDeszczu(start_x=x, start_y=y, max_wysokosc=z, predkosc_opadania=v)
        kropla.stworz_geometrie(indeks=i, material_deszczu=mat_deszcz)

        klatka_start = random.randint(1, 5)
        kropla.animuj_lot(klatka_start, ILOSC_KLATEK_ANIMACJI)