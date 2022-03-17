/*
 * Copyright 2011-2018 Blender Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#pragma once

#include "kernel/bvh/bvh.h"

CCL_NAMESPACE_BEGIN

#ifdef __SHADER_RAYTRACE__

typedef struct OutlineResult {
  float max_depth;
  float3 max_depth_hit_position;
  float min_depth;
  float3 min_depth_hit_position;
  // float min_dot;
  float contour;
  float width_ws_size;
} OutlineResult;

#  ifdef __KERNEL_OPTIX__
extern "C" __device__ float __direct_callable__svm_node_outline(
#  else
ccl_device OutlineResult svm_outline(
#  endif
    KernelGlobals kg,
    ConstIntegratorState state,
    ccl_private ShaderData *sd,
    float3 N,
    float width)
{
  OutlineResult result;
  result.max_depth = 0.0f;
  result.min_depth = 0.0f;
  // result.min_dot = 1.0f;
  result.contour = 0.0f;
  result.max_depth_hit_position = make_float3(0, 0, 0);
  result.min_depth_hit_position = make_float3(0, 0, 0);

  /* Early out if no sampling needed. */
  if (/*num_samples < 1 ||*/ sd->object == OBJECT_NONE) {
    return result;
  }

  // TODO: early out if non camera, transparent or reflection ray ???

  /* Can't raytrace from shaders like displacement, before BVH exists. */
  if (kernel_data.bvh.bvh_layout == BVH_LAYOUT_NONE) {
    return result;
  }

  float3 offsets[4] = {
      make_float3(-1, 0, 0), make_float3(1, 0, 0), make_float3(0, -1, 0), make_float3(0, 1, 0)};

  /*
  float sample_rotation = path_rng_1D(
      kg, state->rng_hash, state->sample, state->num_samples, PRNG_BEVEL_U);
  sample_rotation *= M_PI_2_F;

  float cosine = cos(sample_rotation);
  float sine = sin(sample_rotation);

  for (int i = 0; i < 4; i++)
  {
    offsets[i].x = offsets[i].x * cosine - offsets[i].y * sine;
    offsets[i].y = offsets[i].x * sine   + offsets[i].y * cosine;
  }
  */

  float max_depth = 0.0f;
  float min_depth = 0.0f;
  // float min_dot = 1.0f;
  bool contour = false;

  float3 trace_start = sd->P + sd->I * sd->ray_length;

  float3 raster_P = transform_perspective(&kernel_data.cam.worldtoraster, sd->P);

  for (int i = 0; i < 4; i++) {
    float3 trace_target_raster = raster_P + (offsets[i] * width);
    float3 trace_target = transform_perspective(&kernel_data.cam.rastertoworld,
                                                trace_target_raster);

    result.width_ws_size = len(sd->P - trace_target);

    if (kernel_data.cam.type == CAMERA_ORTHOGRAPHIC) {
      trace_start = trace_target + sd->I * sd->ray_length;
    }

    float3 trace_direction = normalize(trace_target - trace_start);

    Ray ray;
    ray.P = trace_start;
    ray.D = trace_direction;
    ray.t = 1000000000000.0f;  // TODO
    ray.time = sd->time;
    ray.dP = differential_zero_compact();
    ray.dD = differential_zero_compact();

    Intersection intersection;
    if (scene_intersect(kg, &ray, PATH_RAY_CAMERA, &intersection)) {
      // ray-plane intersection
      float expected_distance = (dot(N, sd->P) - dot(trace_start, N)) / dot(trace_direction, N);

      float delta_depth = intersection.t - expected_distance;

      max_depth = max(max_depth, delta_depth);
      if (max_depth == delta_depth) {
        result.max_depth_hit_position = (trace_start + trace_direction * intersection.t) - sd->P;
      }
      min_depth = min(min_depth, delta_depth);
      if (min_depth == delta_depth) {
        result.min_depth_hit_position = (trace_start + trace_direction * intersection.t) - sd->P;
      }

      // TODO: primitive and shader ID contour
      if (intersection.object != sd->object) {
        contour = true;
      }
    }
    else {
      max_depth = 1000000000000.0f;
      result.max_depth_hit_position = (trace_start + trace_direction * max_depth) - sd->P;
      // min_dot = -1.0f;
      contour = true;
    }
  }

  result.max_depth = max_depth;
  result.min_depth = min_depth;
  // result.min_dot = min_dot;
  if (contour)
    result.contour = 1.0f;

  return result;
}

template<uint node_feature_mask, typename ConstIntegratorGenericState>
#  if defined(__KERNEL_OPTIX__)
ccl_device_inline
#  else
ccl_device_noinline
#  endif
    void
    svm_node_outline(KernelGlobals kg,
                     ConstIntegratorGenericState state,
                     ccl_private ShaderData *sd,
                     ccl_private float *stack,
                     uint4 node)
{
  uint normal_offset, width_offset, depth_offset, depth_hit_position_offset, negative_depth_offset,
      negative_depth_hit_position_offset, object_offset, width_ws_size_offset;

  svm_unpack_node_uchar4(
      node.y, &normal_offset, &width_offset, &depth_offset, &depth_hit_position_offset);

  svm_unpack_node_uchar4(node.z,
                         &negative_depth_offset,
                         &negative_depth_hit_position_offset,
                         &object_offset,
                         &width_ws_size_offset);
  OutlineResult result;
  memset(&result, 0, sizeof(result));
  IF_KERNEL_NODES_FEATURE(RAYTRACE)
  {
    float3 normal = stack_valid(normal_offset) ? stack_load_float3(stack, normal_offset) : sd->N;
    float width = stack_load_float(stack, width_offset);

#  ifdef __KERNEL_OPTIX__
    result = optixDirectCall<float>(0, kg, state, sd, normal, width);
#  else
    result = svm_outline(kg, state, sd, normal, width);
#  endif
  }

  if (stack_valid(depth_offset)) {
    stack_store_float(stack, depth_offset, result.max_depth);
  }
  if (stack_valid(depth_hit_position_offset)) {
    stack_store_float3(stack, depth_hit_position_offset, result.max_depth_hit_position);
  }
  if (stack_valid(negative_depth_offset)) {
    stack_store_float(stack, negative_depth_offset, -result.min_depth);
  }
  if (stack_valid(negative_depth_hit_position_offset)) {
    stack_store_float3(stack, negative_depth_hit_position_offset, result.min_depth_hit_position);
  }
  if (stack_valid(object_offset)) {
    stack_store_float(stack, object_offset, result.contour);
  }
  if (stack_valid(width_ws_size_offset)) {
    stack_store_float(stack, width_ws_size_offset, result.width_ws_size);
  }
}

#endif /* __SHADER_RAYTRACE__ */

CCL_NAMESPACE_END