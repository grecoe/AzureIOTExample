import datetime

class ProcessEntry:
    def __init__(self, table_name:str, partition_key:str):
        self.table_name = table_name
        self.RowKey = datetime.datetime.utcnow().isoformat()
        self.PartitionKey = partition_key

    def get_entity(self):
        entity = {}
        for prop in self.__dict__:
            if prop != 'table_name':
                entity[prop] = self.__dict__[prop]

        return entity