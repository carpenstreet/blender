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

  // Adapted from maxzbuffer_fb
  GPU_framebuffer_ensure_config(&fbl->abler_copy_depth_fb,
                                {
                                    GPU_ATTACHMENT_TEXTURE(txl->abler_depth_buffer),
                                    GPU_ATTACHMENT_LEAVE,
                                });
}

void EEVEE_abler_prepass_cache_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata)
{
  EEVEE_PassList *psl = vedata->psl;

  {
    // Adapted from maxz_copydepth_ps
    DRW_PASS_CREATE(psl->abler_copy_depth_pass, DRW_STATE_WRITE_DEPTH | DRW_STATE_DEPTH_ALWAYS);
    struct GPUBatch *quad = DRW_cache_fullscreen_quad_get();
    DRWShadingGroup *grp = DRW_shgroup_create(EEVEE_shaders_abler_copy_depth_pass_sh_get(),
                                              psl->abler_copy_depth_pass);
    DefaultTextureList *dtxl = DRW_viewport_texture_list_get();
    DRW_shgroup_uniform_texture_ref_ex(grp, "depthBuffer", &dtxl->depth, GPU_SAMPLER_DEFAULT);
    DRW_shgroup_call(grp, quad, NULL);
  }
}

void EEVEE_abler_prepass_cache_finish(EEVEE_Data *vedata)
{
  // Do nothing now, leaved for future use
}

void EEVEE_abler_prepass_draw(EEVEE_Data *vedata)
{
  EEVEE_PassList *psl = vedata->psl;
  EEVEE_FramebufferList *fbl = vedata->fbl;

  DRW_stats_group_start("Abler copy depth pass");

  GPU_framebuffer_bind(fbl->abler_copy_depth_fb);
  DRW_draw_pass(psl->abler_copy_depth_pass);

  DRW_stats_group_end();

  // Restore
  GPU_framebuffer_bind(fbl->main_fb);
}

void EEVEE_abler_prepass_free()
{
  // Do nothing now, leaved for future use
}
