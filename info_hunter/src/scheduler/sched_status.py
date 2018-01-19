#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum

class WLEnum(Enum) :
    WL_RUNNING = 'wl_running'
    WL_COMPLETED = 'wl_completed'

    WL_SALVAGE = 'wl_salvage'
    WL_SALVAGE_SUCC = 'wl_salvage_succ'
    WL_SALVAGE_FAIL = 'wl_salvage_fail'

    WL_SUMMON = 'wl_summon'
    WL_SUMMON_SUCC = 'wl_summon_succ'
    WL_SUMMON_FAIL = 'wl_summon_fail'

    WL_PURIFY = 'wl_purify'
    WL_PURIFY_SUCC = 'wl_purify_succ'
    WL_PURIFY_FAIL = 'wl_purify_fail'


