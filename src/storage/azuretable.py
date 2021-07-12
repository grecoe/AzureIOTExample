import typing
import datetime
from azure.data.tables import TableServiceClient, TableClient
from azure.data.tables._entity import EntityProperty
from azure.data.tables._deserialize import TablesEntityDatetime

class AzureTableStoreUtil:
    CONN_STR = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net"

    def __init__(self, account_name:str, account_key:str):
        self.connection_string = AzureTableStoreUtil.CONN_STR.format(
            account_name,
            account_key
        )

    def search_table(self, table_name:str, start: datetime, end: datetime = None) -> typing.Dict[str, typing.Any]:

        return_records = []
        with self._get_table_client(table_name) as table_client:
            query_filter = AzureTableStoreUtil._get_query_filter(start, end)
    
            results = table_client.query_entities(query_filter)
            for result in results:
                entity_record = {}
                
                for key in result:
                    value = result[key]

                    if isinstance(result[key], EntityProperty): 
                        value = result[key].value
                    if isinstance(result[key], TablesEntityDatetime):
                        value = datetime.datetime.fromisoformat(str(result[key]))

                    entity_record[key] = value
                
                return_records.append(entity_record)
        
        return return_records

    def delete_records(self, table_name:str, records:typing.Tuple[str,str]) -> None:
        """Tuple is (row,partion)"""
        with self._get_table_client(table_name) as table_client:
            for pair in records:
                table_client.delete_entity(
                    row_key=pair[0], 
                    partition_key=pair[1]
                    )

    @staticmethod
    def _get_query_filter(start: datetime, end: datetime) -> str:
        """If no end date we are looking for anything BEFORE start, 
        otherwise get records between times"""
        query_filter = None
        if end is not None:
            query_filter = "EventProcessedUtcTime ge datetime'{}' and EventProcessedUtcTime lt datetime'{}'".format(
                start.isoformat(),
                end.isoformat()
            )
        else:
            query_filter = "EventProcessedUtcTime lt datetime'{}'".format(
                start.isoformat()
            )

        return query_filter

    def _get_table_client(self, table_name: str) ->TableClient:
        return_client = None

        with TableServiceClient.from_connection_string(conn_str=self.connection_string) as table_service:
            name_filter = "TableName eq '{}'".format(table_name)
            queried_tables = table_service.query_tables(name_filter)

            found_tables = []
            for table in queried_tables:
                # Have to do this as its an Item_Paged object
                if table.name == table_name:
                    found_tables.append(table)
                    break 
        
            if found_tables and len(found_tables) == 1:
                return_client = TableClient.from_connection_string(conn_str=self.connection_string, table_name=table_name)
            else:
                raise Exception("Table {} not found".format(table_name))

        return return_client                