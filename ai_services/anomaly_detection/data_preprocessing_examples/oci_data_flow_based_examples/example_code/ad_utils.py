import json
import time
from argparse import ArgumentParser

from oci.ai_anomaly_detection import AnomalyDetectionClient
from oci.ai_anomaly_detection.models import CreateModelDetails, \
    ModelTrainingDetails, CreateDataAssetDetails, \
    DataSourceDetailsObjectStorage

from oci.ai_anomaly_detection.models import CreateDetectAnomalyJobDetails, \
    DetectAnomalyJob, ObjectListInputDetails, ObjectLocation, \
    ObjectStoreOutputDetails
from example_code.dataflow_utils import \
    get_authenticated_client, DEFAULT_PROFILE, DEFAULT_LOCATION, \
    DataflowSession

DEFAULT_TARGET_FAP = 0.01
DEFAULT_TRAINING_FRACTION = 0.7


class AdUtils:
    terminal_job_states = [DetectAnomalyJob.LIFECYCLE_STATE_CANCELED,
                           DetectAnomalyJob.LIFECYCLE_STATE_FAILED,
                           DetectAnomalyJob.LIFECYCLE_STATE_PARTIALLY_SUCCEEDED,
                           DetectAnomalyJob.LIFECYCLE_STATE_SUCCEEDED]
    RETRY_SECONDS = 30
    INFERENCE_RESULTS_FOLDER = "inference_results"

    def __init__(self, dataflow_session, profile_name=DEFAULT_PROFILE,
                 file_location=DEFAULT_LOCATION, service_endpoint=None):
        client_args = {
            'profile_name': profile_name,
            'file_location': file_location,
            'dataflow_session': dataflow_session
        }
        if service_endpoint:
            client_args['service_endpoint'] = service_endpoint
        self.ad_client = get_authenticated_client(
            client=AnomalyDetectionClient, **client_args)

    def train(self, project_id, compartment_id, data_asset_detail,
              target_fap=DEFAULT_TARGET_FAP,
              training_fraction=DEFAULT_TRAINING_FRACTION):
        data_asset_id = self._create_data_asset_(
            project_id, compartment_id, data_asset_detail['namespace'],
            data_asset_detail['bucket'], data_asset_detail['object'])
        return self._create_model_(project_id, compartment_id, data_asset_id,
                                   target_fap, training_fraction)

    def _create_data_asset_(self, project_id, compartment_id, namespace,
                            bucket, object_name):
        data_source_details = DataSourceDetailsObjectStorage(
            namespace=namespace, bucket_name=bucket, object_name=object_name)
        create_data_asset_details = CreateDataAssetDetails(
            compartment_id=compartment_id, project_id=project_id,
            data_source_details=data_source_details)
        data_asset_create_response = self.ad_client.create_data_asset(
            create_data_asset_details)
        assert data_asset_create_response.status == 200, \
            f"Error creating data-asset: {data_asset_create_response.text}"
        return data_asset_create_response.data.id

    def _create_model_(self, project_id, compartment_id, data_asset_id,
                       target_fap, training_fraction):
        model_training_details = ModelTrainingDetails(
            target_fap=target_fap, training_fraction=training_fraction,
            data_asset_ids=[data_asset_id])
        create_model_details = CreateModelDetails(
            compartment_id=compartment_id, project_id=project_id,
            model_training_details=model_training_details)
        create_model_response = self.ad_client.create_model(
            create_model_details)
        assert create_model_response.status == 201, \
            f"Error creating model: {create_model_response.text}"
        return create_model_response.data.id

    def create_detect_anomalies_job(self, compartment_id, model_id,
                                    data_asset_detail,
                                    output_path) -> DetectAnomalyJob:

        input_details = ObjectListInputDetails(
            object_locations=[ObjectLocation(
                namespace_name=data_asset_detail['namespace'],
                bucket_name=data_asset_detail['bucket'],
                object_name=data_asset_detail['object'])])
        output_details = ObjectStoreOutputDetails(
            namespace_name=data_asset_detail['namespace'],
            bucket_name=output_path,
            prefix=self.INFERENCE_RESULTS_FOLDER)
        create_detect_anomaly_job_details = CreateDetectAnomalyJobDetails(
            compartment_id=compartment_id,
            display_name="e2e_template_test_job",
            model_id=model_id,
            input_details=input_details,
            output_details=output_details)
        print(f'Creating detection job with details: {create_detect_anomaly_job_details}')
        response = self.ad_client.create_detect_anomaly_job(
            create_detect_anomaly_job_details)
        print(f'Create API response: {response}')
        assert response.status == 200, \
            f"Error detecting anomalies: {response.status}"
        return response.data

    def infer(self, compartment_id: str, model_ids, staging_details, output_path) \
            -> int:
        jobs = []
        for data_asset_detail in staging_details:
            columns = data_asset_detail["columns"]
            columns = '.'.join(str(col) for col in columns)
            matching_model_id = ""
            for model_info in model_ids["model_ids"]:
                model_columns = model_info["columns"]
                model_columns = '.'.join(str(col) for col in model_columns)
                if model_columns == columns:
                    matching_model_id = model_info["model_id"]
            assert matching_model_id != "",\
                f"Columns not matching, schema does not match training dataset"
            create_job = self.create_detect_anomalies_job(compartment_id,
                                             matching_model_id,
                                             data_asset_detail,
                                             output_path)
            jobs.append(create_job.id)
        retries = 0
        while jobs and retries < 10:
            retries = retries + 1
            for job_id in list(jobs):
                time.sleep(self.RETRY_SECONDS)
                response = self.ad_client.get_detect_anomaly_job(job_id)
                if response.status != 200:
                    f"Error fetching detect job status: {response.status}"
                else:
                    job = response.data
                    if job.lifecycle_state in self.terminal_job_states:
                        jobs.remove(job.id)
                        if job.lifecycle_state != DetectAnomalyJob.LIFECYCLE_STATE_SUCCEEDED:
                            return 1
        assert retries <= 10
        return 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--profile_name", required=False, type=str,
                        default=DEFAULT_PROFILE)
    parser.add_argument("--service_endpoint", required=False, type=str,
                        default=None)
    parser.add_argument("--compartment_id", required=True, type=str)

    subparsers = parser.add_subparsers(dest="subparser_name")
    training_parser = subparsers.add_parser('train')
    training_parser.add_argument("--project_id", required=True, type=str)
    training_parser.add_argument("--target_fap", required=False,
                                 type=lambda v: float(v),
                                 default=DEFAULT_TARGET_FAP)
    training_parser.add_argument("--training_fraction", required=False,
                                 type=lambda v: float(v),
                                 default=DEFAULT_TRAINING_FRACTION)
    training_parser.add_argument("--data_asset_detail", required=True,
                                 type=str)

    inference_parser = subparsers.add_parser('infer')
    inference_parser.add_argument("--model_id", required=False, type=str)
    inference_parser.add_argument("--output_path", required=False, type=str)
    inference_parser.add_argument("--namespace", required=False, type=str)
    inference_parser.add_argument("--bucket", required=False, type=str)
    inference_parser.add_argument("--object", required=False, type=str)

    parser.print_help()
    args = parser.parse_args()

    _dataflow_session = DataflowSession(app_name='AnomalyDetectionClient')
    ad_utils = AdUtils(_dataflow_session, profile_name=args.profile_name,
                       service_endpoint=args.service_endpoint)
    if args.subparser_name == "train":
        _data_asset_detail = json.loads(str(args.data_asset_detail))
        model_id = ad_utils.train(
            project_id=args.project_id, compartment_id=args.compartment_id,
            data_asset_detail=_data_asset_detail)
        print(f"Model id: {model_id}")
    elif args.subparser_name == "infer":
        ad_utils.infer(compartment_id=args.compartment_id,
                       model_id=args.model_id,
                       staging_details=[{"namespace": args.namespace,
                                         "bucket": args.bucket,
                                         "object": args.object}],
                       output_path=args.output_path)
