#include <utility>
#include "support.h"

KeepOffsetVec3::KeepOffsetVec3() = default;
KeepOffsetVec3::~KeepOffsetVec3() = default;

int KeepOffsetVec3::lookup(float x, float y, float z) {
    vec3 item {x, y, z};
    if (offsets.find(item) == offsets.end()) {
        offsets[item] = (int)offsets.size();
    }
    return offsets.at(item);
}

int KeepOffsetVec3::size() {
    return offsets.size();
}