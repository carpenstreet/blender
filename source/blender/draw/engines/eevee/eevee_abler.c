#include "eevee_abler.h"
#include "DRW_render.h"
#include "GPU_platform.h"
#include "GPU_texture.h"
#include "eevee_private.h"

void EEVEE_abler_prepass_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata)
{
  // Inspired by `workbench_opaque_engine_init`
  EEVEE_TextureList *txl = vedata->txl;
  EEVEE_FramebufferList *fbl = vedata->fbl;

  DRW_texture_ensure_fullscreen_2d(&txl->abler_depth_buffer, GPU_DEPTH24_STENCIL8, 0);
  DRW_texture_ensure_fullscreen_2d(&txl->abler_normal_buffer, GPU_RGBA16F, DRW_TEX_FILTER);
  DRW_texture_ensure_fullscreen_2d(&txl->abler_object_buffer, GPU_R16UI, 0);

  // Follow maxzbuffer_fb
  // TODO: Workaround for Intel GPUs
  GPU_framebuffer_ensure_config(&fbl->abler_copy_depth_fb,
                                {
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_depth_buffer),
                                    GPU_ATTACHMENT_LEAVE,
                                });

  GPU_framebuffer_ensure_config(&fbl->abler_prepass_fb,
                                {
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_depth_buffer),
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_normal_buffer),
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_object_buffer),
                                });
}

void EEVEE_abler_prepass_cache_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata)
{
  EEVEE_PassList *psl = vedata->psl;
  // Follow maxz_copydepth_ps
  DRW_PASS_CREATE(psl->abler_copy_depth_pass, DRW_STATE_WRITE_DEPTH | DRW_STATE_DEPTH_ALWAYS);
  DRW_PASS_CREATE(psl->abler_prepass, DRW_STATE_WRITE_COLOR | DRW_STATE_WRITE_DEPTH | DRW_STATE_DEPTH_LESS_EQUAL);

  struct GPUBatch *quad = DRW_cache_fullscreen_quad_get();
  DRWShadingGroup *grp = DRW_shgroup_create(EEVEE_shaders_abler_copy_depth_pass_sh_get(), psl->abler_copy_depth_pass);
  DefaultTextureList *dtxl = DRW_viewport_texture_list_get();
  DRW_shgroup_uniform_texture_ref_ex(grp, "depthBuffer", &dtxl->depth, GPU_SAMPLER_DEFAULT);
  DRW_shgroup_call(grp, quad, NULL);
}

void EEVEE_abler_prepass_cache_finish(EEVEE_Data *vedata)
{
  // Inspired by `workbench_cache_finish`
  EEVEE_TextureList *txl = vedata->txl;
  EEVEE_FramebufferList *fbl = vedata->fbl;

  // TODO: 중복 코드
  GPU_framebuffer_ensure_config(&fbl->abler_prepass_fb,
                                {
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_depth_buffer),
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_normal_buffer),
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_object_buffer),
                                });
  // TODO: workbench 의 id_clear_fb 용도 확인
}

void EEVEE_abler_prepass_draw(EEVEE_Data *vedata)
{
  const float clear_col[4] = {0.0f, 0.0f, 0.0f, 0.0f};

  EEVEE_PassList *psl = vedata->psl;
  EEVEE_FramebufferList *fbl = vedata->fbl;

  DRW_stats_group_start("Abler prepass");

  GPU_framebuffer_bind(fbl->abler_copy_depth_fb);
  DRW_draw_pass(psl->abler_copy_depth_pass);

//  GPU_framebuffer_bind(fbl->abler_prepass_fb);
//  GPU_framebuffer_clear_color_depth_stencil(fbl->abler_prepass_fb, clear_col, 1.0f, 0x00);
//  DRW_draw_pass(psl->abler_prepass);
  DRW_stats_group_end();

  // Restore
  GPU_framebuffer_bind(fbl->main_fb);
}

void EEVEE_abler_prepass_free()
{
  // Do nothing
}
