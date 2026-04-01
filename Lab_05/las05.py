import bpy
import bmesh
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ==============================================================================
# [ZADANIE 4.1] KONFIGURACJA GATUNKÓW I BIOMU (SŁOWNIK PARAMETRÓW)
# ==============================================================================

@dataclass
class SpeciesConfig:
    name: str
    mesh_type: str
    height_range: Tuple[float, float]
    radius: float
    trunk_color: Tuple[float, float, float, float]
    detail_color: Tuple[float, float, float, float]

# Baza danych gatunków (Słownik parametrów na poziomie modułu)
SPECIES_BOOK = {
    "DEB": SpeciesConfig("Deb", "TREE", (3.0, 5.0), 0.8, (0.1, 0.05, 0.01, 1), (0.05, 0.2, 0.05, 1)),
    "KRZAK": SpeciesConfig("Krzew", "BUSH", (0.8, 1.5), 0.5, (0.15, 0.1, 0.05, 1), (0.1, 0.4, 0.1, 1)),
    "KWIAT": SpeciesConfig("Kwiat", "FLOWER", (0.3, 0.6), 0.2, (0.02, 0.3, 0.02, 1), (1.0, 0.1, 0.5, 1)),
    "GRZYB": SpeciesConfig("Grzyb", "MUSHROOM", (0.1, 0.25), 0.15, (0.8, 0.7, 0.6, 1), (0.4, 0.1, 0.05, 1)),
    "BIOMECH": SpeciesConfig("Biomech", "CUSTOM", (0.8, 1.4), 0.4, (0,0,0,0), (0,0,0,0))
}

# Konfiguracja stref biomu (Logika radialna dla ZADANIA 4.3)
BIOME_SETTINGS = {
    "center_radius_percent": 0.50, # 35% środka to duże drzewa/biomech
    "mid_radius_percent": 0.85,    # do 70% to krzewy i biomech
    # reszta to krawędź (kwiaty/grzyby)
    
    "zones": {
        "center": ["DEB", "BIOMECH"],
        "mid": ["KRZAK", "BIOMECH", "KWIAT"],
        "edge": ["KWIAT", "GRZYB"]
    }
}

# ==============================================================================
# [ZADANIE 4.4] MANAGER ZASOBÓW (CZYSZCZENIE SCENY I MATERIAŁY)
# ==============================================================================

class ResourceManager:
    @staticmethod
    def clean_scene():
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        for m in bpy.data.materials: bpy.data.materials.remove(m)
        if "Las_System" in bpy.data.collections:
            col = bpy.data.collections["Las_System"]
            for obj in col.objects: bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)

    @staticmethod
    def create_mat(name: str, color: Tuple[float, float, float, float], rough: float = 0.8):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not bsdf: bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = rough
        return mat

    @staticmethod
    def stworz_mat_gradient(nazwa, kolor_dol, kolor_gora, metallic=1.0, emisja=2.0):
        mat = bpy.data.materials.new(name=nazwa)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_p = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_ramp = nodes.new(type='ShaderNodeValToRGB')
        node_sep = nodes.new(type='ShaderNodeSeparateXYZ')
        node_tex = nodes.new(type='ShaderNodeTexCoord')
        node_p.inputs['Metallic'].default_value = metallic
        node_p.inputs['Roughness'].default_value = 0.15
        node_ramp.color_ramp.elements[0].color = kolor_dol
        node_ramp.color_ramp.elements[1].color = kolor_gora
        links.new(node_tex.outputs['Generated'], node_sep.inputs['Vector'])
        links.new(node_sep.outputs['Z'], node_ramp.inputs['Fac'])
        links.new(node_ramp.outputs['Color'], node_p.inputs['Base Color'])
        links.new(node_ramp.outputs['Color'], node_p.inputs['Emission Color'])
        node_p.inputs['Emission Strength'].default_value = emisja
        links.new(node_p.outputs['BSDF'], node_out.inputs['Surface'])
        return mat

