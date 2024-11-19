# coding: utf-8
# Copyright (c) 2016, 2024, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

##########################################################################
# sync_inline_text_extraction_demo.py
#
# Supports Python 3
##########################################################################
# Info:
# Inline Text extraction using synchronous Analyze Document method of OCI AI Document Understanding service.
#
##########################################################################
# Application Command line(no parameter needed)
# python sync_inline_text_extraction_demo.py
##########################################################################

"""
This sample script executes a synchronous request for text extraction on text_extraction_demo.jpg
(found in the resources folder), which is supplied inline as a base64 encoded string. 
Because this is a synchronous request, the results are returned in the response. 
Object storage is not used at all for this request.

This script is designed to be executed on a user's computer that is configured with Python 3 
or later. The user's computer must also be configured with a config file as described in 
README.md to authenticate with the OCI tenancy used to execute the SDK requests in this script. 
The authentication config file used by this script will be sourced from the default location 
(~/.oci/config) and the default profile in the config file will be used.

The Document Understanding service region invoked by this example is represented by an endpoint 
url defined by the variable 'endpoint'
"""

import oci
import uuid
import base64

# CONFIGURE THE REQUEST ------------------------------------------------------------
# Auth Config
# Initialize the service client with the default profile in the config file
config = oci.config.from_file()
# To use a specific profile in the config file, use these instructions instead:
"""
CONFIG_PROFILE = "doctest_profile"      # specify the name of the profile in the config file
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
"""

# Compartment where processor job will be created
# TODO - set the compartment ID from your tenancy
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaag2hxw73h2kz6nkqfs4yvt6sdufhko7ufc367kfgxtcwrcwz5xsgq"  # e.g. "ocid1.compartment.oc1..aaaaaaaar3nriwuw4nmqbhe7alu3ou76vgujnq3cvjwjpcv2iivfbadcqfna";

# Encode the sample document for submitting inline
text_extraction_sample_string = None
with open("resources/text_extraction_demo.jpg", "rb") as document_file:
    text_extraction_sample_string = base64.b64encode(document_file.read()).decode('utf-8')

# Specify the Document Understanding service endpoint
# TODO - specify the Document Understanding endpoint for the desired region. See https://docs.oracle.com/en-us/iaas/api/#/en/document-understanding/20221109/
endpoint = "https://document.aiservice.us-sanjose-1.oci.oraclecloud.com"
aiservicedocument_client = oci.ai_document.AIServiceDocumentClient(config=config, service_endpoint=endpoint)

# Specify text extraction is to be performed on the sample document
text_extraction_feature_searchable_pdf = oci.ai_document.models.DocumentTextExtractionFeature()
# Furthermore, specify if a Searchable PDF is to be generated from the text extraction results
text_extraction_feature_searchable_pdf.generate_searchable_pdf = False   #set to True to generate a searchable PDF

# Assemble the request parameters
document_details = oci.ai_document.models.AnalyzeDocumentDetails(features=[text_extraction_feature_searchable_pdf],
                                                                 document=oci.ai_document.models.InlineDocumentDetails(
                                                                     data=text_extraction_sample_string),
                                                                 compartment_id=COMPARTMENT_ID
                                                                 )

# EXECUTE THE REQUEST ------------------------------------------------------------
print("Calling synchronous api...")
response = aiservicedocument_client.analyze_document(analyze_document_details=document_details)
# Print the response
print("Text extraction result:\n\r", response.data)