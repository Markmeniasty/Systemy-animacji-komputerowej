import bpy
import random
import os


def stworz_material_neonu(nazwa, kolor_rgb, emission_strength):
    """Tworze zaawansowany materiał neonu z barwionym rdzeniem i silną emisją."""
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')

    node_principled.inputs['Base Color'].default_value = (*kolor_rgb, 1.0)
    node_principled.inputs['Roughness'].default_value = 0.1
    node_principled.inputs['Emission Color'].default_value = (*kolor_rgb, 1.0)
    node_principled.inputs['Emission Strength'].default_value = emission_strength

    mat.node_tree.links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])
    return mat


def stworz_mokry_asfalt():
    """Tworze proceduralny materiał mokrego asfaltu z błyszczącymi kałużami za pomocą węzłów."""
    mat = bpy.data.materials.new(name="Mat_Mokry_Asfalt_Proceduralny")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    links = mat.node_tree.links
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')

    # Mokry asfalt jest ekstremalnie ciemny
    node_principled.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1.0)
    node_principled.inputs['Specular IOR Level'].default_value = 0.7  # Zwiększa intensywność odbić wody

    # GENEROWANIE KAŁUŻ (Maska chropowatości)
    node_noise_puddles = nodes.new(type='ShaderNodeTexNoise')
    node_noise_puddles.inputs['Scale'].default_value = 8.0
    node_noise_puddles.inputs['Detail'].default_value = 6.0

    node_ramp_puddles = nodes.new(type='ShaderNodeValToRGB')
    # Ostre przejścia dla kałuż (woda odbija jak lustro: Roughness = 0.0)
    node_ramp_puddles.color_ramp.elements[0].position = 0.47
    node_ramp_puddles.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    node_ramp_puddles.color_ramp.elements[1].position = 0.52
    node_ramp_puddles.color_ramp.elements[1].color = (0.5, 0.5, 0.5, 1.0)

    links.new(node_noise_puddles.outputs['Fac'], node_ramp_puddles.inputs['Fac'])
    links.new(node_ramp_puddles.outputs['Color'], node_principled.inputs['Roughness'])

    # FAKTURA ASFALTU (Ziarno)
    node_noise_grain = nodes.new(type='ShaderNodeTexNoise')
    node_noise_grain.inputs['Scale'].default_value = 200.0

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.12

    links.new(node_noise_grain.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_ramp_puddles.outputs['Color'], node_bump.inputs['Normal'])
    links.new(node_bump.outputs['Normal'], node_principled.inputs['Normal'])

    links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])
    return mat


def stworz_material(nazwa, kolor_rgb, roughness=0.5, emission=0.0):
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = (*kolor_rgb, 1.0)
        principled.inputs['Roughness'].default_value = roughness
        if emission > 0:
            principled.inputs['Emission Color'].default_value = (*kolor_rgb, 1.0)
            principled.inputs['Emission Strength'].default_value = emission
    return mat


