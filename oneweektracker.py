"""
AgMEQ Automated Mass Tracker - one-week mass logger
===================================================

Logs the mass reported by a RADWAG WTC 2000 precision balance (connected to a
Raspberry Pi over USB) every 15 minutes for one week (672 readings), writing
each reading to a CSV file.

This is the script used for the moisture-uptake session described in:
    Looney I, Tabaracci K, Robertson DJ. Indoor storage conditions alter the
    flexural and transverse stiffness of dried maize stalks. (in preparation)

Usage (on the Raspberry Pi):
    python3 oneweektracker.py

Edit the CONFIGURATION block below before running (serial port, file paths,
interval, number of readings). See README.md for full setup instructions.
"""

import serial
import csv
import time
from datetime import datetime
import os
import re
import sys
import shutil
import traceback

# =====================================================
# CONFIGURATION
# =====================================================

# The WTC 2000 enumerates as a USB CDC (virtual serial) device on the Pi.
# Check the actual port with:  ls /dev/ttyACM* /dev/ttyUSB*
SERIAL_PORT = '/dev/ttyACM0'
BAUDRATE = 9600

INTERVAL_SECONDS = 15 * 60          # one reading every 15 minutes
TOTAL_MEASUREMENTS = 7 * 24 * 4     # 672 readings = 7 days

# Primary data file, plus a backup copy on the SD card's boot partition
# (the boot partition is FAT32, so it can be read on any Windows/Mac computer
# by simply removing the SD card - useful if the Pi will not boot).
PRIMARY_FILE = "/home/isaaclooney03/mass_oneweektest_2.csv"
BOOT_FILE = "/boot/firmware/mass_oneweektest_2.csv"
ERROR_LOG_HOME = "/home/isaaclooney03/mass_logger_error.txt"
ERROR_LOG_BOOT = "/boot/firmware/mass_logger_error.txt"

MAX_RETRIES = 3                 # attempts per reading before recording FAIL
SCALE_RESPONSE_WAIT = 0.5       # seconds to wait for the scale to reply


# =====================================================
# ERROR LOGGER
# =====================================================

def log_error(message):
    """Write an error to the home-directory log and copy it to the boot partition."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = (
        "\n========================================\n"
        f"{timestamp}\n"
        f"{message}\n"
        "========================================\n"
    )
    print(text)
    try:
        with open(ERROR_LOG_HOME, 'a') as f:
            f.write(text)
    except Exception:
        pass
    try:
        shutil.copy2(ERROR_LOG_HOME, ERROR_LOG_BOOT)
    except Exception:
        pass


# =====================================================
# STARTUP
# =====================================================

print()
print("========================================")
print("       ONE WEEK MASS LOGGER 2")
print("========================================")
print("Start time:", datetime.now())
print("Measurements:", TOTAL_MEASUREMENTS)
print("Interval:", INTERVAL_SECONDS, "seconds")
print("Primary file:", PRIMARY_FILE)
print("Boot file:", BOOT_FILE)
print("========================================")
print()

# Create the CSV and write the header row (overwrites any existing file)
with open(PRIMARY_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'measurement',
        'elapsed_hours',
        'timestamp',
        'tries',
        'mass_g',
        'raw_response'
    ])

try:
    shutil.copy2(PRIMARY_FILE, BOOT_FILE)
except Exception as e:
    print("Warning: initial boot copy failed")
    print(e)

# Open the serial connection to the scale
try:
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=2)
except Exception as e:
    print("ERROR opening serial port:")
    print(e)
    sys.exit(1)

experiment_start = time.time()


# =====================================================
# MAIN LOOP
# =====================================================

for measurement in range(1, TOTAL_MEASUREMENTS + 1):
    try:
        cycle_start = time.time()
        elapsed_hours = (cycle_start - experiment_start) / 3600.0
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        mass = "NaN"
        response = ""
        tries = "FAIL"

        # ---------------------------------
        # REQUEST A READING (WITH RETRIES)
        # ---------------------------------
        # "SI" is the RADWAG protocol command "send immediate result":
        # the scale returns the current reading whether or not it is stable.
        # The full reply is saved in raw_response so stability can be checked later.

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                ser.reset_input_buffer()
                ser.write(b'SI\r\n')
                ser.flush()
                time.sleep(SCALE_RESPONSE_WAIT)

                response = (
                    ser.read_all()
                    .decode(errors='ignore')
                    .strip()
                )

                # Pull the first number out of the reply (the mass in grams)
                match = re.search(r'([-+]?\d*\.?\d+)', response)
                if match:
                    mass = float(match.group(1))
                    tries = attempt
                    break

            except Exception as e:
                response = str(e)

        # ---------------------------------
        # WRITE TO PRIMARY FILE
        # ---------------------------------
        # flush + fsync forces each row onto the SD card immediately,
        # so a power loss costs at most the current reading.

        with open(PRIMARY_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                measurement,
                round(elapsed_hours, 4),
                timestamp,
                tries,
                mass,
                response
            ])
            f.flush()
            os.fsync(f.fileno())

        # ---------------------------------
        # BACK UP TO BOOT PARTITION EVERY 16 READINGS (4 HOURS)
        # ---------------------------------

        if measurement % 16 == 0 or measurement == TOTAL_MEASUREMENTS:
            try:
                shutil.copy2(PRIMARY_FILE, BOOT_FILE)
                print("Boot backup updated.")
            except Exception as e:
                print("Boot copy failed:", e)

        # ---------------------------------
        # STATUS
        # ---------------------------------

        print(
            f"{measurement:3d}/"
            f"{TOTAL_MEASUREMENTS} | "
            f"{timestamp} | "
            f"tries={tries} | "
            f"mass={mass}"
        )

        # ---------------------------------
        # WAIT UNTIL THE NEXT 15-MINUTE MARK
        # ---------------------------------
        # Sleeps for the interval minus the time already spent this cycle,
        # so readings do not drift later over the week.

        if measurement < TOTAL_MEASUREMENTS:
            elapsed = time.time() - cycle_start
            remaining = INTERVAL_SECONDS - elapsed
            if remaining > 0:
                time.sleep(remaining)

    except Exception:
        # Any unexpected error: log it, then halt WITHOUT shutting down,
        # so the data and error log can be recovered from the Pi.
        error_text = traceback.format_exc()
        log_error(error_text)
        print()
        print("FATAL ERROR")
        print(error_text)
        print()
        print("PROGRAM HALTED")
        print("DO NOT TURN OFF PI")
        while True:
            time.sleep(60)


# =====================================================
# FINISH
# =====================================================

print()
print("========================================")
print("         EXPERIMENT COMPLETE")
print("========================================")

try:
    shutil.copy2(PRIMARY_FILE, BOOT_FILE)
except Exception as e:
    print("Final boot copy failed:", e)

if os.path.exists(PRIMARY_FILE):
    print("Primary file:", os.path.getsize(PRIMARY_FILE), "bytes")
if os.path.exists(BOOT_FILE):
    print("Boot file:", os.path.getsize(BOOT_FILE), "bytes")

print()
print("Shutting down in 5 seconds...")
time.sleep(5)
os.system("sudo poweroff")
