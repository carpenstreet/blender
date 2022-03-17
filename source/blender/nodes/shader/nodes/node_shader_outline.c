/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * The Original Code is Copyright (C) 2005 Blender Foundation.
 * All rights reserved.
 */

#include "../node_shader_util.h"

/* **************** OUTPUT ******************** */

static bNodeSocketTemplate sh_node_outline_in[] = {
    {SOCK_VECTOR, N_("Normal"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f, PROP_NONE, SOCK_HIDE_VALUE},
    {SOCK_FLOAT, N_("Width"), 1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1000.0f},
    {-1, ""},
};

static bNodeSocketTemplate sh_node_outline_out[] = {
    {SOCK_FLOAT, N_("Depth"), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1000.0f},
    {SOCK_VECTOR,
     N_("Depth Hit Position"),
     0.0f,
     0.0f,
     0.0f,
     0.0f,
     -100000000000.0f,
     100000000000.0f},
    {SOCK_FLOAT, N_("Negative Depth"), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1000.0f},
    {SOCK_VECTOR,
     N_("Negative Depth Hit Position"),
     0.0f,
     0.0f,
     0.0f,
     0.0f,
     -100000000000.0f,
     100000000000.0f},
    //{SOCK_FLOAT, N_("Dot"), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f},
    {SOCK_FLOAT, N_("Object"), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f},
    {SOCK_FLOAT, N_("Width WorldSpace Size"), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f},
    {-1, ""},
};

static int node_shader_gpu_outline(GPUMaterial *mat,
                                   bNode *node,
                                   bNodeExecData *UNUSED(execdata),
                                   GPUNodeStack *in,
                                   GPUNodeStack *out)
{
  if (!in[0].link) {
    GPU_link(mat, "world_normals_get", &in[0].link);
  }

  GPU_material_flag_set(mat, GPU_MATFLAG_DIFFUSE);

  return GPU_stack_link(mat, node, "node_outline", in, out);
}

static void node_shader_init_outline(bNodeTree *UNUSED(ntree), bNode *node)
{
}

/* node type definition */
void register_node_type_sh_outline(void)
{
  static bNodeType ntype;

  sh_node_type_base(&ntype, SH_NODE_OUTLINE, "Outline", NODE_CLASS_INPUT, 0);
  node_type_socket_templates(&ntype, sh_node_outline_in, sh_node_outline_out);
  node_type_init(&ntype, node_shader_init_outline);
  node_type_storage(&ntype, "", NULL, NULL);
  node_type_gpu(&ntype, node_shader_gpu_outline);

  nodeRegisterType(&ntype);
}