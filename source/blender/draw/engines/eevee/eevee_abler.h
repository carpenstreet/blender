#pragma once

#include "eevee_private.h"

void EEVEE_abler_prepass_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata);

void EEVEE_abler_prepass_cache_init(EEVEE_ViewLayerData *sldata, EEVEE_Data *vedata);

void EEVEE_abler_prepass_cache_finish(EEVEE_Data *vedata);

void EEVEE_abler_prepass_draw(EEVEE_Data *vedata);

void EEVEE_abler_prepass_free(void);
