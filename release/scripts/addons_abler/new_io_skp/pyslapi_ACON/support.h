#pragma once
#include <memory>
#include <unordered_map>

struct vec3 {
  float x, y, z;
};

struct Vec3Hash {
    std::size_t operator()(const vec3& v) const {
        return std::hash<float>()(v.x) ^ std::hash<float>()(v.y) ^ std::hash<float>()(v.z);
    }
};

struct Vec3Eq {
    bool operator()(const vec3& lhs, const vec3& rhs) const {
        return lhs.x == rhs.x && lhs.y == rhs.y && lhs.z == rhs.z;
    }
};

class KeepOffsetVec3 {
public:
  KeepOffsetVec3();
  ~KeepOffsetVec3();
  int lookup(float x, float y, float z);
  int size();
private:
  std::unordered_map<vec3, int, Vec3Hash, Vec3Eq> offsets;
};
