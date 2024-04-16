import time
import serial.tools.list_ports
from serial import Serial
from volt.constants import *
from volt.db import db
from volt.utils import try_int

def process_data(data: str):
    topic, payload = data.split(":")

    topic = topic.lower().strip()
    payload = payload.strip()

    if topic == "cells":
        measurements = payload.split(",")
        measurements.pop()

        print(measurements)

        # Create data dictionary.
        data = {}
        for i, voltage in enumerate(measurements):
            data[i+1] = voltage

        # Add data to measurements stream.
        db.xadd("measurements", data)


if __name__ == "__main__":
    pubsub = db.pubsub()
    
    # Subscribe to the action channel. This is used to automatically
    # determine when the Arduino should be reconfigured.
    pubsub.subscribe("action")

    while True:
        print("Scanning for serial ports...")
 
        all_ports = serial.tools.list_ports.comports()
        
        # We only care about ports from relevant vendors.
        valid_ports = list(filter(lambda p: (p.vid in USB_VIDS), all_ports))
        
        for port in valid_ports:
            print("{}: {} [{}]".format(port.device, port.description, port.hwid))

        # Connect if a valid port was found.
        if len(valid_ports) > 0:
            port = valid_ports[0]
            print(f"Connecting to {port.device}...")

            with Serial(port.device, 9600, timeout=0.5) as connection:
                print("Connected!")
                time.sleep(2)

                print("Reading configuration from database...")
                config = db.hgetall("config")
                
                # Redis stores everything as strings, so we must convert.
                total_cells = try_int(config.get("total_cells"))
                poll_interval = try_int(config.get("poll_interval_ms"))
                test_mode = config.get("test_mode") == "true"

                # Calculate flags byte (currently only used for test mode).
                flags = 0x00

                if test_mode:
                    flags |= 0x01
                
                # Convert poll interval from milliseconds to seconds.
                if poll_interval is not None:
                    poll_interval /= 1000

                # Log config info
                print("Loaded configuration:")
                print(f"- Total Cells: {total_cells}")
                print(f"- Poll Interval: {poll_interval} seconds")
                print(f"- Test Mode: {test_mode}")

                # Send configuration command
                if total_cells is not None:
                    connection.write(bytearray([0, total_cells, flags]))

                last_poll_time = 0

                while True:
                    # Process action messages.
                    msg = pubsub.get_message()
                    if msg and msg.get("type") == "message" and msg.get("data") == "reconfigure":
                        # Disconnect from serial port.
                        break
                    
                    # Read incoming serial data.
                    while connection.in_waiting > 0:
                        data = connection.readline()
                        if data:
                            data = data.decode().strip()
                            print(f"Received Data: \"{data}\"")
                            process_data(data)
        
                    now = time.time()
                    
                    if poll_interval is not None and now - last_poll_time >= poll_interval:
                        print("Polling...")
                        connection.write(bytearray([1]))
                        last_poll_time = now

            print("Disconnected!")
        else:
            print("No serial ports found")

        time.sleep(2)