def generuj_ulice_i_chodniki(SZEROKOSC_PASA, SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA):
    szerokosc_asfaltu = SZEROKOSC_PASA * 2

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    ulica = bpy.context.active_object
    ulica.name = "Ulica_Asfalt"
    ulica.scale = (szerokosc_asfaltu, DLUGOSC_SEKTORA, 1.0)
    ulica.data.materials.append(stworz_mokry_asfalt())
    bpy.ops.object.transform_apply(scale=True)

    mat_chodnik = stworz_material("Mat_Chodnik_Baza", (0.04, 0.04, 0.04), roughness=0.5)
    for strona in [-1, 1]:
        pos_x = strona * ((szerokosc_asfaltu / 2) + (SZEROKOSC_CHODNIKA / 2))
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pos_x, 0, 0.1))
        chodnik = bpy.context.active_object
        chodnik.name = f"Chodnik_{'Lewy' if strona == -1 else 'Prawy'}"
        chodnik.scale = (SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA, 0.2)
        chodnik.data.materials.append(mat_chodnik)
        bpy.ops.object.transform_apply(scale=True)

    # Pasy rozdzielające kierunki ruchu
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0.006))
    pas = bpy.context.active_object
    pas.name = "Pas_Rozdzielajacy"
    pas.scale = (0.15, 3.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    pas.data.materials.append(stworz_material("Mat_Pasy", (0.6, 0.6, 0.5), roughness=0.3, emission=0.2))

    mod_array = pas.modifiers.new(name="Szyk_Pasow", type='ARRAY')
    mod_array.use_relative_offset = True
    mod_array.relative_offset_displace = (0.0, 2.0, 0.0)
    mod_array.fit_type = 'FIT_LENGTH'
    mod_array.fit_length = DLUGOSC_SEKTORA
    pas.location.y = -DLUGOSC_SEKTORA / 2


def generuj_latarnie(SZEROKOSC_PASA, SZEROKOSC_CHODNIKA, DLUGOSC_SEKTORA):
    """Generuje pionowe latarnie uliczne z fizycznym światłem typu Spot rzuconym na ulicę."""
    mat_metal = stworz_material("Mat_Latarnia_Metal", (0.05, 0.05, 0.05), roughness=0.2)
    mat_zarowka = stworz_material_neonu("Mat_Latarnia_Zarowka", (1.0, 0.85, 0.6), emission_strength=5.0)

    szerokosc_asfaltu = SZEROKOSC_PASA * 2
    odstep_latarni = 25.0  # Co ile metrów stoi latarnia
    liczba_latarni = int(DLUGOSC_SEKTORA / odstep_latarni)

    for strona in [-1, 1]:
        # Latarnie stoją na skraju chodnika przy drodze
        pos_x = strona * (szerokosc_asfaltu / 2 + 0.3)

        for i in range(liczba_latarni + 1):
            pos_y = - (DLUGOSC_SEKTORA / 2) + (i * odstep_latarni)

            # 1. Słup latarni
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=6.0, location=(pos_x, pos_y, 3.2))
            slup = bpy.context.active_object
            slup.name = f"Latarnia_Slup_{'L' if strona == -1 else 'P'}_{i}"
            slup.data.materials.append(mat_metal)
            bpy.ops.object.transform_apply(scale=True)

            # 2. Poprzeczka/Klosz
            bpy.ops.mesh.primitive_cube_add(location=(pos_x - (strona * 0.4), pos_y, 6.1))
            klosz = bpy.context.active_object
            klosz.scale = (0.8, 0.3, 0.2)
            klosz.data.materials.append(mat_metal)
            bpy.ops.object.transform_apply(scale=True)

            # 3. Świecąca żarówka
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(pos_x - (strona * 0.7), pos_y, 5.95))
            zarowka = bpy.context.active_object
            zarowka.data.materials.append(mat_zarowka)

            # 4. Fizyczne źródło światła rzucające snop na asfalt
            bpy.ops.object.light_add(type='SPOT', radius=1.0, location=(pos_x - (strona * 0.7), pos_y, 5.8))
            swiatlo = bpy.context.active_object
            swiatlo.name = f"Swiatlo_Latarni_{i}"
            swiatlo.data.energy = 800.0  # latarnia sodowa/LED
            swiatlo.data.spot_size = 1.1  # Szeroki stożek światła
            swiatlo.data.spot_blend = 0.4
            swiatlo.data.color = (1.0, 0.88, 0.7)  # Ciepły odcień miejski
            swiatlo.rotation_euler = (0.0, 0.0, 0.0)  # Świeci pionowo w dół


def animuj_migotanie_neonu(material_neonu, ILOSC_KLATEK_ANIMACJI, CZESTOTLIWOSC_MIGOTANIA, MAX_MOC_NEONU):
    node_tree = material_neonu.node_tree
    principled = node_tree.nodes.get("Principled BSDF")
    if not principled: return
    wewnetrzne_id_wejscia = principled.inputs['Emission Strength']
    wewnetrzne_id_wejscia.default_value = MAX_MOC_NEONU
    wewnetrzne_id_wejscia.keyframe_insert(data_path="default_value", frame=1)

    stan_wlaczony = True
    for klatka in range(2, ILOSC_KLATEK_ANIMACJI + 1, random.randint(2, 5)):
        if random.random() < CZESTOTLIWOSC_MIGOTANIA:
            stan_wlaczony = not stan_wlaczony
            moc = random.uniform(MAX_MOC_NEONU * 0.6, MAX_MOC_NEONU) if stan_wlaczony else random.choice(
                [0.0, 0.0, 2.0])
            wewnetrzne_id_wejscia.default_value = moc
            wewnetrzne_id_wejscia.keyframe_insert(data_path="default_value", frame=klatka)


