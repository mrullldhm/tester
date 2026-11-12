# Price Reversal v2: hour and entry study

Generated 2026-11-11 20:57 UTC by `tools/price_reversal_v2_study.py` on 2010-06-07 00:00:00+00:00 to 2026-11-10 08:27:00+00:00 (5,680,278 one-minute bars).

> **In-sample, all available bars including the reserved 2024+ interval.** The hour table covers 23 x 64 = 1,472 settings and the entry table 3 x 16 = 48; the best of many looks better than it is. This page is for choosing what to test in feature 2 on the development interval, not a result.

Properties: $50,000, 1 contract, $2.01 per order ($4.02 round trip), limit entries.

## 1. Hourly anchors (all available bars, 0 ticks)

Each hour ran the same 64-setting FPR grid. **Median net** and **positive settings** describe the whole grid, so they are not inflated by picking the best of 64; **best net** is the in-sample top setting. The DST columns split the best setting's trades by US clock (summer = EDT, hour 1 opens 06:00 Malaysia; winter = EST, 07:00 Malaysia).

| Hour | Opens ET | Opens Malaysia (US summer / winter) | Median net (64) | Positive settings | Best net | Best setting | Trades | PF | Max DD | US summer net | US winter net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 18:00 | 06:00 / 07:00 | 23,729.02 USD | 64 / 64 | 34,149.78 USD | w60 x2.0 rr2 | 2,811 | 1.164 | 10,026.72 USD | 20,493.00 USD (1850) | 13,656.78 USD (961) |
| 2 | 19:00 | 07:00 / 08:00 | 850.11 USD | 35 / 64 | 7,160.88 USD | w60 x0.5 far | 2,256 | 1.085 | 5,247.46 USD | 7,457.48 USD (1426) | -296.60 USD (830) |
| 3 | 20:00 | 08:00 / 09:00 | -19,344.76 USD | 0 / 64 | -6,180.08 USD | w30 x0.5 near | 1,204 | 0.890 | 7,503.94 USD | -6,002.28 USD (814) | -177.80 USD (390) |
| 4 | 21:00 | 09:00 / 10:00 | -24,860.83 USD | 0 / 64 | -6,557.46 USD | w30 x0.5 rr1 | 1,273 | 0.908 | 8,073.50 USD | -5,433.18 USD (859) | -1,124.28 USD (414) |
| 5 | 22:00 | 10:00 / 11:00 | -11,114.20 USD | 0 / 64 | -2,322.16 USD | w60 x0.5 rr2 | 2,508 | 0.985 | 11,827.62 USD | -2,870.48 USD (1724) | 548.32 USD (784) |
| 6 | 23:00 | 11:00 / 12:00 | -20,799.85 USD | 0 / 64 | -4,014.16 USD | w30 x1.0 far | 1,108 | 0.901 | 6,623.08 USD | -4,848.26 USD (813) | 834.10 USD (295) |
| 7 | 00:00 | 12:00 / 13:00 | -12,591.37 USD | 0 / 64 | -4,945.88 USD | w30 x1.0 near | 994 | 0.829 | 5,768.20 USD | -3,339.08 USD (654) | -1,606.80 USD (340) |
| 8 | 01:00 | 13:00 / 14:00 | -10,394.46 USD | 0 / 64 | -993.80 USD | w60 x1.0 rr2 | 2,690 | 0.994 | 8,234.94 USD | -1,517.76 USD (1788) | 523.96 USD (902) |
| 9 | 02:00 | 14:00 / 15:00 | -24,807.18 USD | 0 / 64 | -4,418.10 USD | w30 x0.5 rr1 | 1,405 | 0.943 | 10,676.40 USD | -302.32 USD (916) | -4,115.78 USD (489) |
| 10 | 03:00 | 15:00 / 16:00 | -12,389.99 USD | 10 / 64 | 12,568.38 USD | w30 x1.5 rr2 | 1,881 | 1.079 | 7,586.28 USD | 14,287.36 USD (1232) | -1,718.98 USD (649) |
| 11 | 04:00 | 16:00 / 17:00 | -19,527.60 USD | 5 / 64 | 6,729.62 USD | w30 x0.5 rr2 | 1,719 | 1.043 | 8,178.26 USD | 7,400.72 USD (1164) | -671.10 USD (555) |
| 12 | 05:00 | 17:00 / 18:00 | -8,268.95 USD | 2 / 64 | 263.34 USD | w30 x1.0 near | 1,733 | 1.003 | 7,765.48 USD | 5,544.54 USD (1173) | -5,281.20 USD (560) |
| 13 | 06:00 | 18:00 / 19:00 | -8,616.53 USD | 4 / 64 | 612.88 USD | w30 x1.0 far | 1,656 | 1.007 | 8,856.16 USD | 1,513.88 USD (1106) | -901.00 USD (550) |
| 14 | 07:00 | 19:00 / 20:00 | -7,264.83 USD | 8 / 64 | 5,251.24 USD | w90 x1.0 near | 4,338 | 1.020 | 14,904.96 USD | 1,958.68 USD (2866) | 3,292.56 USD (1472) |
| 15 | 08:00 | 20:00 / 21:00 | -10,522.30 USD | 8 / 64 | 10,896.22 USD | w120 x0.5 rr2 | 4,889 | 1.017 | 26,052.96 USD | 11,853.04 USD (3248) | -956.82 USD (1641) |
| 16 | 09:00 | 21:00 / 22:00 | -16,780.69 USD | 15 / 64 | 35,362.52 USD | w90 x0.5 rr2 | 4,074 | 1.057 | 30,603.88 USD | 16,340.32 USD (2684) | 19,022.20 USD (1390) |
| 17 | 10:00 | 22:00 / 23:00 | -9,026.51 USD | 17 / 64 | 10,388.30 USD | w90 x1.0 rr1 | 4,585 | 1.019 | 16,717.90 USD | 7,374.88 USD (3056) | 3,013.42 USD (1529) |
| 18 | 11:00 | 23:00 / 00:00 | -49,380.04 USD | 7 / 64 | 7,334.50 USD | w30 x0.5 far | 1,775 | 1.047 | 11,572.74 USD | 6,687.86 USD (1207) | 646.64 USD (568) |
| 19 | 12:00 | 00:00 / 01:00 | -17,785.94 USD | 3 / 64 | 4,891.62 USD | w60 x2.0 near | 3,119 | 1.022 | 12,706.98 USD | 1,752.42 USD (2079) | 3,139.20 USD (1040) |
| 20 | 13:00 | 01:00 / 02:00 | -15,623.35 USD | 1 / 64 | 1,595.98 USD | w90 x0.5 rr1 | 4,001 | 1.004 | 24,764.78 USD | 70.22 USD (2689) | 1,525.76 USD (1312) |
| 21 | 14:00 | 02:00 / 03:00 | -1,410.02 USD | 26 / 64 | 23,031.16 USD | w30 x1.5 rr1 | 1,542 | 1.171 | 9,297.32 USD | 13,833.32 USD (1034) | 9,197.84 USD (508) |
| 22 | 15:00 | 03:00 / 04:00 | -8,389.03 USD | 4 / 64 | 858.28 USD | w60 x2.0 near | 2,386 | 1.008 | 7,100.00 USD | 547.90 USD (1605) | 310.38 USD (781) |
| 23 | 16:00 | 04:00 / 05:00 | -4,590.50 USD | 5 / 64 | 608.14 USD | w30 x1.5 far | 993 | 1.017 | 2,980.46 USD | -338.98 USD (649) | 947.12 USD (344) |

