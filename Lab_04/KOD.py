import bpy
import math


def czysc_scene():
    """Usuwa wszystkie obiekty i materiały, aby zacząć od czystej sceny."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    # Pętla usuwająca pozostałości materiałów z pamięci Blendera
    for m in bpy.data.materials: bpy.data.materials.remove(m)


def stworz_mat_gradient(nazwa, kolor_dol, kolor_gora, metallic=1.0, emisja=2.0):
    """Proceduralne tworzenie materiału z pionowym gradientem przy użyciu nodów."""
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Tworzenie struktury grafu materiału
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_p = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_ramp = nodes.new(type='ShaderNodeValToRGB')  # Kontrola kolorów gradientu
    node_sep = nodes.new(type='ShaderNodeSeparateXYZ')  # Separacja osi Z dla wysokości
    node_tex = nodes.new(type='ShaderNodeTexCoord')  # Pobranie współrzędnych obiektu

    # Konfiguracja parametrów fizycznych (Zgodnie z wymaganiem: Metal + Roughness)
    node_p.inputs['Metallic'].default_value = metallic
    node_p.inputs['Roughness'].default_value = 0.15

    # Definicja kolorów w rampie (0 = dół, 1 = góra)
    node_ramp.color_ramp.elements[0].color = kolor_dol
    node_ramp.color_ramp.elements[1].color = kolor_gora

    # Łączenie nodów: Współrzędne -> Separacja Z -> Rampa kolorów -> BSDF
    links.new(node_tex.outputs['Generated'], node_sep.inputs['Vector'])
    links.new(node_sep.outputs['Z'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_p.inputs['Base Color'])

    # Dodanie emisji światła (efekt syntetyczny/neonowy)
    links.new(node_ramp.outputs['Color'], node_p.inputs['Emission Color'])
    node_p.inputs['Emission Strength'].default_value = emisja

    links.new(node_p.outputs['BSDF'], node_out.inputs['Surface'])
    return mat


def stworz_korzenie(liczba, x_off, mat, lodyga):
    """Generuje korzenie u podstawy rośliny z prymitywów typu Cube."""
    for i in range(liczba):
        # Rozmieszczenie kątowe (360 stopni podzielone przez liczbę korzeni)
        kat = math.radians(i * (360 / liczba))

        dist = 0.2  # Odległość od środka łodygi
        rx = x_off + math.cos(kat) * dist
        ry = math.sin(kat) * dist
        rz = 0.05

        # Tworzenie kostki (Zgodnie z wymaganiem: primitive_cube_add)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, ry, rz))
        korzen = bpy.context.object
        korzen.name = f"Korzen_{i}"

        # Transformacje: Skalowanie kostki w cienki korzeń i rotacja
        korzen.scale = (0.3, 0.08, 0.04)
        korzen.rotation_euler = (0, math.radians(15), kat)

        # Przypisanie materiału
        korzen.data.materials.append(mat)

        # Hierarchia: Ustawienie łodygi jako rodzica (Parenting)
        korzen.parent = lodyga
        korzen.matrix_parent_inverse = lodyga.matrix_world.inverted()


def stworz_rosline(wysokosc=2.0, liczba_l=5, dlugosc_l=0.8, x_off=0.0):
    """Główna funkcja parametryczna generująca biomechaniczną roślinę."""
    # Tworzenie materiałów biomechanicznych
    m_lodyga = stworz_mat_gradient("MetalLodygi", (0.02, 0.01, 0, 1), (0.3, 0.15, 0.05, 1), 1.0, 0.1)
    m_lisc = stworz_mat_gradient("NeonLisc", (0, 0.2, 0.1, 1), (0, 1, 0.8, 1), 0.8, 2.5)

    # Łodyga: Tworzenie walca i skalowanie w osi Z (Zgodnie z punktem 5 instrukcji)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=1.0, location=(x_off, 0, wysokosc / 2))
    lodyga = bpy.context.object
    lodyga.scale.z = wysokosc  # Skalowanie wysokości łodygi

    # Parametryzacja rozłożenia liści na łodydze
    start_z, end_z = wysokosc * 0.3, wysokosc * 0.9
    step = (end_z - start_z) / liczba_l

    for i in range(liczba_l):
        # Wykorzystanie złotego kąta (137.5) dla naturalnej spirali liści
        kat = math.radians(i * 137.5)
        curr_z = start_z + (i * step)

        # Liście tworzone z Cube (Zgodnie z wymaganiem: primitive_cube_add)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        lisc = bpy.context.object
        lisc.data.materials.append(m_lisc)

        # Manipulacja skalą: tworzenie płaskiego liścia
        lisc.scale = (dlugosc_l, 0.12, 0.005)

        # Obliczenie pozycji za pomocą trygonometrii (sin/cos)
        off_x = math.cos(kat) * (dlugosc_l / 2 + 0.07)
        off_y = math.sin(kat) * (dlugosc_l / 2 + 0.07)
        lisc.location = (x_off + off_x, off_y, curr_z)

        # Rotacja: pochylenie liścia względem łodygi
        lisc.rotation_euler = (0, math.radians(-20), kat)

        # Utrzymanie hierarchii obiektów
        lisc.parent = lodyga
        lisc.matrix_parent_inverse = lodyga.matrix_world.inverted()

    # Wywołanie funkcji pomocniczej dla korzeni
    stworz_korzenie(liczba=4, x_off=x_off, mat=m_lodyga, lodyga=lodyga)


def ustaw_scenerie():
    """Konfiguracja środowiska: podłoga, światła, kamera i silnik renderujący."""
    # Podłoga odbijająca światło z materiałem metalicznym
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    podloga = bpy.context.object
    mat_podloga = bpy.data.materials.new(name="Podloga")
    mat_podloga.use_nodes = True

    # Pobranie głównego noda BSDF w sposób odporny na wersję językową Blendera
    node_p = next(n for n in mat_podloga.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    node_p.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1)
    node_p.inputs['Metallic'].default_value = 1.0
    node_p.inputs['Roughness'].default_value = 0.1
    podloga.data.materials.append(mat_podloga)

    # Oświetlenie typu AREA (nad sceną)
    bpy.ops.object.light_add(type='AREA', radius=5, location=(0, 0, 8))
    area = bpy.context.object
    area.data.energy = 800

    # Oświetlenie punktowe (akcentowe/konturowe)
    bpy.ops.object.light_add(type='POINT', location=(0, 5, 3))
    rim = bpy.context.object
    rim.data.energy = 300
    rim.data.color = (1, 0, 0.5)

    # Kamera - ustawienie pozycji i kąta patrzenia
    bpy.ops.object.camera_add(location=(0, -12, 5))
    cam = bpy.context.object
    cam.rotation_euler = (math.radians(75), 0, 0)
    bpy.context.scene.camera = cam

    # Konfiguracja silnika renderującego (Eevee)
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    # Warunkowe włączenie efektu Bloom (poświata neonów) zależnie od wersji silnika
    if hasattr(bpy.context.scene.eevee, "use_bloom"):
        bpy.context.scene.eevee.use_bloom = True

    # Przełączenie aktywnego okna Blendera w tryb widoku kamery i renderowania
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.shading.type = 'RENDERED'


# --- GŁÓWNA SEKCJA WYKONAWCZA ---
czysc_scene()

# Generowanie trzech wariantów roślin obok siebie (parametryzacja)
stworz_rosline(1.8, 6, 0.7, -3.0)  # Roślina mała
stworz_rosline(3.2, 10, 1.1, 0.0)  # Roślina duża
stworz_rosline(1.4, 4, 0.6, 3.0)  # Roślina najmniejsza

# Finalne ustawienie świateł i kamery
ustaw_scenerie()