def generuj_budynki_i_neony(LICZBA_BUDYNKOW_NA_STRONE, DLUGOSC_SEKTORA, SZEROKOSC_ULICY_TOTAL, SZEROKOSC_PRZECZNICY,
                            MIN_WYSOKOSC, MAX_WYSOKOSC, ILOSC_KLATEK_ANIMACJI, CZESTOTLIWOSC_MIGOTANIA, MAX_MOC_NEONU):
    mat_budynku = stworz_material("Mat_Budynek_Baza", (0.015, 0.015, 0.02), roughness=0.8)
    krok_y = DLUGOSC_SEKTORA / LICZBA_BUDYNKOW_NA_STRONE
    kolory_neonow = [("Neon_Roz", (1.0, 0.05, 0.6)), ("Neon_Cyjan", (0.0, 0.8, 1.0)), ("Neon_Fiolet", (0.5, 0.0, 1.0)),
                     ("Neon_Zolty", (1.0, 0.6, 0.0))]

    for strona in [-1, 1]:
        for i in range(LICZBA_BUDYNKOW_NA_STRONE):
            max_glebokosc = krok_y - SZEROKOSC_PRZECZNICY
            glebokosc = random.uniform(max_glebokosc * 0.7, max_glebokosc)
            szerokosc = random.uniform(10.0, 16.0)
            wysokosc = random.uniform(MIN_WYSOKOSC, MAX_WYSOKOSC)

            pos_x = strona * ((SZEROKOSC_ULICY_TOTAL / 2) + (szerokosc / 2))
            start_slotu_y = - (DLUGOSC_SEKTORA / 2) + (i * krok_y)
            pos_y = start_slotu_y + (krok_y / 2) + random.uniform(-1.0, 1.0)
            pos_z = (wysokosc / 2) + 0.2

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pos_x, pos_y, pos_z))
            budynek = bpy.context.active_object
            budynek.name = f"Budynek_{'L' if strona == -1 else 'P'}_{i + 1}"
            budynek.scale = (szerokosc, glebokosc, wysokosc)
            budynek.data.materials.append(mat_budynku)
            bpy.ops.object.transform_apply(scale=True)

            nazwa_koloru, rgb = random.choice(kolory_neonow)
            mat_neonu = stworz_material_neonu(f"Mat_{nazwa_koloru}_{budynek.name}", rgb, MAX_MOC_NEONU)

            szer_neonu, gleb_neonu, wys_neonu = random.uniform(0.3, 0.8), 0.1, wysokosc * random.uniform(0.4, 0.8)
            neon_x = pos_x + (-strona * (szerokosc / 2 + gleb_neonu / 2))
            neon_y = pos_y + random.uniform(-glebokosc / 4, glebokosc / 4)
            neon_z = wysokosc / 2 + random.uniform(2.0, 5.0)

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(neon_x, neon_y, neon_z))
            neon = bpy.context.active_object
            neon.name = f"Neon_{budynek.name}"
            neon.scale = (gleb_neonu, szer_neonu, wys_neonu)
            neon.data.materials.append(mat_neonu)
            bpy.ops.object.transform_apply(scale=True)

            animuj_migotanie_neonu(mat_neonu, ILOSC_KLATEK_ANIMACJI, CZESTOTLIWOSC_MIGOTANIA, MAX_MOC_NEONU)


def ustaw_nocne_srodowisko_i_render():
    """Kuloodporna konfiguracja czarnej nocy i oświetlenia Eevee bez użycia Compositora."""
    import bpy

    # 1. Konfiguracja Świata (Czysta, czarna noc)
    if not bpy.context.scene.world:
        bpy.context.scene.world = bpy.data.worlds.new("Nocny_Swiat")

    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()

    node_output = nodes.new(type='ShaderNodeOutputWorld')
    node_background = nodes.new(type='ShaderNodeBackground')

    # Czarna noc, brak zewnętrznego światła słonecznego
    node_background.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    node_background.inputs['Strength'].default_value = 0.0

    world.node_tree.links.new(node_background.outputs['Background'], node_output.inputs['Surface'])

    # 2. Wybór silnika renderującego (Eevee)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'

    # 3. WŁĄCZENIE BLASKU I ODBIĆ BEZPOŚREDNIO W SILNIKU EEVEE
    if hasattr(scene, "eevee"):
        # Włączenie efektu Bloom (Blask neonów) bezpośrednio w silniku
        if hasattr(scene.eevee, "use_bloom"):
            scene.eevee.use_bloom = True

        # Włączenie Screen Space Reflections (Odbicia w mokrym asfalcie)
        if hasattr(scene.eevee, "use_ssr"):
            scene.eevee.use_ssr = True
            scene.eevee.use_ssr_refraction = True  # Zaawansowane załamania światła w wodzie

        # Włączenie Ambient Occlusion
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True

        # Włączenie Motion Blur (Smugi świateł i pędzący deszcz)
        scene.render.use_motion_blur = True

    print("-> Środowisko nocne, blask Eevee i odbicia zostały pomyślnie skonfigurowane!")