# ==============================================================================
# [ZADANIE 4.2] FABRYKA GEOMETRII (GENEROWANIE OBIEKTÓW I SKALOWANIE)
# ==============================================================================

class GeometryFactory:
    @staticmethod
    def build_tree(config, loc, col, scale_multiplier):
        # Skalujemy bazową wysokość i promień korony (Zgodnie z wymaganiem "Dla chętnych")
        h = random.uniform(*config.height_range) * scale_multiplier
        r = config.radius * scale_multiplier
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12 * scale_multiplier, depth=h, location=(loc[0], loc[1], h/2))
        trunk = bpy.context.object
        trunk.data.materials.append(ResourceManager.create_mat("TrunkMat", config.trunk_color))
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(loc[0], loc[1], h))
        crown = bpy.context.object
        crown.scale.z = 1.3
        crown.data.materials.append(ResourceManager.create_mat("LeafMat", config.detail_color))
        crown.parent = trunk
        crown.matrix_parent_inverse = trunk.matrix_world.inverted()
        col.objects.link(trunk); col.objects.link(crown)

    @staticmethod
    def build_custom_biomech(config, loc, col, scale_multiplier):
        """Twoja roślina zintegrowana ze skalowaniem biomu (ZADANIE 4.2)."""
        # Skalujemy bazowe parametry
        h = random.uniform(*config.height_range) * scale_multiplier
        x, y = loc[0], loc[1]
        l_lisci = 5
        # Skalujemy długość liścia i promień łodygi
        dlugosc_l = 0.6 * scale_multiplier
        r_lodygi = 0.07 * scale_multiplier
        
        m_lodyga = ResourceManager.stworz_mat_gradient("MetalLodygi", (0.02, 0.01, 0, 1), (0.3, 0.15, 0.05, 1), 1.0, 0.1)
        m_lisc = ResourceManager.stworz_mat_gradient("NeonLisc", (0, 0.2, 0.1, 1), (0, 1, 0.8, 1), 0.8, 2.5)

        # Łodyga
        bpy.ops.mesh.primitive_cylinder_add(radius=r_lodygi, depth=h, location=(x, y, h/2))
        lodyga = bpy.context.object
        lodyga.data.materials.append(m_lodyga)
        col.objects.link(lodyga)

        # Liście
        start_z, end_z = h * 0.3, h * 0.9
        step = (end_z - start_z) / l_lisci
        for i in range(l_lisci):
            kat = math.radians(i * 137.5)
            curr_z = start_z + (i * step)
            bpy.ops.mesh.primitive_cube_add(size=1.0)
            lisc = bpy.context.object
            lisc.data.materials.append(m_lisc)
            # Skalujemy grubość liścia proporcjonalnie
            lisc.scale = (dlugosc_l, 0.12 * scale_multiplier, 0.005)
            off_x = math.cos(kat) * (dlugosc_l / 2 + r_lodygi)
            off_y = math.sin(kat) * (dlugosc_l / 2 + r_lodygi)
            lisc.location = (x + off_x, y + off_y, curr_z)
            lisc.rotation_euler = (0, math.radians(-20), kat)
            lisc.parent = lodyga
            lisc.matrix_parent_inverse = lodyga.matrix_world.inverted()
            col.objects.link(lisc)

        # Korzenie (Skalujemy dystans i rozmiar)
        for i in range(4):
            kat_k = math.radians(i * 90)
            dist = 0.2 * scale_multiplier
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x + math.cos(kat_k)*dist, y + math.sin(kat_k)*dist, 0.05 * scale_multiplier))
            korzen = bpy.context.object
            korzen.scale = (0.3 * scale_multiplier, 0.08 * scale_multiplier, 0.04 * scale_multiplier)
            korzen.rotation_euler = (0, math.radians(15), kat_k)
            korzen.data.materials.append(m_lodyga)
            korzen.parent = lodyga
            korzen.matrix_parent_inverse = lodyga.matrix_world.inverted()
            col.objects.link(korzen)

    @staticmethod
    def build_mushroom(config, loc, col, scale_multiplier):
        # Grzyby skalujemy mniej agresywnie, żeby nie zniknęły
        s_m = math.sqrt(scale_multiplier) 
        h = random.uniform(*config.height_range) * s_m
        r = config.radius * s_m
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04 * s_m, depth=h, location=(loc[0], loc[1], h/2))
        stem = bpy.context.object
        stem.data.materials.append(ResourceManager.create_mat("StemMat", config.trunk_color))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(loc[0], loc[1], h))
        cap = bpy.context.object
        cap.scale = (1, 1, 0.3)
        cap.data.materials.append(ResourceManager.create_mat("CapMat", config.detail_color))
        cap.parent = stem
        cap.matrix_parent_inverse = stem.matrix_world.inverted()
        col.objects.link(stem); col.objects.link(cap)

    @staticmethod
    def build_flower(config, loc, col, scale_multiplier):
        s_m = math.sqrt(scale_multiplier)
        h = random.uniform(*config.height_range) * s_m
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015 * s_m, depth=h, location=(loc[0], loc[1], h/2))
        stem = bpy.context.object
        stem.data.materials.append(ResourceManager.create_mat("FlowerStem", config.trunk_color))
        bpy.ops.mesh.primitive_ico_sphere_add(radius=config.radius * s_m, subdivisions=1, location=(loc[0], loc[1], h))
        head = bpy.context.object
        head.data.materials.append(ResourceManager.create_mat("FlowerHead", config.detail_color))
        head.parent = stem
        head.matrix_parent_inverse = stem.matrix_world.inverted()
        col.objects.link(stem); col.objects.link(head)

    @staticmethod
    def build_bush(config, loc, col, scale_multiplier):
        h = random.uniform(*config.height_range) * scale_multiplier
        r = config.radius * scale_multiplier
        bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2, location=(loc[0], loc[1], h/3))
        bush = bpy.context.object
        bush.scale = (1, 1, h/r)
        bush.data.materials.append(ResourceManager.create_mat("BushMat", config.detail_color))
        col.objects.link(bush)

