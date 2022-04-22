#pragma BLENDER_REQUIRE(common_view_lib.glsl)

layout(location = 0) out vec3 normalData;
layout(location = 1) out uint objectId;

in vec3 normal_interp;
flat in int object_id;

// Inspired by workbench_prepass_frag.glsl
void main()
{
  normalData = normal_interp;
  objectId = uint(object_id);
}
