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

SERIAL_PORT = '/dev/ttyACM0' 
BAUDRATE = 9600 

INTERVAL_SECONDS = 15 * 60 
TOTAL_MEASUREMENTS = 7 * 24 * 4 # 672 
PRIMARY_FILE = "/home/isaaclooney03/mass_oneweektest_2.csv" 
BOOT_FILE = "/boot/firmware/mass_oneweektest_2.csv" 
ERROR_LOG_HOME = "/home/isaaclooney03/mass_logger_error.txt" 
ERROR_LOG_BOOT = "/boot/firmware/mass_logger_error.txt" 
MAX_RETRIES = 3 
SCALE_RESPONSE_WAIT = 0.5 

# ===================================================== 
# ERROR LOGGER 
# ===================================================== 

def log_error(message): 
timestamp = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ) 
text = ( "\n========================================\n" f"{timestamp}\n" f"{message}\n" "========================================\n" ) 
print(text) 
try: with open(ERROR_LOG_HOME, 'a') as f: f.write(text) 
except: pass 
try: shutil.copy2( ERROR_LOG_HOME, ERROR_LOG_BOOT ) 
except: pass 

# ===================================================== 
# STARTUP 
# ===================================================== 

print() 
print("========================================") 
print(" ONE WEEK MASS LOGGER 2") 
print("========================================") 
print("Start time:", datetime.now()) 
print("Measurements:", TOTAL_MEASUREMENTS) 
print("Interval:", INTERVAL_SECONDS, "seconds") 
print("Primary file:", PRIMARY_FILE) 
print("Boot file:", BOOT_FILE) 
print("========================================") 
print() 
with open(PRIMARY_FILE, 'w', newline='') as f: writer = csv.writer(f) writer.writerow([ 'measurement', 'elapsed_hours', 'timestamp', 'tries', 'mass_g', 'raw_response' ]) 

try: shutil.copy2( PRIMARY_FILE, BOOT_FILE ) 
except Exception as e: print( "Warning: initial boot copy failed" ) 
print(e) 

try: ser = serial.Serial( SERIAL_PORT, baudrate=BAUDRATE, timeout=2 ) 
except Exception as e: print( "ERROR opening serial port:" ) 
print(e) 
sys.exit(1) 

experiment_start = time.time() 

# ===================================================== 
# MAIN LOOP 
# ===================================================== 

for measurement in range( 1, TOTAL_MEASUREMENTS + 1):
try: cycle_start = time.time() 
elapsed_hours = ( cycle_start - experiment_start ) / 3600.0 
timestamp = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ) 
mass = "NaN" response = "" tries = "FAIL" 

# --------------------------------- 
# RETRIES 
# --------------------------------- 

for attempt in range( 1, MAX_RETRIES + 1): 
try: ser.reset_input_buffer() 
ser.write(b'SI\r\n') 
ser.flush() 
time.sleep( SCALE_RESPONSE_WAIT ) 

response = ( ser.read_all() .decode( errors='ignore' ) .strip() ) 
match = re.search( r'([-+]?\d*\.?\d+)', response ) 
if match: mass = float( match.group(1) ) 
tries = attempt 
break 

except Exception as e: response = str(e) 

# --------------------------------- 
# WRITE TO PRIMARY 
# --------------------------------- 

with open( PRIMARY_FILE, 'a', newline='' ) 
as f: writer = csv.writer(f) 
writer.writerow([ measurement, round( elapsed_hours, 4 ),timestamp, tries, mass, response ])
f.flush() 
os.fsync( f.fileno() ) 

# --------------------------------- 
# COPY EVERY 16 MEASUREMENTS 
# --------------------------------- 

if ( measurement % 16 == 0 or measurement == TOTAL_MEASUREMENTS ): 
try: shutil.copy2( PRIMARY_FILE, BOOT_FILE ) 
print( "Boot backup updated." ) 
except Exception as e: print( "Boot copy failed:", e ) 

# --------------------------------- 
# STATUS 
# --------------------------------- 

print( f"{measurement:3d}/" f"{TOTAL_MEASUREMENTS} | " f"{timestamp} | " f"tries={tries} | " f"mass={mass}" ) 

# --------------------------------- 
# WAIT 
# --------------------------------- 

if ( measurement < TOTAL_MEASUREMENTS ): 
elapsed = ( time.time() - cycle_start ) 
remaining = ( INTERVAL_SECONDS - elapsed ) 
if remaining > 0: time.sleep( remaining ) 
except Exception: error_text = ( traceback .format_exc() ) log_error( error_text ) print() print( "FATAL ERROR" ) print( error_text ) print() print( "PROGRAM HALTED" ) print( "DO NOT TURN OFF PI" ) 
while True: time.sleep(60) 

# ===================================================== 
# FINISH 
# ===================================================== 

print() print( "========================================" ) 
print( "EXPERIMENT COMPLETE" ) 
print( "========================================" ) 
try: shutil.copy2( PRIMARY_FILE, BOOT_FILE ) 
except Exception as e: print( "Final boot copy failed:", e ) 
if os.path.exists( PRIMARY_FILE): print( "Primary file:", os.path.getsize( PRIMARY_FILE ), "bytes" ) 
if os.path.exists( BOOT_FILE): print( "Boot file:", os.path.getsize( BOOT_FILE ), "bytes" ) 
print() 
print( "Shutting down " "in 5 seconds..." ) 
time.sleep(5) 
os.system( "sudo poweroff" )
















































































