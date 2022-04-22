#pragma BLENDER_REQUIRE(common_view_lib.glsl)

in vec3 pos;
in vec3 nor;

out vec3 normal_interp;
flat out int object_id;

// Inspired by workbench_prepass_vert.glsl
void main()
{
  vec3 world_pos = point_object_to_world(pos);
  gl_Position = point_world_to_ndc(world_pos);
  normal_interp = normalize(normal_object_to_view(nor));
  object_id = int(uint(resource_handle) & 0xFFFFu) + 1;
}
