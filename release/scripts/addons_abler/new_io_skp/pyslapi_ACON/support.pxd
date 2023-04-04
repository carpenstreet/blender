cdef extern from "support.h":
    cdef cppclass KeepOffsetVec3:
        KeepOffsetVec3() except +
        int lookup(float x, float y, float z)
        int size()
