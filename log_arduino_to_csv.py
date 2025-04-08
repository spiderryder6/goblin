import csv
import time

import serial

# === CONFIGURATION ===
COM_PORT = "/dev/ttyACM0"  # ← Change this to your Arduino port
BAUD_RATE = 115200
CSV_FILENAME = "sensor_log_occupancy_up20.csv"

# ======================


def main():
    print(f"Connecting to {COM_PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give time for Arduino to reset

    with open(CSV_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "occupancy", "ambient_light"])  # CSV header

        print("Logging started. Press Ctrl+C to stop.")
        try:
            while True:
                line = ser.readline().decode("utf-8").strip()

                # Skip header if Arduino is repeating it
                if line.lower().startswith("occupancy"):
                    continue

                if "," in line:
                    occupancy, ambient = line.split(",")
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([timestamp, occupancy.strip(), ambient.strip()])
                    print(
                        f"{timestamp} - occupancy: {occupancy.strip()}, ambient: {ambient.strip()}"
                    )

        except KeyboardInterrupt:
            print("\nLogging stopped by user.")
        finally:
            ser.close()


if __name__ == "__main__":
    main()