# ==============================================================================
# [ZADANIE 4.3 i 4.4] SILNIK ORKIESTRACJI (GENEROWANIE LASU I BIOMY)
# ==============================================================================

class ForestOrchestrator:
    def __init__(self, plate_size: float, target_count: int):
        self.size = plate_size
        self.target = target_count
        self.points = []
        # Maksymalny możliwy promień na płycie (do rogu)
        self.max_influence_radius = (plate_size / 2) * math.sqrt(2)

    def wybierz_gatunek_i_skale(self, x, y) -> Tuple[SpeciesConfig, float]:
        """[ZADANIE 4.3] Oblicza strefę i mnożnik skali na podstawie pozycji."""
        distance = math.sqrt(x**2 + y**2)
        # Normalizujemy dystans (0 w środku, ~1 na krawędzi płyty)
        normalized_dist = distance / (self.size / 2)
        
        # Określenie strefy i wybór puli gatunków (Logika biomów)
        if normalized_dist <= BIOME_SETTINGS["center_radius_percent"]:
            pool = BIOME_SETTINGS["zones"]["center"]
        elif normalized_dist <= BIOME_SETTINGS["mid_radius_percent"]:
            pool = BIOME_SETTINGS["zones"]["mid"]
        else:
            pool = BIOME_SETTINGS["zones"]["edge"]
            
        spec_key = random.choice(pool)
        spec = SPECIES_BOOK[spec_key]
        
        # Obliczenie mnożnika skali (ZADANIE 6 - Dla chętnych)
        scale_mult = 1.0 - (normalized_dist * 0.3) 
        scale_mult = max(0.2, scale_mult) 
        
        return spec, scale_mult

    def spawn_forest(self):
        """[ZADANIE 4.4] Pętla generowania i linkowanie do kolekcji."""
        ResourceManager.clean_scene()
        # Tworzenie nazwanej kolekcji "Las_System" (Zgodnie z wymaganiami punktu 4.4)
        root_col = bpy.data.collections.new("Las_System")
        bpy.context.scene.collection.children.link(root_col)

        bpy.ops.mesh.primitive_plane_add(size=self.size, location=(0,0,0))
        ground = bpy.context.object
        ground.data.materials.append(ResourceManager.create_mat("GroundMat", (0.005, 0.01, 0.005, 1), 0.9))

        count = 0
        attempts = 0
        while count < self.target and attempts < 2000:
            attempts += 1
            x = random.uniform(-self.size/2 + 0.5, self.size/2 - 0.5)
            y = random.uniform(-self.size/2 + 0.5, self.size/2 - 0.5)
            
            spec, scale_multiplier = self.wybierz_gatunek_i_skale(x, y)
            current_radius = spec.radius * scale_multiplier

            # Sprawdzanie kolizji
            if all(math.sqrt((x-px)**2 + (y-py)**2) > (current_radius + pr) * 0.85 for px, py, pr in self.points):
                self.points.append((x, y, current_radius))
                
                # Budowanie konkretnego typu (ZADANIE 4.2)
                if spec.mesh_type == 'TREE': GeometryFactory.build_tree(spec, (x,y,0), root_col, scale_multiplier)
                elif spec.mesh_type == 'BUSH': GeometryFactory.build_bush(spec, (x,y,0), root_col, scale_multiplier)
                elif spec.mesh_type == 'FLOWER': GeometryFactory.build_flower(spec, (x,y,0), root_col, scale_multiplier)
                elif spec.mesh_type == 'MUSHROOM': GeometryFactory.build_mushroom(spec, (x,y,0), root_col, scale_multiplier)
                elif spec.mesh_type == 'CUSTOM': GeometryFactory.build_custom_biomech(spec, (x,y,0), root_col, scale_multiplier)
                
                # Porządkowanie obiektów w Outlinerze
                for obj in bpy.context.scene.collection.objects:
                    if obj.name not in ["Plane", "Ground"] and obj.parent is None:
                        if obj.name not in root_col.objects:
                            try: bpy.context.scene.collection.objects.unlink(obj)
                            except: pass
                count += 1
        self._finalize()