### Median net by target, per hour

| Hour | far | near | rr1 | rr2 |
|---|---|---|---|---|
| 1 | 24,226.80 USD | 21,963.70 USD | 22,711.48 USD | 26,327.96 USD |
| 2 | 2,449.88 USD | 1,776.16 USD | -3,420.34 USD | 3,948.78 USD |
| 3 | -19,276.30 USD | -20,003.89 USD | -13,830.41 USD | -26,412.93 USD |
| 4 | -23,409.23 USD | -25,199.10 USD | -26,254.62 USD | -27,110.15 USD |
| 5 | -12,621.36 USD | -11,312.03 USD | -12,869.55 USD | -8,921.78 USD |
| 6 | -17,326.33 USD | -17,544.09 USD | -19,869.79 USD | -21,906.55 USD |
| 7 | -11,062.93 USD | -10,445.92 USD | -10,605.10 USD | -13,471.18 USD |
| 8 | -21,988.58 USD | -17,296.22 USD | -11,765.60 USD | -5,117.57 USD |
| 9 | -24,682.85 USD | -24,537.50 USD | -21,831.58 USD | -27,714.69 USD |
| 10 | -12,389.99 USD | -16,691.85 USD | -15,296.13 USD | -1,081.04 USD |
| 11 | -33,059.45 USD | -33,072.59 USD | -17,577.39 USD | -5,281.78 USD |
| 12 | -8,383.13 USD | -8,557.64 USD | -4,135.02 USD | -13,221.50 USD |
| 13 | -8,906.30 USD | -9,412.46 USD | -4,422.51 USD | -9,848.97 USD |
| 14 | -4,466.52 USD | -4,253.14 USD | -10,355.17 USD | -14,958.07 USD |
| 15 | -10,444.12 USD | -11,334.02 USD | -9,201.77 USD | -13,960.54 USD |
| 16 | -17,102.45 USD | -27,110.21 USD | -24,103.89 USD | 11,399.11 USD |
| 17 | -11,143.90 USD | -19,512.18 USD | 3,398.43 USD | -20.27 USD |
| 18 | -50,638.21 USD | -55,428.16 USD | -41,028.99 USD | -83,334.88 USD |
| 19 | -16,640.75 USD | -6,288.92 USD | -19,044.46 USD | -31,117.77 USD |
| 20 | -17,200.12 USD | -20,248.06 USD | -9,411.11 USD | -15,784.92 USD |
| 21 | -1,159.92 USD | -2,058.84 USD | 1,877.51 USD | -6,705.06 USD |
| 22 | -6,174.83 USD | -2,108.36 USD | -11,639.99 USD | -25,584.66 USD |
| 23 | -4,158.02 USD | -4,485.56 USD | -4,850.18 USD | -6,949.04 USD |

