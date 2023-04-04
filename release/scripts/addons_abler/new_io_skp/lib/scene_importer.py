import math, os, tempfile, time, bpy
from mathutils import Matrix, Vector
import numpy as np
from psd_tools import PSDImage
from enum import auto
import sys
if sys.platform == "win32":
    lib = bpy.app.binary_path.split("\\")[:-1]
    lib[0] += "\\"
    lib = os.path.join(*lib, "2.96", "scripts", "addons_abler", "io_skp", "lib")
elif sys.platform == "darwin":
    lib = bpy.app.binary_path.split("/")[:-6]
    lib = "/" + os.path.join(*lib, "blender", "release", "scripts", "addons_abler", "io_skp", "lib")
else:
    lib = None

sys.path.append(lib)
from . import sketchup
from .SKPutil import *
from .skp_model_info import *
from typing import Optional
from dotenv import load_dotenv
from .constants import LAYER_SKIP_NAMES


def find_dotenv() -> Optional[str]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    last_dir = None
    while last_dir != current_dir:
        check_path = os.path.join(current_dir, ".env")
        if os.path.isfile(check_path):
            return check_path

        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir


def get_time_limit() -> int:
    env_var = os.getenv("TIME_LIMIT")
    if env_var is not None and env_var.isdigit():
        return int(env_var)
    else:
        return 1800


load_dotenv(dotenv_path=find_dotenv())
TIME_LIMIT = get_time_limit()


class ImportProgress(Enum):
    IMPORT_START = auto()
    READ_FILE = auto()
    MATERIAL = auto()
    MATERIALS_DONE = auto()
    OBJECT = auto()
    OBJECTS_DONE = auto()
    TIME_GROUP = auto()
    TIME_INSTANCE = auto()
    UPDATE_SKIP_LAYER = auto()
    UPDATE_SKIP_LAYER_DONE = auto()
    UPDATE_VIEW_LAYER = auto()
    ALWAYS_FACE_CAMERA = auto()
    ALWAYS_FACE_CAMERA_DONE = auto()
    APPLY_TOON_STYLE = auto()


