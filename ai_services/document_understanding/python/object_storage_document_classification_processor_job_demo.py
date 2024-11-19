# coding: utf-8
# Copyright (c) 2016, 2024, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

##########################################################################
# object_storage_document_classification_processor_job_demo.py
#
# Supports Python 3
##########################################################################
# Info:
# Object Storage Document Classification Processor Job creation using OCI AI Document Understanding service.
#
##########################################################################
# Application Command line(no parameter needed)
# python object_storage_document_classification_processor_job_demo.py
##########################################################################

"""
This sample script creates an asynchronous processor job to perform document classification on document_classification_demo.pdf 
(found in the resources folder), which is expected to be found in the specified object storage bucket. Successful execution of this 
sample will create results in object storage as configured under the output_location variable.

Review and update the instructions following "TODO" to configure the script for your OCI tenancy. 
The test document will be uploaded to the object storage bucket specified by 'bucketname' and 'object_location'.

This script is designed to be executed on a user's computer that is configured with Python 3 or later. The user's computer 
must also be configured with a config file as described in README.md to authenticate with the OCI tenancy used to execute 
the SDK requests in this script. The authentication config file used by this script will be sourced from the default location (~/.oci/config) 
and the default profile in the config file will be used.

The Document Understanding service region invoked by this example is represented by an endpoint url defined by the variable 'endpoint'.
"""

import oci
import uuid
import base64
import os

# PREPARE TO AUTHENTICATE WITH THE SDK ------------------------------------------------------------
# Obtain the authentication configuration from the local file
config = oci.config.from_file()
# To use a specific profile in the config file, use these instructions instead:
"""
CONFIG_PROFILE = "doctest_profile"      # specify the name of the profile in the config file
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
"""

# UPLOAD THE DEMO DOCUMENT TO OBJECT STORAGE ------------------------------------------------------------
# Specify the name of the file to be uploaded
samplefile = "resources/document_classification_demo.pdf"

# Specify the name of the bucket where the file will be stored
# TODO - set the bucket name from your tenancy
bucketname = "postman"      # e.g. "demo-documents"

# Setup parameters need to upload the sample file 
object_storage = oci.object_storage.ObjectStorageClient(config)  
namespace = object_storage.get_namespace().data  
filename = os.path.basename(samplefile)

# Upload the sample file to the specified object storage bucket. The document will be overwritten if it alrady exists.
with open(samplefile, 'rb') as f:
    obj = object_storage.put_object(namespace,bucketname,filename,f)
    print(f'"{filename}" uploaded to bucket "{bucketname}"')

# CONFIGURE THE JOB ------------------------------------------------------------
# Specify Compartment where processor job will be created
# TODO - set the compartment ID from your tenancy
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaag2hxw73h2kz6nkqfs4yvt6sdufhko7ufc367kfgxtcwrcwz5xsgq"  # e.g. "ocid1.compartment.oc1..aaaaaaaar3nriwuw4nmqbhe7alu3ou76vgujnq3cvjwjpcv2iivfbadcqfna";

def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)

# Initialize client service_endpoint is optional, if not provided then client will point to region specified in oci config
# TODO - set the Document Understanding endpoint for the desired region. See https://docs.oracle.com/en-us/iaas/api/#/en/document-understanding/20221109/
endpoint = "https://document.aiservice.us-sanjose-1.oci.oraclecloud.com"
aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config, service_endpoint=endpoint))

# Specify the Document Classification feature
document_classification_feature = oci.ai_document.models.DocumentClassificationFeature()

# Specify the location where the document to be processed is stored
#TODO - set .namespace_name and .object_name for your tenancy
object_location = oci.ai_document.models.ObjectLocation()
object_location.namespace_name = "axcqscmddjqn"  # e.g. "axk2tfhlrens"
object_location.bucket_name = bucketname
object_location.object_name = filename

# Setup the output location where processor job results will be created
# TODO - set .namespace_name and .prefix for your tenancy
output_location = oci.ai_document.models.OutputLocation()
output_location.namespace_name = "axcqscmddjqn"  # e.g. "axk2tfhlrens"
output_location.bucket_name = bucketname
output_location.prefix = "results-python"

# Assemble the job details
create_processor_job_details_document_classification_extraction = oci.ai_document.models.CreateProcessorJobDetails(
                                                display_name=str(uuid.uuid4()),
                                                compartment_id=COMPARTMENT_ID,
                                                input_location=oci.ai_document.models.ObjectStorageLocations(object_locations=[object_location]),
                                                output_location=output_location,
                                                processor_config=oci.ai_document.models.GeneralProcessorConfig(features=[document_classification_feature]))

# EXECUTE THE JOB ------------------------------------------------------------
# Initiate the processor job status and wait for it to succeed
print("Calling create_processor with create_processor_job_details_document_classification_extraction:", create_processor_job_details_document_classification_extraction, "\n\rWaiting for processor job to finish...")
create_processor_response = aiservicedocument_client.create_processor_job_and_wait_for_state(
    create_processor_job_details=create_processor_job_details_document_classification_extraction,
    wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
    waiter_kwargs={"wait_callback": create_processor_job_callback})

# Get the processor job status and display it
print("Processor job succeeded with status: {} and request_id: {}.".format(create_processor_response.status, create_processor_response.request_id))
processor_job: oci.ai_document.models.ProcessorJob = create_processor_response.data
print("Job response:\n\r", create_processor_response.data)

# Get the results from the object storage output location and display it
print("Getting result json from the output_location")
object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
get_object_response = object_storage_client.get_object(namespace_name=output_location.namespace_name,
                                                       bucket_name=output_location.bucket_name,
                                                       object_name="{}/{}/{}_{}/results/{}.json".format(
                                                           output_location.prefix, processor_job.id,
                                                           object_location.namespace_name,
                                                           object_location.bucket_name,
                                                           object_location.object_name))
print(str(get_object_response.data.content.decode()))
print("You can also access the results in the specified output location under the job id: ", processor_job.id)