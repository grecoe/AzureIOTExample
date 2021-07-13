import datetime
from src.storage.azuretable import AzureTableStoreUtil
from src.utils.configuration import Configuration
from src.utils.iothubutil import IOTHubUtil

def mock_function():
    # Configuration has settings about account/table
    configuration = Configuration.load_configuration("./settings.json")

    # Process log record
    process_info = {}

    # Create the table util
    table_store_utility = AzureTableStoreUtil(
        configuration.table_store.account_name,
        configuration.table_store.account_key
    )


    # Set scan and cache cutoff window
    end_time = datetime.datetime.utcnow()
    start_delta = datetime.timedelta(seconds=configuration.simulation.search_seconds)
    start_time = end_time - start_delta
    cache_delta = datetime.timedelta(seconds=configuration.simulation.cache_life_seconds)
    cache_cutoff = end_time - cache_delta

    # For the log
    process_info["scanStart"] = start_time.isoformat()
    process_info["scanEnd"] = end_time.isoformat()
    process_info["notifiedDevices"] = []
    process_info["cacheCutoff"] = cache_cutoff.isoformat()

    ###########################################################################
    # Search the table for records in our specified search window to process
    ###########################################################################
    records = table_store_utility.search_table(
                configuration.table_store.table_name,
                start_time,
                end_time
                )

    process_info["recordsInScan"] = len(records)

    print("Process {} records in window {} to {}".format(
        len(records),
        start_time.isoformat(),
        end_time.isoformat()
    ))

    # Perform work on the records here in whatever way makes sense for you
    # complete with notifications back to the device.
    if len(records) > 0:
        hubUtil = IOTHubUtil(configuration.simulation.hubconnection)
        for record in records:
            if record["triggered"]:
                print("Notify ", record['uid'])
                if record['uid'] not in process_info["notifiedDevices"]:
                    process_info["notifiedDevices"].append(record['uid'])

                hubUtil.send_device_message(
                    record['uid'],
                    "From simulate_serverless.py", 
                    {"simulation" : True}
                )

    ###########################################################################
    # Clean up the storage table as we only need a subset of information there.
    ###########################################################################
    aged_records = table_store_utility.search_table(
        configuration.table_store.table_name,
        cache_cutoff
        )

    # Report how many records are going to be deleted
    process_info["clearedRecordCount"] = len(aged_records)

    # With the list before a certain time, we can batch delete them
    # to keep the table clean....
    delete_tuples = []
    for record in aged_records:
        delete_tuples.append((record["RowKey"],record["PartitionKey"]))

    print("Delete {} aged records older than {}".format(
        len(delete_tuples),
        cache_cutoff.isoformat()
        ))

    table_store_utility.delete_records(
        configuration.table_store.table_name,
        delete_tuples
    )

    ###########################################################################
    # Now add a processing log to another table
    ###########################################################################
    process_info["notifiedDevices"].append("another for test")
    process_info["notifiedDevices"] = ",".join(process_info["notifiedDevices"])
    table_store_utility.add_record(
        configuration.table_store.log_table,
        datetime.datetime.utcnow().isoformat(),
        configuration.table_store.log_partition,
        process_info
    )



if __name__ == "__main__":
    mock_function()