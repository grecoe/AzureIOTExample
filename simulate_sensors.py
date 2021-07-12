"""
File to simulate devices sending messages to the IOT Hub.

Messages are basic and defined in src.sensors.messagesim.MessageSimulator
and contain a very small set of information, primarily

- device_id
- batch_size
- triggered (some arbitrary bool indicating which ones to send notifications back
to the device)

Run this code to add messages to the hub, through stream analytics and into 
table storage.

INSTRUCTIONS:
- conda env create -f environment.yml
- conda activate IOTEnv
- python simulate_sensors.py

"""
import time
import asyncio
from src.utils.configuration import Configuration
from src.utils.iothubutil import IOTDeviceUtil
from src.sensors.messagesim import MessageSimulator

async def main(): 
    configuration = Configuration.load_configuration("./settings.json")
    deviceutil = IOTDeviceUtil(configuration.simulation.devices)

    # Create devices
    await deviceutil.create_clients()

    # Generate simulated messages
    simulated_messages = MessageSimulator.generate_messages(
        list(deviceutil.devices.keys()),
        configuration.simulation.message_count
    )

    print("Beginnning simulation....")
    current_count = 0
    for device_id in simulated_messages:
        for message in simulated_messages[device_id]:
            await deviceutil.send_message_from_device(
                device_id,  
                message
            )
            current_count += 1
            print("Message {} sent...".format(current_count))
            # Sleep some predetermined time between messages
            time.sleep(configuration.simulation.delay_min)

    print("Ending simulation....")
  
    # Shut down devices
    await deviceutil.shutdown_clients()


if __name__ == "__main__":
    asyncio.run(main())