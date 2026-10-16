# Architecture (Phase 1)
Pipeline: BirthInput → `calendar_core.normalize` (tz, DST, true solar, Zi rule, lunar date) → `bazi.compute` / `tuvi.compute` → facts + trace.
- Bát Tự: year at Lập Xuân instant, month at jie instant (absolute UTC), day by sxtwl, hour by ngũ thử độn; luck start = days to adjacent jie / 3.
- Tử Vi: lunar year/month/day (VN UTC+7, UTC+8 before 1968; or CN), school pack `vn_tan_bien_draft`.
- The two systems share only the calendar layer; no rule is shared.
- Facts (pillars, stars, relations) are the input of the future inference graph; relations never assert 'hóa'.
