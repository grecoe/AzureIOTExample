import json
import typing
# For sending message to IOTHub (IOTDeviceUtil)
from azure.iot.device.aio import IoTHubDeviceClient
# For sending messages to device (IOTHubUtil)
from azure.iot.hub import IoTHubRegistryManager

class IOTHubUtil:
    def __init__(self, hub_connection_string:str):
        self.hub_connection = hub_connection_string
        self.registry_manager = IoTHubRegistryManager(self.hub_connection)

    def get_device(self, device_id:str):
        return self.registry_manager.get_device(device_id)

    def send_device_message(self, device_id:str,  payload:str, props: dict):
        # Call the direct method.
        # To monitor that this is working you can use this:
        #  https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-visual-studio-cloud-device-messaging

        return_payload = None
        try:
            response = self.registry_manager.send_c2d_message(device_id, payload, props)
            return_payload = response
        except Exception as ex:
            print(str(ex))

        return return_payload


class IOTDeviceUtil:
    def __init__(self, device_connections: typing.List[str]):
        self.devices = {}
        self.connections = device_connections

    async def create_clients(self) -> None:
        for device_conn in self.connections:
            dev_name = IOTDeviceUtil.get_device_id_from_conn(device_conn)
            client = IoTHubDeviceClient.create_from_connection_string(device_conn)
            await client.connect()
            self.devices[dev_name] = client

    """
    async def send_message(self, device_selector:int, message_details: dict) -> None:
        if len(self.devices) == 0:
            raise Exception("Call create_clients first")
        
        device = self.devices[device_selector % len(self.devices)]
        await device.send_message(json.dumps(message_details))
    """

    async def send_message_from_device(self, device_name:str, message_details: dict) -> None:
        if len(self.devices) == 0:
            raise Exception("Call create_clients first")
        
        if device_name not in self.devices:
            raise Exception("Device {} not recognized".format(device_name))

        device = self.devices[device_name]
        await device.send_message(json.dumps(message_details))

    async def shutdown_clients(self) -> None:
        for device in self.devices:
            await self.devices[device].shutdown()

    @staticmethod
    def get_device_id_from_conn(conn_str:str):
        idx = conn_str.index("DeviceId")
        sub_str = conn_str[idx:] 
        idx = sub_str.index(';')
        sub_str = sub_str[0:idx]
        idx = sub_str.index('=')
        sub_str = sub_str[idx+1:]

        return sub_str