## 2. Entry cap and fixed TP on the FPR session baselines (all available bars)

`cap 0 / default` is Fair Price Reversal unchanged. A cap N moves the limit to N ticks from the stop only when the signal close is further away; otherwise the entry is the signal close. Limits never slip; the 1 / 2 tick columns slip stops and session-end market exits only.

### asia (`window=30`, `atr_mult=2.0`, `target=rr2`)

| Cap | TP | Net 0 / 1 / 2 ticks | Trades | % win | PF | Avg trade | Avg win | Avg loss | Largest loss | Max DD | Net / max DD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| close | default | -5,035.22 USD / -15,925.22 USD / -26,815.22 USD | 1,561 | 32.48% | 0.959 | -3.23 USD | 231.90 USD | -116.33 USD | -1,794.02 USD | 10,296.38 USD | -0.49 |
| close | fixed | -11,441.30 USD / -24,881.30 USD / -38,321.30 USD | 1,565 | 21.60% | 0.915 | -7.31 USD | 365.92 USD | -110.12 USD | -1,794.02 USD | 14,832.72 USD | -0.77 |
| 20 | default | -9,438.04 USD / -19,868.04 USD / -30,298.04 USD | 1,502 | 31.82% | 0.908 | -6.28 USD | 193.99 USD | -99.77 USD | -204.02 USD | 10,190.76 USD | -0.93 |
| 20 | fixed | -14,944.12 USD / -27,874.12 USD / -40,804.12 USD | 1,506 | 20.78% | 0.869 | -9.92 USD | 316.43 USD | -95.55 USD | -204.02 USD | 15,471.16 USD | -0.97 |
| 25 | default | -13,000.30 USD / -23,570.30 USD / -34,140.30 USD | 1,515 | 31.62% | 0.880 | -8.58 USD | 198.86 USD | -104.49 USD | -254.02 USD | 13,777.94 USD | -0.94 |
| 25 | fixed | -20,646.38 USD / -33,766.38 USD / -46,886.38 USD | 1,519 | 20.41% | 0.829 | -13.59 USD | 322.98 USD | -99.89 USD | -254.02 USD | 21,118.34 USD | -0.98 |
| 30 | default | -13,644.52 USD / -24,314.52 USD / -34,984.52 USD | 1,526 | 31.72% | 0.878 | -8.94 USD | 202.72 USD | -107.25 USD | -304.02 USD | 14,572.16 USD | -0.94 |
| 30 | fixed | -20,970.60 USD / -34,190.60 USD / -47,410.60 USD | 1,530 | 20.59% | 0.831 | -13.71 USD | 327.95 USD | -102.28 USD | -304.02 USD | 21,592.56 USD | -0.97 |
| 35 | default | -12,392.66 USD / -23,092.66 USD / -33,792.66 USD | 1,533 | 31.90% | 0.891 | -8.08 USD | 207.66 USD | -109.13 USD | -354.02 USD | 13,470.30 USD | -0.92 |
| 35 | fixed | -19,538.74 USD / -32,788.74 USD / -46,038.74 USD | 1,537 | 20.82% | 0.845 | -12.71 USD | 334.11 USD | -103.90 USD | -354.02 USD | 20,310.70 USD | -0.96 |
| 40 | default | -10,466.78 USD / -21,196.78 USD / -31,926.78 USD | 1,539 | 32.03% | 0.909 | -6.80 USD | 212.96 USD | -110.38 USD | -404.02 USD | 11,614.42 USD | -0.90 |
| 40 | fixed | -17,532.86 USD / -30,812.86 USD / -44,092.86 USD | 1,543 | 21.00% | 0.863 | -11.36 USD | 340.86 USD | -104.98 USD | -404.02 USD | 18,414.82 USD | -0.95 |
| 45 | default | -6,688.94 USD / -17,448.94 USD / -28,208.94 USD | 1,547 | 32.32% | 0.943 | -4.32 USD | 220.18 USD | -111.54 USD | -454.02 USD | 8,432.36 USD | -0.79 |
| 45 | fixed | -13,455.02 USD / -26,765.02 USD / -40,075.02 USD | 1,551 | 21.34% | 0.896 | -8.68 USD | 349.97 USD | -105.98 USD | -454.02 USD | 14,376.58 USD | -0.94 |
| 50 | default | -5,936.98 USD / -16,706.98 USD / -27,476.98 USD | 1,549 | 32.34% | 0.949 | -3.83 USD | 222.49 USD | -112.03 USD | -504.02 USD | 8,392.36 USD | -0.71 |
| 50 | fixed | -12,503.06 USD / -25,823.06 USD / -39,143.06 USD | 1,553 | 21.38% | 0.904 | -8.05 USD | 353.66 USD | -106.40 USD | -504.02 USD | 13,385.02 USD | -0.93 |

