from dataclasses import dataclass

from .constants import LAYER_SKIP_NAMES
from .skp_log import skp_log


@dataclass
class SUModelStatistics:
    edges: int = 0
    faces: int = 0
    instances: int = 0
    groups: int = 0
    component_defs: int = 0
    materials: int = 0
    # afc = always face camera
    afc_instances: int = 0
    hidden_layer_count: int = 0


class GetModelInfo:
    def __init__(self, skp_model):
        self.SUModel = skp_model
        self.statistics = SUModelStatistics()

    def get_model_statistics(self, model):
        self.statistics.component_defs = model.NumComponentDefinitions()
        self.statistics.materials = model.NumMaterials()

        # invisible layers excluded
        for layer in model.layers:
            if layer.name in LAYER_SKIP_NAMES:
                continue
            if not layer.visible:
                self.statistics.hidden_layer_count += 1

    def get_entities_statistics(self, entities):
        self.statistics.edges += entities.NumEdges()
        self.statistics.faces += entities.NumFaces()
        self.statistics.instances += entities.NumInstances()
        self.statistics.groups += entities.NumGroups()

        for group in entities.groups:
            self.get_entities_statistics(group.entities)

        for instance in entities.instances:
            component_def = instance.definition
            if component_def.alwaysFaceCamera:
                self.statistics.afc_instances += 1
            self.get_entities_statistics(component_def.entities)

    def print_statistics(self):
        skp_log("Print Model Info")
        print(
            "=" * 35
            + "\n"
            + "-> Edges                : %8i\n" % self.statistics.edges
            + "-> Faces                : %8i\n" % self.statistics.faces
            + "-> Instances            : %8i\n" % self.statistics.instances
            + "-> Groups               : %8i\n" % self.statistics.groups
            + "-> Component Definitions: %8i\n" % self.statistics.component_defs
            + "-> Materials            : %8i\n" % self.statistics.materials
            + "-> AFC Instances        : %8i\n" % self.statistics.afc_instances
            + "=" * 35
        )

    def return_model_statistics(self):
        self.get_model_statistics(self.SUModel)
        self.get_entities_statistics(self.SUModel.entities)
        self.print_statistics()
        return self.statistics
