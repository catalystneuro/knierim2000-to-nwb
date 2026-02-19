# McNaughton Neurolab NWB Conversion Notes

## Dataset
- **Publication**: Knierim, McNaughton & Poe (2000) "Three-dimensional spatial selectivity of hippocampal neurons during space flight." *Nature Neuroscience* 3(3):209-212. DOI: 10.1038/72910
- **Mission**: Neurolab STS-90 Space Shuttle mission, April–May 1998
- **Source data**: NASA OSDR legacy dataset, originally in Xclust .CEL spike files and binary .RMA rate maps

## Subjects
- 3 rats (Fischer 344, adult males) with tetrode arrays in hippocampal area CA1
- Rat 1 ↔ PREFLI~1, FD4RAT1, FD9RAT1
- Rat 2 ↔ PREFLI~2, FD4RAT2, FD9RAT2
- Rat 3 ↔ PREFLI~3, FD4RAT3 (no FD9 — technical issues)

## Recording Sessions
| Subject | Date | Time | Context |
|---------|------|------|---------|
| PREFLI~2 | 1998-04-13 | 16:37 UTC | Preflight, Rat 2 |
| PREFLI~1 | 1998-04-14 | 12:53 UTC | Preflight, Rat 1 |
| PREFLI~3 | 1998-04-14 | 13:49 UTC | Preflight, Rat 3 |
| FD4RAT1+2 | 1998-04-20 | 09:57 UTC | Flight Day 4, Rats 1+2 simultaneous |
| FD4RAT3 | 1998-04-20 | 15:28 UTC | Flight Day 4, Rat 3 separate |
| FD9RAT1+2 | 1998-04-25 | 12:45 UTC | Flight Day 9, Rats 1+2 simultaneous |

## Data Structure

### CEL Files (Raw Sorted Spikes)
- ASCII format from Xclust spike sorting software
- Fields: id, t_px, t_py, t_pa, t_pb (spike waveform peak amplitudes on 4 channels), t_mx, t_my, t_ma, t_mb (integrated waveform areas), t_maxwd, t_maxht (waveform shape), time (seconds), pos_x, pos_y (pixels), head_dir
- **Time units are SECONDS** (not 10µs ticks as the original ChatGPT script assumed)
- Position data (pos_x, pos_y) available in flight sessions only; missing in preflight
- head_dir is always -50 (sentinel for "no data") — not stored in NWB
- Each file represents one sorted cluster from one task epoch on one tetrode

### RMA Files (Rate Maps)
- Binary format: 32,768 bytes
- First 4096 float32 big-endian → 64×64 firing rate map (Hz)
- Next 4096 int32 big-endian → 64×64 occupancy map (counts)
- CELL~N.RMA files are per-cell maps linked to specific clusters
- Other .RMA files are session/tetrode-level analysis products

### Session Types
- **BL**: Baseline — rectangular flat track
- **ES**: Escher Staircase — 3D track with 90° yaw/pitch turns
- **MC**: Magic Carpet — flat 2D track

## NWB File Structure (per subject-session)
- **Units table**: spike_times (seconds), tetrode, cluster_id, session_type, source_file, electrodes
- **Epochs**: TimeIntervals with start/end times and session_type for BL/ES/MC periods
- **Position**: SpatialSeries (pos_x, pos_y in pixels) — flight sessions only
- **Rate maps**: DynamicTable in processing/ecephys with 64×64 rate_map and occupancy_map columns

## Issues Found in Original (ChatGPT-generated) NWB Files
1. **Time units wrong**: multiplied by 1e-5 when times were already in seconds
2. **No position data**: pos_x/pos_y columns were discarded
3. **No epochs**: task periods not marked
4. **Placeholder dates**: used 2001-01-01 instead of actual 1998 dates
5. **Rate maps as TimeSeries**: misused TimeSeries with fake timestamps
6. **Missing metadata**: no species, strain, experimenter, DOI, experiment description
7. **No electrode groups**: tetrodes not properly modeled

## Open Questions
- Exact age of rats at time of recording (currently set to unknown)
- Coordinate system for position tracking (pixel coordinates, exact camera resolution unknown)
- Whether Rat 1↔PREFLI~1 mapping is correct (tetrode numbering differs between preflight and flight for Rat 2)
