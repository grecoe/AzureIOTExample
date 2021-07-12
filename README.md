# AzureIOTExample

This repo creates an example on how to use Azure IOT Hub to recieve and send messages to an IOT device. 

To succesfully use this sample you must 

- Have an Azure Subscription
- Have the ability to create resources in that subscription.
- Have [conda/python](https://docs.conda.io/en/latest/miniconda.html) installed on your system (or Virtual Machine if you so choose). 
- Have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed on your system. 

## Architecture Overview
![](images/BasicArchitecture.jpg)

In this example the flow of data is shown in the above message

|Step|Description|
|----|----|
|1|An IOT Sensor/Device sends messages to the IOT Hub|
|2|A Stream Analytics Job detects incoming IOT Hub messages and branches them to two different storage solutions:<br><br><b>1.</b> (Not implemented in this sample) Dump all raw data to Cosmos DB<br><b>2.</b> Stream out raw data to an Azure Storage Table|
|3|A serverless function (Azure Function):<br><br><b>1.</b> Reads the table storage<br><b>2.</b> Determines if a notification to the device is warranted.<br><b>3</b>. Sends a message back to the device through the IOT Hub.<br><b>4</b>. Performs maintenance (deletes) on storage table (as all data will be in Cosmos)|

> <b>NOTE:</b> This example does not take into account Network Isolation or other security best practices. 

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

### Step 1.2 - Create IOT Device(s)

Now that we have the services up, you will need to [generate an IOT device](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-python-python-device-management-get-started#register-a-new-device-in-the-iot-hub). 

This can be done through the Azure Portal or via the Azure CLI. 


# Step 2 - Create Devices

https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-python-python-device-management-get-started#register-a-new-device-in-the-iot-hub