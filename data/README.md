# Data

Mass logs from the two tracking sessions reported in the paper. Both sessions were recorded with `oneweektracker.py`, unmodified; only the output filename was changed between runs. Both sessions used the same set of four dried maize stalks, resting together on the balance pan. Between sessions the stalks were stored in the laboratory, then re-conditioned for one week in the conditioning chamber before the moisture loss session began.

| File | Session | Conditions | Dates (2026) | Duration | Readings |
|---|---|---|---|---|---|
| `uptake_session.csv` | Moisture uptake: dried stalks placed in the conditioning chamber | 25 °C, 75% RH (balance and Pi inside the chamber) | Jul 7 – Jul 14 | 168 h | 672 |
| `loss_session.csv` | Moisture loss: the same four stalks, re-conditioned for one week in the same chamber (25 °C, 75% RH), then moved to the lab bench | Ambient laboratory | Aug 3 – Aug 10 | 168 h | 672 |

Both runs completed every reading on the first attempt, with no failed readings and no gaps.

## Columns

| Column | Units | Description |
|---|---|---|
| `measurement` | – | Reading number, starting at 1 |
| `elapsed_hours` | h | Time since the start of the run |
| `timestamp` | local time (Pacific) | Date and time of the reading |
| `tries` | – | Attempts needed to get a valid reading (1–3); `FAIL` if all three failed |
| `mass_g` | g | Combined mass of the four-stalk set (0.01 g readability); `NaN` if the reading failed |
| `raw_response` | – | Unedited reply from the balance |

## Notes

- **Unstable flag.** A `?` in `raw_response` means the balance had not settled when the reading was taken. This happened in 438 of 672 chamber readings, most likely because of air movement from the chamber's circulation, and in 1 of 672 laboratory readings. The unstable readings follow the same smooth curve as the stable ones. Fitting all 672 chamber readings reproduces the paper's time constant (τ = 31.8 h, R² = 0.999).
- **Timestamp format.** The laboratory file had been opened and re-saved in a spreadsheet program, which dropped the seconds from its timestamps (`YYYY-MM-DD HH:MM`). The `elapsed_hours` column is unaffected and is the one to use for analysis.
- **Moisture content.** Moisture content can't be calculated from these files alone, because the oven-dry mass of the stalks is needed for that.

## License

These data are released under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You may reuse them with attribution. Please cite the paper and this repository.
