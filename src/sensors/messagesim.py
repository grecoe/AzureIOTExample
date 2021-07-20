
import typing


class MessageSimulator:

    @staticmethod
    def generate_messages(device_ids:typing.List[str], message_count: int) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        """Generate a group of dummy messages for the IOT hub ingestion
        as it turns out, data will likely come through a proxy instead.
        
        Parameters:
        device_ids - List of device ids (not connection strings)
        message_count - How many messages to generate


        Format
        {
            "uid" : device_id,
            "batch_size" : messages in payload,
            "triggered" : Used by processing function, every 3rd message
            triggers a call back to the device.
        }
        """
        return_batch = {}
        curr = 0
        while curr < message_count:
            for device_id in device_ids:
                if device_id not in return_batch:
                    return_batch[device_id] = []

                curr += 1
                return_batch[device_id].append({   
                    "uid":device_id,
                    "batch_size":message_count,
                    "triggered": (curr % 3) == 0
                })

        return return_batch        
