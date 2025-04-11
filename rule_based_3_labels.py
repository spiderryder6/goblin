import csv
import datetime
import time

import serial

# === CONFIGURATION ===
COM_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
DESIRED_LUX = 50
SAMPLING_INTERVAL = 0.5  # seconds (for high-frequency data)

# Generate timestamped filename
start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILENAME = f"data/collection_log_{start_time}.csv"


def compute_label(occupancy, ambient):
    if occupancy == 0:
        return "unoccupied_off"
    elif 40 <= ambient <= 60:
        return "occupied_ok"
    elif ambient < 40:
        return "increase_light"
    elif ambient > 60:
        return "decrease_light"


def main():
    print(f"Connecting to {COM_PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    with open(CSV_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "occupancy", "ambient_light", "label"])

        print("\n[+] Logging started — press Ctrl+C to stop.\n")

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
                        f"{timestamp} - occ: {occupancy}, amb: {ambient}, label: {label}"
                    )

                time.sleep(SAMPLING_INTERVAL)

        except KeyboardInterrupt:
            print("\n[!] Logging stopped.")
        finally:
            ser.close()
            print(f"[✔] Data saved to {CSV_FILENAME}")


if __name__ == "__main__":
    main()
