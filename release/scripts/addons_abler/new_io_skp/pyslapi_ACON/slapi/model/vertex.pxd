# -*- coding: utf-8 -*-
from libcpp cimport bool
from slapi.color cimport *
from slapi.model.defs cimport *
from slapi.geometry cimport *
from slapi.transformation cimport SUTransformation
from slapi.unicodestring cimport *
from slapi.model.geometry_input cimport *

cdef extern from "SketchUpAPI/model/vertex.h":
	SUEntityRef SUVertexToEntity(SUVertexRef vertex)
	SUVertexRef SUVertexFromEntity(SUEntityRef entity)
	SU_RESULT SUVertexGetPosition(SUVertexRef vertex, const SUPoint3D* position)
	SU_RESULT SUVertexSetPosition(SUVertexRef vertex, const SUPoint3D* position)
	SU_RESULT SUVertexGetNumEdges(SUVertexRef vertex, size_t *count)
	SU_RESULT SUVertexGetEdges(SUVertexRef vertex, size_t len, SUEdgeRef edges[], size_t *count)
	SU_RESULT SUVertexGetNumFaces(SUVertexRef vertex, size_t *count)
	SU_RESULT SUVertexGetFaces(SUVertexRef vertex, size_t len, SUFaceRef faces[], size_t *count)
	SU_RESULT SUVertexGetNumLoops(SUVertexRef vertex, size_t *count)
	SU_RESULT SUVertexGetLoops(SUVertexRef vertex, size_t len, SULoopRef loops[], size_t *count)
