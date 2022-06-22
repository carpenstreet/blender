uniform sampler2D ablerDepthBuffer;

void node_outline(vec3 normal,
                  float width,
                  out float depth,
                  out vec3 depth_hit_position,
                  out float negative_depth,
                  out vec3 negative_depth_hit_position,
                  out float object,
                  out float width_ws_size)
{
  vec3 viewNormal = normalize(normal_world_to_view(normal));
  depth_hit_position = vec3(0,0,0);
  negative_depth_hit_position = vec3(0, 0, 0);

  ivec2 texel = ivec2(gl_FragCoord.xy);
  float texel_depth = texelFetch(ablerDepthBuffer, texel, 0).r;
  float texel_z = get_view_z_from_depth(texel_depth);
  vec2 texel_uv = vec2(texel) / textureSize(ablerDepthBuffer, 0).xy;
  vec3 texel_vs = get_view_space_from_depth(texel_uv, texel_depth);

  //ivec2 offsets[4] = ivec2[4](ivec2(-1, -1), ivec2(-1, 1), ivec2(1, -1), ivec2(1, 1));
  ivec2 offsets[4] = ivec2[4](ivec2(-1, 0), ivec2(1, 0), ivec2(0, -1), ivec2(0, 1));

  float camera_dot = dot(viewNormal, normalize(-viewPosition));

  /*
  vec2 camera_jitter = vec2(ProjectionMatrix[2][0], ProjectionMatrix[2][1]);

  // If orthographic projection
  if (ProjectionMatrix[3][3] != 0.0)
  {
    camera_jitter = vec2(ProjectionMatrix[3][0], ProjectionMatrix[3][1]);
  }
  */

  float max_depth = 0.0;
  float min_depth = 0.0;

  float noise = texelFetch(utilTex, ivec3(0, 0, 2.0), 0).r;

  if (noise < fract(width))
  {
    width = ceil(width);
  }
  else
  {
    width = floor(width);
  }

  for (int i = 0; i < 4; i++)
  {
    ivec2 sample_offset = offsets[i] * int(round(width));

    ivec2 offset = texel + sample_offset;
    float offset_depth = texelFetch(ablerDepthBuffer, offset, 0).r;
    float offset_z = get_view_z_from_depth(offset_depth);
    vec2 offset_uv = vec2(offset) / textureSize(ablerDepthBuffer, 0).xy;
    vec3 offset_vs = get_view_space_from_depth(offset_uv, texel_depth);
    vec3 actual_offset_vs = get_view_space_from_depth(offset_uv, offset_depth);

    width_ws_size = length(offset_vs - texel_vs);

    vec3 ray_origin = vec3(0,0,0);
    // If orthographic projection
    if (ProjectionMatrix[3][3] != 0.0)
    {
      ray_origin = get_view_space_from_depth(offset_uv, 0);
    }

    vec3 ray_direction = normalize(offset_vs - ray_origin);

    // ray-plane intersection
    float expected_distance = (dot(viewNormal, texel_vs) - dot(ray_origin, viewNormal)) /
                      dot(ray_direction, viewNormal);

    float delta_depth = length(actual_offset_vs - ray_origin) - expected_distance;

    max_depth = max(max_depth, delta_depth);
    if (max_depth == delta_depth)
    {
      depth_hit_position = point_view_to_world(actual_offset_vs) - point_view_to_world(texel_vs);
    }
    min_depth = min(min_depth, delta_depth);
    if (min_depth == delta_depth)
    {
      negative_depth_hit_position = point_view_to_world(actual_offset_vs) - point_view_to_world(texel_vs);
    }
  }

  depth = max_depth;
  negative_depth = -min_depth;
  object = 0;
}