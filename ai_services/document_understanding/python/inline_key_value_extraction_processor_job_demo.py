# coding: utf-8
# Copyright (c) 2016, 2024, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

##########################################################################
# inline_key_value_extraction_processor_job_demo.py
#
# Supports Python 3
##########################################################################
# Info:
# Inline Key Value extraction Processor Job creation using OCI AI Document Understanding service.
#
##########################################################################
# Application Command line(no parameter needed)
# python inline_key_value_extraction_processor_job_demo.py
##########################################################################

"""
This sample script creates an asynchronous processor job to perform key value extraction on receipt.jpg
(found in the resources folder), which is supplied inline as a base64 encoded string. Successful execution of this 
sample will create results in object storage as configured under the output_location variable.

This script is designed to be executed on a user's computer that is configured with Python 3 or later. The user's computer 
must also be configured with a config file as described in README.md to authenticate with the OCI tenancy used to execute 
the SDK requests in this script. The authentication config file used by this script will be sourced from the default location (~/.oci/config) 
and the default profile in the config file will be used.

The Document Understanding service region invoked by this example is represented by an endpoint url defined by the variable 'endpoint'
"""

import oci
import uuid
import base64

# CONFIGURE THE JOB ------------------------------------------------------------
# Auth Config
# Initialize the service client with the default profile in the config file
config = oci.config.from_file()
# To use a specific profile in the config file, use these instructions instead:
"""
CONFIG_PROFILE = "doctest_profile"      # specify the name of the profile in the config file
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
"""

# Specify the Compartment where the processor job will be created
# TODO - set the compartment ID from your tenancy
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaag2hxw73h2kz6nkqfs4yvt6sdufhko7ufc367kfgxtcwrcwz5xsgq"  # e.g. "ocid1.compartment.oc1..aaaaaaaar3nriwuw4nmqbhe7alu3ou76vgujnq3cvjwjpcv2iivfbadcqfna";

# Encode the sample document for submitting inline
key_value_extraction_sample_string = None
with open("resources/key_value_extraction_demo.pdf", "rb") as document_file:
    key_value_extraction_sample_string = base64.b64encode(document_file.read()).decode('utf-8')

def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)

# Initializing the client service_endpoint is optional. If not provided then client will point to region specified in oci config
# TODO - specify the Document Understanding endpoint for the desired region. See https://docs.oracle.com/en-us/iaas/api/#/en/document-understanding/20221109/
endpoint = "https://document.aiservice.us-sanjose-1.oci.oraclecloud.com"    #e.g. "https://document.aiservice.us-ashburn-1.oci.oraclecloud.com"
aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config, service_endpoint=endpoint))

# Specify the Key-Value Extraction feature for this processor job
key_value_extraction_feature = oci.ai_document.models.DocumentKeyValueExtractionFeature()

# Setup the output location where the processor job results will be created
# TODO - set .namespace_name, .bucket_name, and .prefix for your tenancy
output_location = oci.ai_document.models.OutputLocation()
output_location.namespace_name = "axcqscmddjqn"  # e.g. "axk2tfhlrens"
output_location.bucket_name = "postman"  # e.g "output"
output_location.prefix = "results-python"  #e.g. "python-sdk"

# Create a processor_job for key_value_extraction feature
create_processor_job_details_key_value_extraction = oci.ai_document.models.CreateProcessorJobDetails(
                                                    display_name=str(uuid.uuid4()),
                                                    compartment_id=COMPARTMENT_ID,
                                                    input_location=oci.ai_document.models.InlineDocumentContent(data=key_value_extraction_sample_string),
                                                    output_location=output_location,
                                                    processor_config=oci.ai_document.models.GeneralProcessorConfig(features=[key_value_extraction_feature]))

# EXECUTE THE JOB ------------------------------------------------------------
# Initiate the processor job status and wait for it to succeed
print("Calling create_processor with create_processor_job_details_key_value_extraction:", create_processor_job_details_key_value_extraction, "\n\rWaiting for processor job to finish...")
create_processor_response = aiservicedocument_client.create_processor_job_and_wait_for_state(
    create_processor_job_details=create_processor_job_details_key_value_extraction,
    wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
    waiter_kwargs={"wait_callback": create_processor_job_callback})

# Get the processor job status and display the job response
print("Processor job succeeded with status: {} and request_id: {}.".format(create_processor_response.status, create_processor_response.request_id))
processor_job: oci.ai_document.models.ProcessorJob = create_processor_response.data
print("This is the processor job response: ", create_processor_response.data)

# Get the key-value extraction results from the object storage output location and display it
print("This is the output json retrieved from the output location:")
object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
get_object_response = object_storage_client.get_object(namespace_name=output_location.namespace_name,
                                                       bucket_name=output_location.bucket_name,
                                                       object_name="{}/{}/_/results/defaultObject.json".format(
                                                           output_location.prefix, processor_job.id))
print(str(get_object_response.data.content.decode()))
print("You can also view the results in the specified output location under the job id: ", processor_job.id)