# ==============================================================================
# [ZADANIE 4.4] FINALIZACJA SCENY (KAMERA, ŚWIATŁO, RENDER)
# ==============================================================================

    def _finalize(self):
        # 1. Czyszczenie starych świateł i kamer
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.type in ['LIGHT', 'CAMERA']:
                obj.select_set(True)
        bpy.ops.object.delete()

        # 2. Ustawienie Kamery
        cam_x, cam_y, cam_z = self.size * 1.1, -self.size * 1.1, self.size * 0.9
        bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
        cam = bpy.context.object
        target = bpy.data.objects.new("CamTarget", None)
        bpy.context.scene.collection.objects.link(target)
        constraint = cam.constraints.new(type='TRACK_TO')
        constraint.target = target
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        bpy.context.scene.camera = cam

        # 3. Światło (SUN / AREA)
        bpy.ops.object.light_add(type='AREA', location=(-15, 15, 20))
        area_light = bpy.context.object
        area_light.data.energy = 5000  
        area_light.data.size = 50      
        area_light.data.color = (0.8, 0.9, 1.0)

        # 4. Podłoże (Czarne szkło)
        ground = bpy.data.objects.get("Plane")
        if ground:
            mat = bpy.data.materials.new(name="DeepBlack")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
            bsdf.inputs['Roughness'].default_value = 0.1
            bsdf.inputs['Metallic'].default_value = 0.5
            ground.data.materials.clear()
            ground.data.materials.append(mat)

        # 5. Konfiguracja Silnika Renderującego (Eevee Bloom)
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        if hasattr(bpy.context.scene.eevee, "use_bloom"):
            bpy.context.scene.eevee.use_bloom = True 
            bpy.context.scene.eevee.use_ssr = True

# ==============================================================================
# URUCHOMIENIE GENERATORA
# ==============================================================================
orchestrator = ForestOrchestrator(plate_size=30.0, target_count=400)
orchestrator.spawn_forest()