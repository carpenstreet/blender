#pragma once

#include "eevee_private.h"

void EEVEE_abler_prepass_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata);

void EEVEE_abler_prepass_cache_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata);

// 불투명 재질에 대해서만 캐시를 생성하도록 EEVEE_materials_cache_populate 에서 대신 처리
// void EEVEE_abler_prepass_cache_populate(EEVEE_Data *vedata, Object *ob);

void EEVEE_abler_prepass_cache_finish(EEVEE_Data *vedata);

void EEVEE_abler_prepass_draw(EEVEE_Data *vedata);

void EEVEE_abler_prepass_free(void);
