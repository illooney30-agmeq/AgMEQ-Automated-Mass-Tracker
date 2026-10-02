# AgMEQ Automated Mass Tracker
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23109458.svg)](https://doi.org/10.5281/zenodo.23109458)

A low-cost system that logs the mass of plant samples every 15 minutes, built from a Raspberry Pi and a laboratory precision balance. It was used to track how quickly dried maize stalks gain moisture in a humidity-controlled conditioning chamber and how quickly they lose it once they return to ambient laboratory conditions. In practice, that tells you two things: how long samples need to be conditioned before testing, and how long you have to test them once they leave the chamber.

This repository accompanies the paper:

> Looney I, Tabaracci K, Robertson DJ. *Indoor storage conditions alter the flexural and transverse stiffness of dried maize stalks.* (in preparation)

Department of Mechanical Engineering, University of Idaho, Moscow, ID, USA

---

## Contents

| Path | What it is |
|---|---|
| `oneweektracker.py` | Logging script that ran on the Raspberry Pi |
| `requirements.txt` | Python dependency (`pyserial`) |
| `data/uptake_session.csv` | Moisture uptake session: 168 h in the conditioning chamber (672 readings) |
| `data/loss_session.csv` | Moisture loss session: 168 h under ambient laboratory conditions (672 readings) |
| `data/README.md` | Data dictionary and notes |
| `CITATION.cff` | How to cite this repository |
| `LICENSE` | MIT license for the code; data license in `data/README.md` |

---

## Hardware

| Component | Details |
|---|---|
| Single-board computer | Raspberry Pi 3 Model B (v1.2) |
| Balance | RADWAG WTC 2000 precision balance: 2000 g capacity, 0.01 g readability |
| Scale connection | USB cable, Pi USB-A port to the balance's USB-B port |
| Power | Raspberry Pi power supply (see note below) |
| Setup only | USB keyboard and HDMI monitor, used to start the script |

There is no custom wiring. The balance plugs into the Pi with a standard USB-A to USB-B cable, the kind used for printers. The balance appears on the Pi as a virtual serial port, usually `/dev/ttyACM0`.

```
 ┌──────────────────┐   USB-A ──── USB-B   ┌──────────────────────┐
 │ Raspberry Pi 3 B │─────────────────────▶│ RADWAG WTC 2000      │
 │                  │                      │ (4 stalks on the pan)│
 └──────────────────┘                      └──────────────────────┘
   │ micro-USB power
   │ HDMI monitor + USB keyboard (only needed to start the run)
```

**Power supply lesson learned.** Earlier logging attempts failed, and the cause turned out to be the power source. Use a reliable supply rated for the Pi 3, such as the official 5.1 V / 2.5 A supply. An under-powered Pi can reboot or drop the USB connection partway through a run, and you might not notice until the data is lost. The retry and backup safeguards in the script were added after those failures.

---

## How it works

1. Every 15 minutes, the Pi sends the RADWAG protocol command `SI` ("send immediate result") over the USB serial connection.
2. The balance replies with the current reading, for example `SI ?   1234.56 g`. The script takes the number out of the reply and records it.
3. If no valid reply arrives, the script tries again, up to 3 times. If all three attempts fail, it records `NaN` and `FAIL` and moves on, so one missed reading doesn't stop the run.
4. Each reading is forced onto the SD card the moment it's taken. A power cut therefore loses at most one reading.
5. Every 16 readings (4 hours), the data file is copied to the SD card's boot partition. That partition can be read on any Windows or Mac computer, so the data is recoverable even if the Pi won't start.
6. The script schedules each reading 15 minutes after the *start* of the previous one, so the timing doesn't drift over a week.
7. After 672 readings (7 days), the script makes a final backup and shuts the Pi down.
8. If an unexpected error occurs, the script writes it to `mass_logger_error.txt`, prints `PROGRAM HALTED – DO NOT TURN OFF PI`, and waits. It deliberately does *not* shut down, so the data and the error can be recovered.

---

## Setup and use

### 1. Prepare the Pi

Install Raspberry Pi OS. The script expects the boot partition at `/boot/firmware`, which is where Raspberry Pi OS Bookworm and later put it. Then install the one dependency:

```bash
sudo apt install python3-serial
# or: pip install -r requirements.txt
```

### 2. Connect the balance

Plug the balance into the Pi with the USB cable, turn the balance on, and confirm the Pi can see it:

```bash
ls /dev/ttyACM* /dev/ttyUSB*
```

If the port isn't `/dev/ttyACM0`, change `SERIAL_PORT` in the script. If you get a "permission denied" error, add your user to the `dialout` group with `sudo usermod -aG dialout $USER`, then log out and back in.

### 3. Configure the script

Edit the `CONFIGURATION` block at the top of `oneweektracker.py`:

- `PRIMARY_FILE`, `ERROR_LOG_HOME`: change `/home/isaaclooney03/` to your own home directory.
- `PRIMARY_FILE`, `BOOT_FILE`: give each run a new filename. **The script overwrites an existing file with the same name.**
- `INTERVAL_SECONDS`, `TOTAL_MEASUREMENTS`: change these for a different logging interval or run length.

### 4. Start a run

1. Place the samples on the balance and let the reading settle.
2. Start the script from a terminal:
   ```bash
   python3 oneweektracker.py
   ```
3. Confirm the first status line shows a sensible mass, for example `  1/672 | 2026-... | tries=1 | mass=...`.
4. The keyboard and monitor can stay connected or be unplugged. The run continues either way.

If you close the terminal, the run stops. To be able to disconnect safely, start the script inside `tmux` or with `nohup python3 oneweektracker.py &`.

### 5. Retrieve the data

Copy the CSV from the home directory, or pull the SD card and open the backup copy on the boot partition from any computer.

---

## Notes and limitations

- **Unstable readings.** `SI` returns the reading even if the balance hasn't settled. RADWAG marks unstable readings with a `?` in the reply, and the full reply is saved in the `raw_response` column, so unstable readings can be identified or excluded afterward. With stationary samples in a closed chamber, readings change slowly, but airflow from a chamber fan can add noise.
- **Balance in the chamber.** In the uptake session, the balance and the Pi sat inside the conditioning chamber at 25 °C and 75% relative humidity. Check that your balance's rated operating conditions cover your chamber settings.
- **Proof of concept.** This system was built as a proof of concept to show that automated mass tracking is practical for conditioning plant samples. It was not designed as a finished instrument.

---

## Citation

If you use this code or data, please cite the paper above and this repository. The repository citation details are in `CITATION.cff`, and GitHub's "Cite this repository" button reads them.

## License

Code: MIT (see `LICENSE`). Data: CC BY 4.0 (see `data/README.md`).

## Contact

Isaac Looney: loon1344@vandals.uidaho.edu
Daniel J. Robertson (corresponding author): danieljr@uidaho.edu
