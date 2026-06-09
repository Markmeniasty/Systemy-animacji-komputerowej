import bpy
import math


def generuj_kamere_pov(SZEROKOSC_PASA, SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA, ILOSC_KLATEK_ANIMACJI):
    bpy.ops.object.camera_add()
    kam = bpy.context.active_object
    kam.name = "Kamera_POV"
    bpy.context.scene.camera = kam

    wysokosc_glowy = 1.75
    start_x = (SZEROKOSC_PASA) + (SZEROKOSC_CHODNIKA / 2)
    start_y = -DLUGOSC_SEKTORA / 2 + 5.0
    kam.rotation_euler = (1.5708, 0.0, 0.0)

    for klatka in range(1, ILOSC_KLATEK_ANIMACJI + 1):
        t = (klatka - 1) / (ILOSC_KLATEK_ANIMACJI - 1)
        aktualny_y = start_y + (DLUGOSC_SEKTORA * 0.4) * t

        predkosc_kroku = klatka * 0.25
        szum_z = math.sin(predkosc_kroku * 2) * 0.04
        aktualny_z = wysokosc_glowy + szum_z

        szum_x = math.cos(predkosc_kroku) * 0.06
        aktualny_x = start_x + szum_x

        kam.rotation_euler[1] = math.cos(predkosc_kroku) * 0.02
        kam.rotation_euler[2] = math.sin(predkosc_kroku) * 0.01

        kam.location = (aktualny_x, aktualny_y, aktualny_z)
        kam.keyframe_insert(data_path="location", frame=klatka)
        kam.keyframe_insert(data_path="rotation_euler", frame=klatka)


def stworz_fizyczna_lampe(car_obj, px, py, pz, kolor_rgb, moc, nazwa, kierunek_y):
    """Tworzy widoczne, świecące kółko (lampę) na bryle samochodu."""
    # Tworze płaski cylinder (dysk) udający reflektor
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.05, location=(px, py, pz))
    lampa_mesh = bpy.context.active_object
    lampa_mesh.name = f"Mesh_{nazwa}_{car_obj.name}"

    # Obracam kółko reflektora przodem do kierunku jazdy
    lampa_mesh.rotation_euler = (1.5708, 0.0, 0.0)

    # Tworze dla niego materiał mocno świecący (Emission)
    mat = bpy.data.materials.new(name=f"Mat_{nazwa}_{car_obj.name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')

    node_principled.inputs['Base Color'].default_value = (*kolor_rgb, 1.0)
    node_principled.inputs['Emission Color'].default_value = (*kolor_rgb, 1.0)
    node_principled.inputs['Emission Strength'].default_value = moc

    mat.node_tree.links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])
    lampa_mesh.data.materials.append(mat)

    # Łącze z samochodem jako rodzicem, żeby lampa poruszała się razem z nim
    lampa_mesh.parent = car_obj


def stworz_reflektor_swiatlo(car_obj, przesuniecie_x, przesuniecie_y, przesuniecie_z, kierunek_y):
    """Generuje ostre źródło światła SPOT wychodzące prosto z białego reflektora."""
    bpy.ops.object.light_add(type='SPOT', radius=0.1)
    spot = bpy.context.active_object
    spot.name = f"Swiatlo_Reflektor_{car_obj.name}"

    spot.data.energy = 18000.0  # moc dla ostrego błysku
    spot.data.spot_size = 0.45  # Wąski, skupiony promień (iskra)
    spot.data.spot_blend = 0.2
    spot.data.color = (0.95, 0.98, 1.0)  # Zimny, jasny odcień ksenonu
    spot.data.use_shadow = False  # Wyłączone cienie, aby auto nie blokowało światła

    kat_pochylenia = 0.015

    if kierunek_y > 0:
        spot.rotation_euler = (kat_pochylenia, 0.0, 0.0)
    else:
        spot.rotation_euler = (3.14159 - kat_pochylenia, 0.0, 0.0)

    spot.parent = car_obj
    spot.location = (przesuniecie_x, przesuniecie_y, przesuniecie_z)