**What the cap changes, signal by signal** (against `close / default`, same TP mode = default). *Affected* = original trades whose stop was further than the cap. Net change = capped minus original profit on those signals.

| Cap | Affected trades | Missed winners (not filled) | Avoided losers (not filled) | Loser -> winner | Winner -> loser | Still win / still lose | Net change from missed winners | Net change from avoided losers | Net change, all filled ones | New trades (no original) | Lost unaffected trades (blocked by a capped order) | Net change, total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 196 | 37 | 23 | 8 | 0 | 128 | -26,281.26 USD | +12,192.46 USD | 9,890.00 USD | 1 (-204.02 USD) | 0 (0.00 USD) | -4,402.82 USD |
| 25 | 113 | 30 | 17 | 2 | 0 | 64 | -22,009.40 USD | +9,358.34 USD | 4,940.00 USD | 1 (-254.02 USD) | 0 (0.00 USD) | -7,965.08 USD |
| 30 | 83 | 26 | 10 | 3 | 0 | 44 | -19,665.48 USD | +5,430.20 USD | 5,930.00 USD | 1 (-304.02 USD) | 0 (0.00 USD) | -8,609.30 USD |
| 35 | 66 | 19 | 9 | 1 | 0 | 37 | -14,273.62 USD | +4,936.18 USD | 1,980.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -7,357.44 USD |
| 40 | 51 | 15 | 7 | 1 | 0 | 28 | -11,679.70 USD | +3,958.14 USD | 2,290.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -5,431.56 USD |
| 45 | 39 | 8 | 6 | 1 | 0 | 24 | -7,647.84 USD | +3,494.12 USD | 2,500.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -1,653.72 USD |
| 50 | 29 | 7 | 5 | 1 | 0 | 16 | -6,891.86 USD | +3,480.10 USD | 2,510.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -901.76 USD |

### london (`window=30`, `atr_mult=1.5`, `target=rr2`)

