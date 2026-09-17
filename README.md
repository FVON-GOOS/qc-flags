# FVON QC flags: where we are

One row per test: its status, the parameters it flags, the thresholds and the flag each condition produces, and what the group still has to decide. The full page with the three flag standards is in [`docs/index.html`](docs/index.html) (rendered at https://fvon-goos.github.io/qc-flags/).

**How to give feedback.** Every test has a [Discussion](../../discussions). Reply there with the status you want (compulsory, optional, not applied), the thresholds you would apply and why. One reply per person is enough; edit it if you change your mind. This summary is updated from the threads before each subcommittee meeting. To suggest a test that is not listed, use the [proposals thread](https://github.com/FVON-GOOS/qc-flags/discussions/17).

## Flag scale

FVON uses the IOC Manuals and Guides 54 scale: 0 no QC, 1 good, 2 probably good, 3 suspect, 4 bad, 5 corrected, 9 missing. One flag per variable; a derived variable inherits the worst flag of its inputs. QARTOD uses 1 pass, 2 not evaluated, 3 suspect, 4 fail, 9 missing. SeaDataNet (L20) uses 0 to 9 with 3 meaning probably bad, plus 6 below detection, 7 in excess, 8 interpolated and letter codes for uncertain values.

## Variable names

Each test writes its own flag, named under the test in the table, and contributes to the combined flag of every parameter it assesses. FVON names in the code today: time `DATETIME_QC`, position `LOCATION_QC`, pressure `PRESSURE_QC`, temperature `TEMPERATURE_QC`, salinity `SALINITY_QC`, conductivity `CONDUCTIVITY_QC`. The SeaDataNet publication of FVON data names one flag per parameter after the parameter itself (position `POSITION_QC`, pressure `DEPTH_QC`, temperature `TEMP_QC`, `QV_SEADATANET` in ODV exports) and carries no separate time flag. Which set FVON adopts, and whether the per-test flags are published alongside the combined ones, is part of the discussion.

## Test by test

| Test | Status | Parameters | Thresholds | Discussion |
|---|---|---|---|---|
| **Compulsory** | | | | |
| [Impossible date](https://github.com/FVON-GOOS/qc-flags/discussions/1)<br>`flag_date` | compulsory | time `DATETIME_QC` | before 1990 or in the future → **4**<br>gap longer than the expected interval → **3** | Cutoff year: 1900, 1990 or 2010. |
| [Impossible location](https://github.com/FVON-GOOS/qc-flags/discussions/2)<br>`flag_location` | compulsory | position `LOCATION_QC` | latitude outside ±90 or longitude outside ±180 → **4** | Settled. |
| [Impossible speed](https://github.com/FVON-GOOS/qc-flags/discussions/3)<br>`flag_speed` | compulsory | position `LOCATION_QC` | mobile gear, 8 to 30 knots → **3**<br>over 30 knots → **4** | Confirm the limits: based on GPS accuracy or on fishing speed, and whether they vary by gear. |
| [Global range](https://github.com/FVON-GOOS/qc-flags/discussions/4)<br>`flag_global_range` | compulsory | temperature `TEMPERATURE_QC`<br>pressure `PRESSURE_QC`<br>salinity `SALINITY_QC`<br>conductivity `CONDUCTIVITY_QC` | outside the sensor's range from the manufacturer table → **4**<br>sensor unknown: outside −2.5 to 40 °C, 0 to 11000 dbar, 2 to 42 PSU → **4** | Sensor tables incomplete. Decide whether two inner tiers, calibrated range and operating range, give 2 and 3. |
| [Spike](https://github.com/FVON-GOOS/qc-flags/discussions/5)<br>`flag_temp_spike` `flag_sal_spike` | compulsory | temperature `TEMPERATURE_QC`<br>salinity `SALINITY_QC`<br>pressure `PRESSURE_QC` | difference to both neighbours over 6 °C above 200 m, 2 °C below, or 0.9 PSU → **3** | Absolute differences or standard deviations. No pressure threshold yet. |
| [Stuck value](https://github.com/FVON-GOOS/qc-flags/discussions/6)<br>`flag_temp_stuck` `flag_sal_stuck` | compulsory | temperature `TEMPERATURE_QC`<br>salinity `SALINITY_QC`<br>pressure `PRESSURE_QC` | 3 to 5 identical values within 0.001 → **3**<br>more than 5 → **4** | Counts and tolerance for "identical" (0.001 or 0.01 °C). Row counts mislead on fixed gear, where sampling slows at rest; count time instead. |
| [Calibration date](https://github.com/FVON-GOOS/qc-flags/discussions/7)<br>`flag_calibration_date` | compulsory | temperature `TEMPERATURE_QC`<br>pressure `PRESSURE_QC`<br>salinity `SALINITY_QC` | past the manufacturer's recalibration interval → **3**<br>no calibration date → **4**<br>no timestamp → **9** | We need all manufacturers' information to apply this flag. |
| **Optional** | | | | |
| [Climatology](https://github.com/FVON-GOOS/qc-flags/discussions/8)<br>`flag_clima` | optional | temperature `TEMPERATURE_QC`<br>salinity `SALINITY_QC` | outside the seasonal mean ± N standard deviations, WOA or regional → **3** | Climatology source and coastal accuracy; our data are meant to improve the climatologies. |
| [Mud](https://github.com/FVON-GOOS/qc-flags/discussions/9)<br>`flag_mud` | optional | temperature `TEMPERATURE_QC`<br>salinity `SALINITY_QC` | fouling signature on the ascent → **3** | Detection criteria per parameter still to write. |
| [Drift](https://github.com/FVON-GOOS/qc-flags/discussions/10)<br>`flag_drift` | optional | temperature `TEMPERATURE_QC`<br>salinity `SALINITY_QC` | not defined | Decide between long-term calibration drift, which belongs to delayed mode, and a real-time damaged-sensor check on the bottom segment. |
| **Not applied** | | | | |
| [Position on land](https://github.com/FVON-GOOS/qc-flags/discussions/11)<br>`flag_land` | not applied | position `LOCATION_QC` | on land per ETOPO5 or better → **4** | Kept off because land masks are poor near shore. If a program enables it, 3 rather than 4. |
| **To decide** | | | | |
| [Gear type control](https://github.com/FVON-GOOS/qc-flags/discussions/12)<br>`flag_gear_type` | to decide | position `LOCATION_QC` | fixed gear, deployment to retrieval over 200 m → **3**<br>mobile gear: to be defined; drifting gear: not applied | We need to differentiate mobile from fixed gear. This should not apply to drifting gear. |
| [Rate of change](https://github.com/FVON-GOOS/qc-flags/discussions/13)<br>`flag_RoC` | to decide | temperature `TEMPERATURE_QC`<br>salinity `SALINITY_QC` | change from the previous value over 3 standard deviations of the segment → **3** | Compulsory, optional or not applied. |
| [Cold surface](https://github.com/FVON-GOOS/qc-flags/discussions/14)<br>`flag_cold_surface` | to decide | temperature `TEMPERATURE_QC` | not defined | Separate test, or surface thresholds inside the spike test. |
| [Response time](https://github.com/FVON-GOOS/qc-flags/discussions/15)<br>`flag_response_time` | to decide | temperature `TEMPERATURE_QC` | not defined; thermistor lag blurs gradients | Implement or not; quantify per sensor; 3 rather than 4 since the data are imprecise, not wrong. |
| [Rollover](https://github.com/FVON-GOOS/qc-flags/discussions/16)<br>`flag_rollover` | to decide | temperature `TEMPERATURE_QC` | proposal: bottom value more than 1 °C from its neighbour → **3** | Threshold, what counts as adjacent, profiling gear only, whether salinity gets the same. |

## Files

- `flags.json`: the data behind the table (status, parameters, thresholds, discussion per test). Change it and run `build_flags.py` and `build_readme.py`.
- `docs/index.html`: the full page, including the description of the FVON, QARTOD and SeaDataNet standards.
- `build_flags.py`, `build_readme.py`, `flags-body.html`, `page.css`: the generators.

Maintained by the FVON Data Management Subcommittee.