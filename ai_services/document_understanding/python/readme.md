# OCI Document Understanding: Getting Started with the Python SDK

## Introduction

Oracle Cloud Infrastructure provides a number of programming language Software Development Kits (SDKs) to facilitate application integration and development of custom solutions. SDKs allow you to build and deploy apps that integrate with Oracle Cloud Infrastructure services. Each SDK also includes tools and artifacts you need to develop an app, such as code samples and documentation. In addition, if you want to contribute to the development of the SDKs, they are all open source and available on GitHub.

You can invoke OCI Document Understanding capabilities through the OCI SDKs.

## Prerequisites:

### Ensure Document Understanding is configured in your OCI tenancy
Review this documentation to setup policies that allow users to access the document Understanding APIs:
* [Policy to Grant Users Access to Document Understanding APIs](https://docs.oracle.com/en-us/iaas/Content/document-understanding/using/about_document-understanding_policies.htm#policy_users)

It's also a good idea to verify your user account can process documents using the OCI Console for your tenancy.

### Set up config file

You need to set up an API Signing Key and a configuration file so that the SDK can find  the credentials needed to connect to your OCI tenancy and use the Document Understanding capabilities.

If you have never done this before, you may want to follow the steps described in the [OCI Document Understanding Workshop - Lab 4](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/master/labs/ai-document-understanding/workshops/4-python-sdk).

Other related documents:
* [Generating API KEY](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm)
* [SDK and CLI Configuration File](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File)

After completion, you should have following 2 files in your ~/.oci directory 

1. A config file (where key_file refers to private key for your user and tenancy: e.g. key_file=~/.oci/oci_api_key.pem)
2. A private key file, e.g. oci_api_key.pem

### Python requirements

Make sure you have Python 3.x version and that it’s available from your command line. You can check this by simply running 

> python --version

If you do not have Python, please install the latest 3.x version from python.org

Additionally, you’ll need to make sure you have pip available. You can check this by running:

> pip --version

If you installed Python from source, with an installer from python.org, or via Homebrew you should already have pip. If you’re on Linux and installed using your OS package manager, you may have to install pip separately.

### Set up and activate a virtual environment 

To create a virtual environment, run the venv module as a script as shown below

> python3 -m venv <name of virtual environment>

Once you’ve created a virtual environment, you may activate it.

In Mac OS / Linux:

> source \<name of virtual environment>/bin/activate

In Windows:

> \<name of virtual environment>\Scripts\activate

### Install OCI SDK

Once you have activated your environment, install the OCI SDK by running:

> pip install oci

(If you are on a VPN, ensure it allows you to connect to pypi.org. You might need to disconnect from VPN.)

## Execute the sample scripts
### Change directory to this project location
In the python environment that you activated, change the directory to the location where this project resides on your local machine.

```
cd <path to the project>/python
```

### Edit the scripts to work with your OCI tenancy

The comments in each script contain instructions on what values need to be updated for your specific OCI tenancy.
This includes things like compartment ID, regional service endpoint, and object storage locations.

### Execute any or all of the python sample scripts using these commands

Synchronous API using an inline source document:
```
python sync_inline_text_extraction_demo.py
```

Asynchronous API using an inline document source:
```
python inline_text_extraction_processor_job_demo.py
python inline_table_extraction_processor_job_demo.py
python inline_key_value_extraction_processor_job_demo.py
python inline_document_classification_processor_job_demo.py
```

Asynchronous API using object storage as the document source:
```
python object_storage_text_extraction_processor_job_demo.py
python object_storage_table_extraction_processor_job_demo.py
python object_storage_key_value_extraction_processor_job_demo.py
python object_storage_document_classification_processor_job_demo.py
```
 
### When running each of above scripts, you will see the request and the response similar to this example from inline_document_classification_processor_job_demo.py:
Note that the output contains the base64 encoded document, which is REMOVED here for brevity
```
python inline_document_classification_processor_job_demo.py
Calling create_processor with create_processor_job_details_document_classification_extraction: {
  "compartment_id": "ocid1.compartment.oc1..aaaaaaaag2hxw73h2kz6nkqfs4yvt6sdufhko7ufc367kfgxtcwrcwz5xsgq",
  "display_name": "8a868eb6-83a6-4ec1-a576-951fc4bf6752",
  "input_location": {
    "data": "--REMOVED--",
    "source_type": "INLINE_DOCUMENT_CONTENT"
  },
  "output_location": {
    "bucket_name": "postman",
    "namespace_name": "axcqscmddjqn",
    "prefix": "results-python"
  },
  "processor_config": {
    "document_type": null,
    "features": [
      {
        "feature_type": "DOCUMENT_CLASSIFICATION",
        "max_results": null,
        "model_id": null,
        "tenancy_id": null
      }
    ],
    "is_zip_output_enabled": null,
    "language": null,
    "processor_type": "GENERAL"
  }
}
Waiting for processor job to finish...
processor call succeeded with status: 200 and request_id: AAEF79E1FC7447FE88E4E2A44D932B05/CD7BEAB837D2CC81FAD506CFB98BEFA7/4340A8CCA1D3B15BC3EB41DE9BD1FFBA.
create_processor_job_details_document_classification_extraction response:  {
  "compartment_id": "ocid1.compartment.oc1..aaaaaaaag2hxw73h2kz6nkqfs4yvt6sdufhko7ufc367kfgxtcwrcwz5xsgq",
  "display_name": "8a868eb6-83a6-4ec1-a576-951fc4bf6752",
  "id": "ocid1.aidocumentprocessorjob.oc1.us-sanjose-1.amaaaaaa3nkmftyasfwqfleictfbm2bwlwz6kwklne3iqcezyl6asxaier2q",
  "input_location": null,
  "lifecycle_details": null,
  "lifecycle_state": "SUCCEEDED",
  "output_location": {
    "bucket_name": "postman",
    "namespace_name": "axcqscmddjqn",
    "prefix": "results-python"
  },
  "percent_complete": 100.0,
  "processor_config": {
    "document_type": null,
    "features": [
      {
        "feature_type": "DOCUMENT_CLASSIFICATION",
        "max_results": null,
        "model_id": null,
        "tenancy_id": null
      }
    ],
    "is_zip_output_enabled": false,
    "language": null,
    "processor_type": "GENERAL"
  },
  "time_accepted": "2024-01-10T23:12:59.520000+00:00",
  "time_finished": "2024-01-10T23:12:59.520000+00:00",
  "time_started": "2024-01-10T23:12:59.520000+00:00"
}
Getting defaultObject.json from the output_location
{
  "documentMetadata" : {
    "pageCount" : 1,
    "mimeType" : "application/pdf"
  },
  "pages" : [ {
    "pageNumber" : 1,
    "dimensions" : null,
    "detectedDocumentTypes" : [ {
      "documentType" : "RESUME",
      "confidence" : 0.99459565
    }, {
      "documentType" : "PASSPORT",
      "confidence" : 8.510603E-4
    }, {
      "documentType" : "OTHERS",
      "confidence" : 7.4783183E-4
    }, {
      "documentType" : "TAX_FORM",
      "confidence" : 7.022046E-4
    }, {
      "documentType" : "INVOICE",
      "confidence" : 6.5188756E-4
    } ],
    "detectedLanguages" : null,
    "words" : null,
    "lines" : null,
    "tables" : null,
    "documentFields" : null
  } ],
  "detectedDocumentTypes" : [ {
    "documentType" : "RESUME",
    "confidence" : 0.99459565
  } ],
  "detectedLanguages" : null,
  "documentClassificationModelVersion" : "1.6.43",
  "languageClassificationModelVersion" : null,
  "textExtractionModelVersion" : null,
  "keyValueExtractionModelVersion" : null,
  "tableExtractionModelVersion" : null,
  "errors" : null,
  "searchablePdf" : null
}
You can also view the results in the specified output location under the job id:  ocid1.aidocumentprocessorjob.oc1.us-sanjose-1.amaaaaaa3nkmftyasfwqfleictfbm2bwlwz6kwklne3iqcezyl6asxaier2q
```