| Cap | TP | Net 0 / 1 / 2 ticks | Trades | % win | PF | Avg trade | Avg win | Avg loss | Largest loss | Max DD | Net / max DD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| close | default | 12,186.22 USD / -143.78 USD / -12,473.78 USD | 1,889 | 35.15% | 1.075 | 6.45 USD | 264.20 USD | -133.26 USD | -1,264.02 USD | 8,059.10 USD | 1.51 |
| close | fixed | 5,074.26 USD / -9,805.74 USD / -24,685.74 USD | 1,887 | 23.48% | 1.028 | 2.69 USD | 424.83 USD | -126.82 USD | -1,264.02 USD | 13,370.94 USD | 0.38 |
| 20 | default | 7,099.38 USD / -4,840.62 USD / -16,780.62 USD | 1,831 | 34.95% | 1.051 | 3.88 USD | 229.40 USD | -117.31 USD | -204.02 USD | 6,589.30 USD | 1.08 |
| 20 | fixed | -2,152.58 USD / -16,612.58 USD / -31,072.58 USD | 1,829 | 23.02% | 0.986 | -1.18 USD | 373.39 USD | -113.17 USD | -204.02 USD | 13,239.48 USD | -0.16 |
| 25 | default | 7,364.86 USD / -4,745.14 USD / -16,855.14 USD | 1,857 | 34.95% | 1.049 | 3.97 USD | 240.77 USD | -123.26 USD | -264.02 USD | 8,079.76 USD | 0.91 |
| 25 | fixed | -2,077.10 USD / -16,737.10 USD / -31,397.10 USD | 1,855 | 23.07% | 0.988 | -1.12 USD | 389.48 USD | -118.27 USD | -264.02 USD | 14,664.46 USD | -0.14 |
| 30 | default | 8,972.60 USD / -3,217.40 USD / -15,407.40 USD | 1,870 | 35.03% | 1.058 | 4.80 USD | 248.21 USD | -126.42 USD | -314.02 USD | 9,657.90 USD | 0.93 |
| 30 | fixed | 480.64 USD / -14,259.36 USD / -28,999.36 USD | 1,868 | 23.23% | 1.003 | 0.26 USD | 400.84 USD | -120.98 USD | -314.02 USD | 15,918.08 USD | 0.03 |
| 35 | default | 8,580.44 USD / -3,679.56 USD / -15,939.56 USD | 1,878 | 35.04% | 1.055 | 4.57 USD | 251.68 USD | -128.71 USD | -364.02 USD | 9,038.00 USD | 0.95 |
| 35 | fixed | 708.48 USD / -14,101.52 USD / -28,911.52 USD | 1,876 | 23.29% | 1.004 | 0.38 USD | 406.44 USD | -122.94 USD | -364.02 USD | 15,196.82 USD | 0.05 |
| 40 | default | 8,944.36 USD / -3,345.64 USD / -15,635.64 USD | 1,882 | 35.02% | 1.056 | 4.75 USD | 255.16 USD | -130.18 USD | -414.02 USD | 8,022.72 USD | 1.11 |
| 40 | fixed | 1,292.40 USD / -13,547.60 USD / -28,387.60 USD | 1,880 | 23.30% | 1.007 | 0.69 USD | 411.82 USD | -124.19 USD | -414.02 USD | 14,082.90 USD | 0.09 |
| 45 | default | 12,478.28 USD / 188.28 USD / -12,101.72 USD | 1,886 | 35.15% | 1.078 | 6.62 USD | 260.32 USD | -130.92 USD | -464.02 USD | 7,609.10 USD | 1.64 |
| 45 | fixed | 4,966.32 USD / -9,873.68 USD / -24,713.68 USD | 1,884 | 23.46% | 1.028 | 2.64 USD | 418.47 USD | -124.82 USD | -464.02 USD | 12,708.28 USD | 0.39 |
| 50 | default | 13,824.26 USD / 1,534.26 USD / -10,755.74 USD | 1,887 | 35.19% | 1.086 | 7.33 USD | 262.73 USD | -131.34 USD | -504.02 USD | 7,849.10 USD | 1.76 |
| 50 | fixed | 6,452.30 USD / -8,387.70 USD / -23,227.70 USD | 1,885 | 23.50% | 1.036 | 3.42 USD | 422.03 USD | -125.18 USD | -504.02 USD | 12,608.28 USD | 0.51 |

