import csv
import datetime
import time

import serial

# === CONFIGURATION ===
COM_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILENAME = f"data/adjustment_labels_{start_time}.csv"
DESIRED_LUX = 50


def compute_label(occupancy, ambient):
    if occupancy == 0:
        return "unoccupied_off"

    # Compute adjustment needed
    diff = DESIRED_LUX - ambient
    percent_change = int((abs(diff) / DESIRED_LUX) * 100)

    if diff > 5:
        return f"occupied_up{min(percent_change, 100)}%"
    elif diff < -5:
        return f"occupied_down{min(percent_change, 100)}%"
    else:
        return "occupied_ok"


def main():
    print(f"Connecting to {COM_PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    with open(CSV_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "occupancy", "ambient_light", "label"])

        print("\nLogging started. Press Ctrl+C to stop.\n")

        try:
            while True:
                line = ser.readline().decode("utf-8").strip()

                if line.lower().startswith("occupancy") or not line:
                    continue

                if "," in line:
                    occ, amb = line.split(",")
                    occupancy = int(occ.strip())
                    ambient = int(amb.strip())
                    label = compute_label(occupancy, ambient)
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                    writer.writerow([timestamp, occupancy, ambient, label])
                    print(
                        f"{timestamp} - occ: {occupancy} | light: {ambient} | label: {label}"
                    )

        except KeyboardInterrupt:
            print("\n[!] Logging stopped.")
        finally:
            ser.close()
            print("[✔] Serial closed, data saved.")


if __name__ == "__main__":
    main()