def generuj_samochody(SZEROKOSC_PASA, DLUGOSC_SEKTORA, ILOSC_KLATEK_ANIMACJI, zewnetrzny_kreator_mat):
    """Generuje samochody z widocznymi, świecącymi białymi reflektorami z przodu i czerwonymi z tyłu."""
    mat_auto1 = zewnetrzny_kreator_mat("Mat_Auto_1", (0.3, 0.01, 0.01), roughness=0.1)
    mat_auto2 = zewnetrzny_kreator_mat("Mat_Auto_2", (0.01, 0.01, 0.03), roughness=0.1)

    # ==========================================
    # AUTO 1 (Oddala się od nas, przód do +Y)
    # ==========================================
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    auto1 = bpy.context.active_object
    auto1.name = "Samochod_OddalajacySie"
    auto1.scale = (1.8, 4.0, 1.4)
    auto1.data.materials.append(mat_auto1)
    bpy.ops.object.transform_apply(scale=True)

    pas_lewy_x = -SZEROKOSC_PASA / 2
    for klatka in range(1, ILOSC_KLATEK_ANIMACJI + 1):
        t = (klatka - 1) / (ILOSC_KLATEK_ANIMACJI - 1)
        y_pos = (-DLUGOSC_SEKTORA / 3) + (DLUGOSC_SEKTORA * 0.8) * t
        auto1.location = (pas_lewy_x, y_pos, 0.7)
        auto1.keyframe_insert(data_path="location", frame=klatka)

    # PRZÓD (+Y): Białe świecące kółka
    stworz_fizyczna_lampe(auto1, -0.6, 2.01, 0.2, (1.0, 1.0, 1.0), moc=15.0, nazwa="Reflektor_L", kierunek_y=1)
    stworz_fizyczna_lampe(auto1, 0.6, 2.01, 0.2, (1.0, 1.0, 1.0), moc=15.0, nazwa="Reflektor_P", kierunek_y=1)
    # Źródła światła wychodzące z białych kółek
    stworz_reflektor_swiatlo(auto1, -0.6, 2.1, 0.2, kierunek_y=1)
    stworz_reflektor_swiatlo(auto1, 0.6, 2.1, 0.2, kierunek_y=1)

    # TYŁ (-Y): Czerwone świecące kółka (pozycyjne)
    stworz_fizyczna_lampe(auto1, -0.6, -2.01, 0.2, (1.0, 0.0, 0.0), moc=8.0, nazwa="Tylne_L", kierunek_y=1)
    stworz_fizyczna_lampe(auto1, 0.6, -2.01, 0.2, (1.0, 0.0, 0.0), moc=8.0, nazwa="Tylne_P", kierunek_y=1)

    # ==========================================
    # AUTO 2 (Nadjeżdża na nas, przód do -Y)
    # ==========================================
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    auto2 = bpy.context.active_object
    auto2.name = "Samochod_Nadjezdzajacy"
    auto2.scale = (1.8, 4.0, 1.4)
    auto2.data.materials.append(mat_auto2)
    bpy.ops.object.transform_apply(scale=True)
    auto2.rotation_euler[2] = 3.14159  # Obrót o 180 stopni

    pas_prawy_x = SZEROKOSC_PASA / 2
    for klatka in range(1, ILOSC_KLATEK_ANIMACJI + 1):
        t = (klatka - 1) / (ILOSC_KLATEK_ANIMACJI - 1)
        y_pos = (DLUGOSC_SEKTORA / 2) - (DLUGOSC_SEKTORA * 0.9) * t
        auto2.location = (pas_prawy_x, y_pos, 0.7)
        auto2.keyframe_insert(data_path="location", frame=klatka)

    # PRZÓD (-Y wzgl. świata, bo auto jest obrócone – lokalnie to nadal przód sześcianu)
    stworz_fizyczna_lampe(auto2, -0.6, 2.01, 0.2, (1.0, 1.0, 1.0), moc=15.0, nazwa="Reflektor_L", kierunek_y=-1)
    stworz_fizyczna_lampe(auto2, 0.6, 2.01, 0.2, (1.0, 1.0, 1.0), moc=15.0, nazwa="Reflektor_P", kierunek_y=-1)
    # Źródła światła rzucające blask na drogę przed auto2
    stworz_reflektor_swiatlo(auto2, -0.6, 2.1, 0.2, kierunek_y=-1)
    stworz_reflektor_swiatlo(auto2, 0.6, 2.1, 0.2, kierunek_y=-1)

    # TYŁ (+Y dla obróconego auta): Czerwone świecące kółka
    stworz_fizyczna_lampe(auto2, -0.6, -2.01, 0.2, (1.0, 0.0, 0.0), moc=8.0, nazwa="Tylne_L", kierunek_y=-1)
    stworz_fizyczna_lampe(auto2, 0.6, -2.01, 0.2, (1.0, 0.0, 0.0), moc=8.0, nazwa="Tylne_P", kierunek_y=-1)