**What the cap changes, signal by signal** (against `close / default`, same TP mode = default). *Affected* = original trades whose stop was further than the cap. Net change = capped minus original profit on those signals.

| Cap | Affected trades | Missed winners (not filled) | Avoided losers (not filled) | Loser -> winner | Winner -> loser | Still win / still lose | Net change from missed winners | Net change from avoided losers | Net change, all filled ones | New trades (no original) | Lost unaffected trades (blocked by a capped order) | Net change, total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 255 | 36 | 25 | 12 | 0 | 182 | -26,625.28 USD | +11,870.50 USD | 10,270.00 USD | 3 (-602.06 USD) | 0 (0.00 USD) | -5,086.84 USD |
| 25 | 144 | 19 | 13 | 4 | 0 | 108 | -15,473.62 USD | +7,302.26 USD | 3,350.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -4,821.36 USD |
| 30 | 86 | 13 | 6 | 4 | 0 | 63 | -11,797.74 USD | +3,834.12 USD | 4,750.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -3,213.62 USD |
| 35 | 61 | 8 | 3 | 2 | 0 | 48 | -7,387.84 USD | +2,322.06 USD | 1,460.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -3,605.78 USD |
| 40 | 41 | 5 | 2 | 0 | 0 | 34 | -4,279.90 USD | +1,838.04 USD | -800.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | -3,241.86 USD |
| 45 | 27 | 3 | 0 | 2 | 0 | 22 | -2,167.94 USD | +0.00 USD | 2,460.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | 292.06 USD |
| 50 | 17 | 2 | 0 | 2 | 0 | 13 | -1,031.96 USD | +0.00 USD | 2,670.00 USD | 0 (0.00 USD) | 0 (0.00 USD) | 1,638.04 USD |

### ny (`window=120`, `atr_mult=0.5`, `target=rr2`)

| Cap | TP | Net 0 / 1 / 2 ticks | Trades | % win | PF | Avg trade | Avg win | Avg loss | Largest loss | Max DD | Net / max DD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| close | default | 33,899.76 USD / 2,609.76 USD / -28,680.24 USD | 4,612 | 34.30% | 1.047 | 7.35 USD | 473.37 USD | -235.96 USD | -1,364.02 USD | 34,555.52 USD | 0.98 |
| close | fixed | 36,639.60 USD / 3,829.60 USD / -28,980.40 USD | 4,520 | 30.07% | 1.050 | 8.11 USD | 565.08 USD | -231.35 USD | -1,364.02 USD | 32,109.64 USD | 1.14 |
| 20 | default | -23,233.72 USD / -50,123.72 USD / -77,013.72 USD | 3,986 | 32.81% | 0.948 | -5.83 USD | 325.04 USD | -167.43 USD | -284.02 USD | 35,111.20 USD | -0.66 |
| 20 | fixed | -24,982.12 USD / -53,122.12 USD / -81,262.12 USD | 3,906 | 28.44% | 0.946 | -6.40 USD | 392.30 USD | -164.88 USD | -284.02 USD | 37,872.42 USD | -0.66 |
| 25 | default | -11,895.60 USD / -40,725.60 USD / -69,555.60 USD | 4,280 | 33.34% | 0.978 | -2.78 USD | 367.25 USD | -187.86 USD | -334.02 USD | 35,319.56 USD | -0.34 |
| 25 | fixed | -10,703.90 USD / -40,833.90 USD / -70,963.90 USD | 4,195 | 29.13% | 0.981 | -2.55 USD | 440.52 USD | -184.67 USD | -334.02 USD | 34,979.84 USD | -0.31 |
| 30 | default | 497.78 USD / -29,202.22 USD / -58,902.22 USD | 4,411 | 33.69% | 1.001 | 0.11 USD | 397.49 USD | -201.77 USD | -384.02 USD | 34,456.64 USD | 0.01 |
| 30 | fixed | 1,197.52 USD / -29,872.48 USD / -60,942.48 USD | 4,324 | 29.42% | 1.002 | 0.28 USD | 476.67 USD | -198.27 USD | -384.02 USD | 35,659.82 USD | 0.03 |
| 35 | default | 12,820.10 USD / -17,479.90 USD / -47,779.90 USD | 4,495 | 33.93% | 1.020 | 2.85 USD | 419.53 USD | -211.10 USD | -434.02 USD | 33,973.66 USD | 0.38 |
| 35 | fixed | 14,553.86 USD / -17,176.14 USD / -48,906.14 USD | 4,407 | 29.68% | 1.023 | 3.30 USD | 502.36 USD | -207.34 USD | -434.02 USD | 31,777.78 USD | 0.46 |
| 40 | default | 9,219.50 USD / -21,400.50 USD / -52,020.50 USD | 4,525 | 33.88% | 1.014 | 2.04 USD | 431.21 USD | -217.86 USD | -484.02 USD | 34,839.64 USD | 0.26 |
| 40 | fixed | 12,567.28 USD / -19,512.72 USD / -51,592.72 USD | 4,436 | 29.62% | 1.019 | 2.83 USD | 517.75 USD | -213.89 USD | -484.02 USD | 32,393.76 USD | 0.39 |
| 45 | default | 10,062.92 USD / -20,807.08 USD / -51,677.08 USD | 4,554 | 33.97% | 1.015 | 2.21 USD | 439.52 USD | -222.77 USD | -514.02 USD | 34,863.66 USD | 0.29 |
| 45 | fixed | 13,718.74 USD / -18,611.26 USD / -50,941.26 USD | 4,463 | 29.71% | 1.020 | 3.07 USD | 527.44 USD | -218.57 USD | -514.02 USD | 32,397.78 USD | 0.42 |
| 50 | default | 11,164.58 USD / -19,855.42 USD / -50,875.42 USD | 4,571 | 34.00% | 1.016 | 2.44 USD | 446.17 USD | -226.11 USD | -544.02 USD | 34,717.48 USD | 0.32 |
| 50 | fixed | 13,430.40 USD / -19,079.60 USD / -51,589.60 USD | 4,480 | 29.73% | 1.019 | 3.00 USD | 534.45 USD | -221.87 USD | -544.02 USD | 32,311.60 USD | 0.42 |

