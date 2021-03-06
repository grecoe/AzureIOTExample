# AzureIOTExample

This repo creates an example on how to use Azure IOT Hub to recieve and send messages to an IOT device in a generic way and without tying all the loose ends up.

### Scenario
The solution has multiple IOT devices spread across a geographic region, or perhaps within a single factory.

The devices all report status through an Azure IOT Hub. Attached to the IOT hub is an Azure Stream Analytics job which branches that incoming sensor data to two storage services:

- Azure Cosmos DB for long term storage 
- Azure Table Storage for temporary storage

Periodically the temporary storage is processed for:

- Determine if a certain state has been reached, and if so, send a control message back to the reorting IOT device.
- Maintain the temorary storage as it just needs enough data to process.  

> This example solution does not include the connection of a Cosmos DB to the solution for cost reasons. Pushing data with an Azure Stream Analytics job to cosmos is a trivial task. 

> This example solution does not implement the timer triggered Azure Function to process the temporary storage. This functionality is provided through a Python script included in this directory. Wrapping this to an Azure Function is also a relatively trivial task. 

### Prerequisites
To succesfully use this sample you must 

- Have an Azure Subscription
- Have the ability to create resources in that subscription.
- Have [conda/python](https://docs.conda.io/en/latest/miniconda.html) installed on your system (or Virtual Machine if you so choose). 
- Have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed on your system. 

## Contents
- [Architecture Overview](#architecture-overview)
- [Step 1 - Set up Services](#step-1---set-up-services)
    - [Step 1.1 - Stream Analytics job](#step-11---configure-stream-analytics-job)
    - [Step 1.2 - Create Devices](#step-12---create-iot-devices)
- [Step 2 Collect Settings](#step-2---fill-in-settingsjson-settings)
- [Step 3 Run Scripts](#step-3---run-scripts)


## Architecture Overview
![](images/BasicArchitecture.JPG?raw=true)

In this example the flow of data is shown in the above message

|Step|Description|
|----|----|
|1|An IOT Sensor/Device sends messages to the IOT Hub|
|2|A Stream Analytics Job detects incoming IOT Hub messages and branches them to two different storage solutions:<br><br><b>1.</b> (Not implemented in this sample) Dump all raw data to Cosmos DB<br><b>2.</b> Stream out raw data to an Azure Storage Table|
|3|A serverless function (Azure Function):<br><br><b>1.</b> Reads the table storage<br><b>2.</b> Determines if a notification to the device is warranted.<br><b>3</b>. Sends a message back to the device through the IOT Hub.<br><b>4</b>. Performs maintenance (deletes) on storage table (as all data will be in Cosmos)<br><br>NOTE: This is not implemented as an actual function in this example but as Python code you run locally (simulate_serverless.py)|

> <b>NOTE:</b> This example does not take into account Network Isolation or other security best practices. 

[Top of article](#azureiotexample)

## Step 1 - Set up services
While it is completely possible to set up the following resources using Azure ARM templates, this example is set up manually. 

> <b>NOTE::</b> The following instructions assume you are logged in to the (Azure Portal)[https://portal.azure.com] and that you are working with a specific subscription in the portal.

|Service|Instructions|
|----|----|
|Azure Resource Group|- Click on Resource Groups in the Subscription Blade.<br>- Click Create at the top of the blade.<br>- Select a name and region and note those down.|
|REMAINING|For the next three services:<br><br>- Click on the resource group created above.<br>- At the top of the resource group blade, click create.|
|Azure IOT Hub|- In the search enter <b>IOT Hub</b> and select IOT Hub from the options.<br>- Click create, ensure it's going to the resource group above in the same region then accept all defaults.| 
|Azure Storage Account|- In the search enter <b>Storage Account</b> and select Storage account from the options.<br>- Click create, ensure it's going to the resource group above in the same region then accept all defaults.| 
|Azure Stream Ananlytics Job|- In the search enter <b>Stream Ananlytics job</b> and select Stream Ananlytics job from the options.<br>- Click create, ensure it's going to the resource group above in the same region then accept all defaults.| 

[Top of article](#azureiotexample)

### Step 1.1 - Configure Stream Analytics job

The Stream Analytics job must be configured and started so that when messages arrive at the Event Hub they can be moved to the Table Storage. 

In the Resource group blade, click on the Stream Analytics job resource. 

- Under Job Topology click on Inputs
    - Click on Add Stream input
    - Choose IOT Hub
    - Choose Select IOT Hub from your subscription and then choose the IOT hub you created above.
    - Name should be <b>hubqueryinput</b>
    - Accept other defaults and click Save.
- Under Job Topology click on Outputs
    - Click on Add 
    - Choose Table Storage
    - Choose Select Table storage from your subscriptions and then choose the storage account created above.
    - Name should be <b>hubqueryouttable</b>
    - Under Table Name enter <b>streamoutput</b>
    - In Partition key enter <b>uid</b>
    - In Row key enter <b>EventProcessedUtcTime</b>
    - Click Save 
- Under Job Topoloty click on Query and enter the following and click Save Query:
```
SELECT
    *
INTO
    hubqueryouttable
FROM
    hubqueryinput
```
- Go to Overview in the main menu for the Stream Analytics job and click Start

[Top of article](#azureiotexample)

### Step 1.2 - Create IOT Device(s)

Now that we have the services up, you will need to [generate an IOT device](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-python-python-device-management-get-started#register-a-new-device-in-the-iot-hub). 

This can be done through the Azure Portal or via the Azure CLI. Here is an example (from the page above) to accomplish this from the command line:
```
az extension add --name azure-iot
az account set -s [YOUR_SUBSCRIPION_ID]
[For the number of devices you want to create on the IOT Hub]
az iot hub device-identity create --device-id myDeviceId --hub-name {Your IoT Hub name}
[NOTE Change in command from page listing above]
az iot hub device-identity connection-string show --device-id myDeviceId --hub-name {Your IoT Hub name} -o table
```

[Top of article](#azureiotexample)

## Step 2 - Fill in settings.json settings

To succefully run the scripts you need to fill in some details in the <b>settings.json</b> file located in the root of this repo. 

|Setting|Value|
|----|----|
|simulation.hubconnection|Get the Service connection string to the IOT Hub<br><br>> az iot hub connection-string show --all --hub-name {Your IoT Hub name}<br><br>Find the entry that contains <b>SharedAccessKeyName=service</b> and copy the full connection string to the setting simulation.hubconnection|
|simulation.devices|This is a list of all of the connection strings for the devices that are being simulated. You need at least one of these.<br><br>For each device, run the following command and copy the connection string as an entry to the simulation.devices list:<br><br>> az iot hub device-identity connection-string show --device-id myDeviceId --hub-name {Your IoT Hub name} -o table|
|table_store.account_name|The name of the storage account created above.|
|table_store.account_key|The primary key for the storage account created above.<br><br>> az storage account keys list --account-name {Your storage account name}<br><br>From the output, copy key1.value into the setting  table_store.account_key|
|table_store.table_name|This is the table name in the above storage account where the Stream Analytics job is recording IOT events. If you left the name as requested above, you will not need to change this value.|

[Top of article](#azureiotexample)

## Step 3 - Run Scripts

To run the scripts you must first generate and activate the conda environment from a command prompt (not PowerShell):

```
conda env create -f environment.yml
conda activate IOTEnv
```

### Simulate Sensor Data to IOT Hub

```
(IOTEnv) PATH> python simulate_sensors.py
```

Script mimics messages going from sensors to the IOT Hub. These messages populate the storage table. 

See file for more detail.

### Simulate Serverless Function Activity

```
(IOTEnv) PATH> python simulate_serverless.py
```

> <b>NOTE</b>: This example does not actually set up an Azure Function, instead this file mimics the behavior that would be required within the function itself.

Script mimics Azure Function for:
- Scanning messages arriving within a specified window.
- Sending notifications back to the device.
- Clearing the storage table cache of outdated records.  

See file for more detail.

#### Monitor activity for messages back to the device
https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-visual-studio-cloud-device-messaging

or

https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-vscode-iot-toolkit-cloud-device-messaging

[Top of article](#azureiotexample)