class SceneImporter:
    def __init__(self):
        self.filepath = "/tmp/untitled.skp"
        self.name_mapping = {}
        self.component_meshes = {}
        self.scene = None
        self.layers_skip = []
        self.source_obj = []
        self.start_time = None
        self.always_face_camera_instances = []

        # scene.collection.children 에 바로 object 혹은 collection 을 추가했을 때 매우 느린 이슈가 있어서
        # scene.collection.children 바깥에 있는 collection 에다가 모아서 나중에 한꺼번에 scene 에 등록함으로서 속도 개선
        self.object_collection = self.create_or_get_collection("Objects")
        self.layer_collection = self.create_or_get_collection("Layers")

        self.imported_object = None
        for scene in bpy.data.scenes:
            scene_cols = scene.collection.children
            if "Layers" in scene_cols:
                scene_cols.unlink(self.layer_collection)
            if "Objects" in scene_cols:
                scene_cols.unlink(self.object_collection)

    def set_filename(self, filename):
        self.filepath = filename
        self.basepath, self.skp_filename = os.path.split(self.filepath)
        return self  # allow chaining

    def init_load_setting(self, context, **options):
        self.context = context
        self.reuse_material = options["reuse_material"]
        self.reuse_group = options["reuse_existing_groups"]
        self.max_instance = options["max_instance"]
        self.import_lookatme = options["import_lookatme"]
        # self.render_engine = options['render_engine']
        self.mesh_data_dict = defaultdict(list)
        self.component_skip = proxy_dict()
        self.component_depth = proxy_dict()
        self.group_written = {}
        ren_res_x = context.scene.render.resolution_x
        ren_res_y = context.scene.render.resolution_y
        self.aspect_ratio = ren_res_x / ren_res_y

        skp_log(f"Importing: {self.filepath}")
        addon_name = __name__.split(".")[0]
        self.prefs = context.preferences.addons[addon_name].preferences

        try:
            self.skp_model = sketchup.Model.from_file(self.filepath)

            # Get SketchUp model info
            _t1 = time.time()
            self.statistics = GetModelInfo(self.skp_model).return_model_statistics()
            skp_log(f"Get model info in {(time.time() - _t1):.4f} sec.")
        except Exception as e:
            skp_log(f"Error reading input file: {self.filepath}")
            skp_log(e)
            return {"FINISHED"}

    def add_layers(self, context, **options):
        lst_layer_off = []

        if options["import_scene"]:
            for s in self.skp_model.scenes:
                if s.name == options["import_scene"]:
                    skp_log(f"Importing Scene '{s.name}'")
                    self.scene = s
                    self.layers_skip = list(s.layers)
                    for l in s.layers:
                        skp_log(f"SKIP: {l.name}")
            if not self.layers_skip:
                skp_log(
                    f'Could not find scene: {options["import_scene"]}, importing default.'
                )

        # invisible layers excluded
        for l in self.skp_model.layers:
            if l.name in LAYER_SKIP_NAMES:
                continue

            if l.name not in bpy.data.collections:
                new_coll = bpy.data.collections.new(l.name)
                self.layer_collection.children.link(new_coll)
                for scene in bpy.data.scenes:
                    added_l_exclude = scene.l_exclude.add()
                    added_l_exclude.name = l.name
            if not l.visible:
                lst_layer_off.append(l.name)

        skp_log("Added Layers ... ")

        for l in sorted([l.name for l in self.layers_skip]):
            skp_log(l)

        return lst_layer_off

    def elapsed(self):
        return time.time() - self.start_time

    def load(self, context, **options):
        """load a sketchup file"""
        yield ImportProgress.IMPORT_START, None
        # Initialize slapi
        sketchup.initialize_slapi()
        # Initialize load settings
        self.start_time = time.time()
        self.init_load_setting(context, **options)
        yield ImportProgress.READ_FILE, self.statistics, self.import_lookatme

        # Analyze layers and add to scene
        lst_layer_off = self.add_layers(context, **options)

        # Parse component definition into dictionary
        self.skp_components = proxy_dict(self.skp_model.component_definition_as_dict)
        skp_log(f"Parsed in {self.elapsed():.4f} sec.")

        # Material import
        yield from self.write_materials(self.skp_model.materials)

        yield ImportProgress.MATERIALS_DONE, None
        skp_log(f"Materials imported in {self.elapsed():.4f} sec.")

        # Component depth analysis
        D = SKP_util()
        SKP_util.layers_skip = self.layers_skip
        for c in self.skp_model.component_definitions:
            self.component_depth[c.name] = D.component_deps(c.entities)
        skp_log(f"Component depths analyzed in {self.elapsed():.4f} sec.")
        # Write entities
        yield from self.write_entities(
            self.skp_model.entities,
            "Sketchup",
            Matrix.Identity(4),
        )
        skp_log(f"Entities written in {self.elapsed():.4f} sec.")

        # 동적 컴포넌트 처리가 없어 write_entities()와 Model Info의 group, instance 개수 차이가 발생함
        # 그래서 write_entities 과정이 끝나면 Model Info의 group, instance 개수로 업데이트 해서 progress 완료로 처리
        yield ImportProgress.OBJECTS_DONE, True

        # Update Layer state
        for i in lst_layer_off:
            for scene in bpy.data.scenes:
                scene.l_exclude[i].value = False
                yield ImportProgress.UPDATE_SKIP_LAYER, None
        yield ImportProgress.UPDATE_SKIP_LAYER_DONE, None
        skp_log(f"Layer updated in {self.elapsed():.4f} sec.")

        for scene in bpy.data.scenes:
            scene.collection.children.link(self.object_collection)
            scene.collection.children.link(self.layer_collection)

        skp_log(f"View layer updated in {self.elapsed():.4f} sec.")
        yield ImportProgress.UPDATE_VIEW_LAYER, None

        # write_entities가 끝나고 always face camera가 적용된 인스턴스는 look at me로 적용
        for instance_name in self.always_face_camera_instances:
            if instance_name in bpy.data.objects:
                bpy.data.objects[
                    instance_name
                ].ACON_prop.constraint_to_camera_rotation_z = True
            yield ImportProgress.ALWAYS_FACE_CAMERA, None
        yield ImportProgress.ALWAYS_FACE_CAMERA_DONE, None

        bpy.ops.object.select_all(action="DESELECT")
        skp_log(
            f"Always face camera imported in {(time.time() - self.start_time):.4f} sec."
        )

        # Exclude "Groups" Collection
        # context.view_layer.layer_collection.children["Groups"].exclude = True

        # Set file compression
        bpy.context.preferences.filepaths.use_file_compression = True

        # Minimize collection tabs
        for layer in self.layer_collection.children:
            self.minimize_collection(layer)
        skp_log(f"Collection minimized in {self.elapsed():.4f} sec.")

        # Apply Abler's toon style material
        bpy.ops.acon3d.apply_toon_style("INVOKE_DEFAULT")
        skp_log(f"Toon-style applied in {self.elapsed():.4f} sec.")
        yield ImportProgress.APPLY_TOON_STYLE, None

        # create list of scenes from skp model
        scenes_list = list(self.skp_model.scenes)

        # using for loop, return camera object from write_camera() and create scene with that camera object
        for i in range(len(scenes_list)):
            cam = self.write_camera(scenes_list[i].camera)
            new_scene = bpy.context.scene.copy()
            new_scene.name = scenes_list[i].name
            new_scene.camera = cam

        # Terminate slapi
        sketchup.terminate_slapi()

        # refresh scene_col using already created function
        self.add_scene_items_to_collection()

        # Finished
        skp_log(f"Finished importing in {self.elapsed():.4f} sec.")


    # copied from scenes.py
    def add_scene_items_to_collection(self):
        """scene_col에 bpy.data.scenes 항목 넣어주기"""

        prop = bpy.context.window_manager.ACON_prop
        prop.scene_col.clear()
        for i, scene in enumerate(bpy.data.scenes):
            # 파일 열기 시 씬 이름들을 Scene UI에 넣는 과정에서 change_scene_name이 실행이 됨
            # 실제 이름을 바꾸는 과정이 아니므로 is_scene_renamed를 설정
            # 각 씬마다 change_scene_name 함수에 들어갔다 나오므로 for문 안에서 설정
            global is_scene_renamed
            is_scene_renamed = False

            new_scene = prop.scene_col.add()
            new_scene.name = scene.name
            new_scene.index = i

        # 현재 씬과 scene_col 맞추기
        scene = bpy.context.scene
        scene_col_list = [*prop.scene_col]

        for item in scene_col_list:
            if item.name == scene.name:
                index = item.index
        prop.active_scene_index = index

    def minimize_collection(self, cocol):
        outliners = [a for a in bpy.context.screen.areas if a.type == "OUTLINER"]
        c = bpy.context.copy()
        c["collection"] = cocol
        for ol in outliners:
            c["area"] = ol

            bpy.ops.outliner.show_one_level(c, open=False)
            ol.tag_redraw()

    def write_materials(self, materials):
        if self.context.scene.render.engine != "BLENDER_EEVEE":
            self.context.scene.render.engine = "BLENDER_EEVEE"

        self.materials = {}
        self.materials_scales = {}

        bmat = None
        if "Material" in bpy.data.materials:
            bmat = bpy.data.materials["Material"]
            bmat_node = bmat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
            bmat_node.inputs["Color"].default_value = (0.8, 0.8, 0.8, 0)
        else:
            bmat = bpy.data.materials.new("Material")
            bmat.diffuse_color = (0.8, 0.8, 0.8, 0)
            bmat.use_nodes = True

        if bmat is not None:
            self.materials["Material"] = bmat

        for mat in materials:

            name = mat.name

            if mat.texture:
                self.materials_scales[name] = mat.texture.dimensions[2:]
            else:
                self.materials_scales[name] = (1.0, 1.0)

            if self.reuse_material:
                if mat.opacity < 1.0 and not name.startswith("ACON_mat_clear"):
                    name = "ACON_mat_clear " + name
                bmat = bpy.data.materials.new(name)
                r, g, b, a = mat.color
                tex = mat.texture
                bmat.diffuse_color = (
                    math.pow((r / 255.0), 2.2),
                    math.pow((g / 255.0), 2.2),
                    math.pow((b / 255.0), 2.2),
                    round((a / 255.0), 2),
                )  # sRGB to Linear

                if round((a / 255.0), 2) < 1:
                    bmat.blend_method = "BLEND"

                bmat.use_nodes = True
                default_shader = bmat.node_tree.nodes["Principled BSDF"]

                default_shader_base_color = default_shader.inputs["Base Color"]
                default_shader_base_color.default_value = bmat.diffuse_color

                default_shader_alpha = default_shader.inputs["Alpha"]
                default_shader_alpha.default_value = round((a / 255.0), 2)

                if name.startswith("ACON_mat_clear"):
                    bmat.shadow_method = "NONE"

                if tex:
                    tex_name = tex.name.split("\\")[-1]
                    tmp_name = os.path.join(tempfile.gettempdir(), tex_name)
                    tex.write(tmp_name)
                    if tmp_name.endswith(".psd"):
                        psd = PSDImage.open(f"{tmp_name}")
                        tmp_name = tmp_name.replace(".psd", ".png")
                        psd.composite().save("{}".format(tmp_name))
                    img = bpy.data.images.load(tmp_name)
                    img.pack()
                    os.remove(tmp_name)

                    tex_node = bmat.node_tree.nodes.new("ShaderNodeTexImage")
                    tex_node.image = img
                    tex_node.location = Vector((-750, 225))
                    bmat.node_tree.links.new(
                        tex_node.outputs["Color"], default_shader_base_color
                    )
                self.materials[name] = bmat
                yield ImportProgress.MATERIAL, None
            else:
                self.materials[name] = bpy.data.materials[name]

    def write_mesh_data(self, entities=None, name="", default_material="Material"):
        """
        writes mesh data to the scene
        """
        mesh_key = (name, default_material)
        # return mesh info if mesh already written
        if mesh_key in self.component_meshes:
            return self.component_meshes[mesh_key]
        alpha = False
        uvs_used = False

        (co, loops_vert_idx, mat_index, smooth, uv_list, mats) = entities.get_mesh_data(
            self.materials_scales, default_material
        )

        if not co:
            return None, False

        me = bpy.data.meshes.new(name)

        if len(mats) >= 1:
            mats_sorted = OrderedDict(sorted(mats.items(), key=lambda x: x[1]))
            for k in mats_sorted.keys():
                try:
                    bmat = self.materials[k]
                except KeyError as _e:
                    try:
                        bmat = self.materials["ACON_mat_clear " + k]
                    except KeyError as _e:
                        bmat = self.materials["Material"]
                me.materials.append(bmat)
                try:
                    for node in bmat.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            uvs_used = True
                            break
                except AttributeError as _e:
                    uvs_used = False
        else:
            skp_log(f"WARNING: Object {name} has no material!")

        tri_faces = list(zip(*[iter(loops_vert_idx)] * 3))
        tri_face_count = len(tri_faces)

        loop_start = []
        i = 0
        for f in tri_faces:
            loop_start.append(i)
            i += len(f)

        loop_total = list(map(lambda f: len(f), tri_faces))

        me.vertices.add(len(co) / 3)
        me.vertices.foreach_set("co", co)

        me.loops.add(len(loops_vert_idx))
        me.loops.foreach_set("vertex_index", loops_vert_idx)

        me.polygons.add(tri_face_count)
        me.polygons.foreach_set("loop_start", loop_start)
        me.polygons.foreach_set("loop_total", loop_total)
        me.polygons.foreach_set("material_index", mat_index)
        me.polygons.foreach_set("use_smooth", smooth)

        if uvs_used:
            k, l = 0, 0
            me.uv_layers.new()
            for i in range(len(tri_faces)):
                for j in range(3):
                    uv_cordinates = (uv_list[i][l], uv_list[i][l + 1])
                    me.uv_layers[0].data[k].uv = Vector(uv_cordinates)
                    k += 1
                    if j != 2:
                        l += 2
                    else:
                        l = 0

        me.update(calc_edges=True)
        me.validate()
        self.component_meshes[mesh_key] = me, alpha

        return me, alpha

    def write_entities(
        self,
        entities,
        name,
        transform: Matrix,
        default_material="Material",
        etype=None,
        layer_name: Optional[str] = None,
        parent_object=None,
    ):
        def set_parent_obj(prt, child):
            if prt is not None:
                child.parent_type = "OBJECT"
                child.parent = prt

        elapsed_time_mesh = time.time()

        # time check : converting time over 1 hour(3600s) -> blender quit
        if time.time() - self.start_time > TIME_LIMIT:
            exit()
            bpy.ops.wm.quit_blender()
        if (
            etype == EntityType.component
            and (name, default_material) in self.component_skip
        ):
            return

        # mesh
        me, alpha = self.write_mesh_data(
            entities=entities, name=name, default_material=default_material
        )
        if me:
            new_ob = bpy.data.objects.new(name, me)
            if 0.01 < alpha < 1.0:
                new_ob.show_transparent = True
        else:
            new_ob = bpy.data.objects.new(name, None)
        self.object_collection.objects.link(new_ob)
        if self.imported_object is None:
            self.imported_object = new_ob

        if layer_name:
            bpy.data.collections[layer_name].objects.link(new_ob)

        # shear transform
        is_shear = not transform.to_3x3().is_orthogonal_axis_vectors
        if is_shear:
            mid_ob = bpy.data.objects.new(f"{name}_decomposed", None)
            self.object_collection.objects.link(mid_ob)

            mat_parent, mat_self = decompose_shear(transform)
            mid_ob.matrix_local = mat_parent
            new_ob.matrix_local = mat_self
            set_parent_obj(mid_ob, new_ob)
            set_parent_obj(parent_object, mid_ob)
        else:
            new_ob.matrix_local = transform
            set_parent_obj(parent_object, new_ob)

        elapsed_time_mesh = time.time() - elapsed_time_mesh
        elapsed_time_group = 0
        elapsed_time_instance = 0

        # 최상위 오브젝트에 대해서 statistics.objects에 카운트하지 않음
        if parent_object is not None:
            yield ImportProgress.OBJECT, None

        for group in entities.groups:
            _tg = time.time()

            if group.hidden:
                continue
            if self.layers_skip and group.layer in self.layers_skip:
                continue

            group_name = group.name + group.guid
            if not group_name:
                group_name = group.guid

            cur_layer_name = None
            if group.layer.name not in LAYER_SKIP_NAMES:
                cur_layer_name = group.layer.name

            elapsed_time_group += time.time() - _tg
            yield from self.write_entities(
                group.entities,
                f"G-{group_name}",
                Matrix(group.transform),
                default_material=inherent_default_mat(group.material, default_material),
                etype=EntityType.group,
                layer_name=cur_layer_name,
                parent_object=new_ob,
            )

        for instance in entities.instances:
            _ti = time.time()

            if instance.hidden:
                continue
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            mat_name = inherent_default_mat(instance.material, default_material)
            instance_name = f"I-{instance.guid}"

            cdef = self.skp_components[instance.definition.name]

            if self.import_lookatme and cdef.alwaysFaceCamera:
                self.always_face_camera_instances.append(instance_name)

            cur_layer_name = None
            if instance.layer.name not in LAYER_SKIP_NAMES:
                cur_layer_name = instance.layer.name

            elapsed_time_instance += time.time() - _ti
            yield from self.write_entities(
                cdef.entities,
                instance_name,
                Matrix(instance.transform),
                default_material=mat_name,
                etype=EntityType.component,
                layer_name=cur_layer_name,
                parent_object=new_ob,
            )

        elapsed_time = elapsed_time_mesh + elapsed_time_group + elapsed_time_instance
        if etype == EntityType.group:
            yield ImportProgress.TIME_GROUP, elapsed_time
        elif etype == EntityType.component:
            yield ImportProgress.TIME_INSTANCE, elapsed_time

    def create_or_get_collection(self, name: str):
        return (
            bpy.data.collections.new(name)
            if name not in bpy.data.collections.keys()
            else bpy.data.collections[name]
        )

    def write_camera(self, camera, name="Active Camera"):

        pos, target, up = camera.GetOrientation()
        bpy.ops.object.add(type="CAMERA", location=pos)
        ob = self.context.object
        ob.name = name

        z = Vector(pos) - Vector(target)
        x = Vector(up).cross(z)
        y = z.cross(x)

        x.normalize()
        y.normalize()
        z.normalize()

        ob.matrix_world.col[0] = x.resized(4)
        ob.matrix_world.col[1] = y.resized(4)
        ob.matrix_world.col[2] = z.resized(4)

        cam = ob.data
        aspect_ratio = camera.aspect_ratio
        fov = camera.fov
        if not aspect_ratio:
            # skp_log(f"Camera:'{name}' uses dynamic/screen aspect ratio.")
            aspect_ratio = self.aspect_ratio
        if not fov:
            skp_log(f"Camera:'{name}'' is in Orthographic Mode.")
            cam.type = "ORTHO"
        else:
            cam.angle = (math.pi * fov / 180) * aspect_ratio
        cam.clip_end = self.prefs.camera_far_plane
        cam.name = name

        # add camera to designated collection (create one if not exists)
        # collection = bpy.data.collections.get("ACON_col_cameras")
        # if not collection:
        #     collection = bpy.data.collections.new("ACON_col_cameras")
        #     for scene in bpy.data.scenes:
        #         scene.collection.children.link(collection)
        # collection.objects.link(ob)
        # if (
        #     "Collection" in bpy.data.collections.keys()
        #     and ob.name in bpy.data.collections.get("Collection").objects.keys()
        # ):
        #     bpy.data.collections.get("Collection").objects.unlink(ob)

        #return camera object
        return ob


def decompose_shear(mat):
    # https://math.stackexchange.com/questions/109108/is-it-true-that-any-matrix-can-be-decomposed-into-product-of-rotation-reflection
    u, s, v = np.linalg.svd(mat.to_3x3())
    mat_u = Matrix(u)
    mat_s = Matrix([[s[0], 0, 0], [0, s[1], 0], [0, 0, s[2]]])
    mat_v = Matrix(v)
    mat_trans = Matrix.Translation(mat.to_translation())
    mat_prt = mat_trans @ (mat_u @ mat_s).to_4x4()
    mat_chld = mat_v.to_4x4()
    return mat_prt, mat_chld
