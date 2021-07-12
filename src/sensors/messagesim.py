
import typing


class MessageSimulator:

    @staticmethod
    def generate_messages(device_ids:typing.List[str], message_count: int) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
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
