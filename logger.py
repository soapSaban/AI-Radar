import serial
import csv
import time

# --- CONFIGURATION ---
PORT = 'COM5'
BAUD = 115200
SAMPLES_TO_COLLECT = 300 # 300 samples at ~10Hz = roughly 30 seconds of data

# Ask the user what we are doing
label = input("Enter the state you are about to record (e.g., coding, gaming, passive): ").strip().upper()
filename = f"{label}_dataset.csv"

print(f"\n[ SYSTEM ARMED ]")
print(f"Prepare to perform: {label}. Recording starts in 5 seconds...")
time.sleep(5)
print(f"\n[ RECORDING INITIATED: Capturing {SAMPLES_TO_COLLECT} frames... ]")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Distance', 'LDR_Left', 'LDR_Right', 'Temp', 'Label'])
        
        count = 0
        while count < SAMPLES_TO_COLLECT:
            line = ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(',')
                if len(parts) == 4:
                    # Write the 4 sensor values PLUS the label to the CSV
                    writer.writerow([parts[0], parts[1], parts[2], parts[3], label])
                    count += 1
                    
                    if count % 50 == 0:
                        print(f"Captured {count} / {SAMPLES_TO_COLLECT} frames...")
                        
    print(f"\n[ HEIST COMPLETE ] Data saved to {filename}")
    
except Exception as e:
    print(f"Error: {e}")