**What the cap changes, signal by signal** (against `close / default`, same TP mode = default). *Affected* = original trades whose stop was further than the cap. Net change = capped minus original profit on those signals.

| Cap | Affected trades | Missed winners (not filled) | Avoided losers (not filled) | Loser -> winner | Winner -> loser | Still win / still lose | Net change from missed winners | Net change from avoided losers | Net change, all filled ones | New trades (no original) | Lost unaffected trades (blocked by a capped order) | Net change, total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 2,292 | 419 | 311 | 110 | 0 | 1,452 | -331,915.62 USD | +159,750.22 USD | 114,610.00 USD | 104 (421.92 USD) | 0 (0.00 USD) | -57,133.48 USD |
| 25 | 1,617 | 263 | 152 | 80 | 0 | 1,122 | -236,712.74 USD | +93,381.04 USD | 96,810.00 USD | 83 (726.34 USD) | 0 (0.00 USD) | -45,795.36 USD |
| 30 | 1,094 | 175 | 85 | 57 | 0 | 777 | -173,086.50 USD | +61,301.70 USD | 76,890.00 USD | 59 (1,492.82 USD) | 0 (0.00 USD) | -33,401.98 USD |
| 35 | 754 | 112 | 47 | 39 | 0 | 556 | -125,309.76 USD | +36,688.94 USD | 65,960.00 USD | 42 (1,581.16 USD) | 0 (0.00 USD) | -21,079.66 USD |
| 40 | 507 | 82 | 29 | 25 | 0 | 371 | -97,390.36 USD | +24,436.58 USD | 49,040.00 USD | 24 (-766.48 USD) | 0 (0.00 USD) | -24,680.26 USD |
| 45 | 357 | 57 | 20 | 16 | 0 | 264 | -74,090.86 USD | +16,990.40 USD | 34,280.00 USD | 19 (-1,016.38 USD) | 0 (0.00 USD) | -23,836.84 USD |
| 50 | 257 | 41 | 13 | 11 | 0 | 192 | -56,525.18 USD | +11,422.26 USD | 25,070.00 USD | 13 (-2,702.26 USD) | 0 (0.00 USD) | -22,735.18 USD |
