from oci.config import from_file

# import oci
import time
from oci.ai_anomaly_detection.models import *
from oci.ai_anomaly_detection.anomaly_detection_client import AnomalyDetectionClient
from oci.ai_anomaly_detection.models.data_item import DataItem
from oci.ai_anomaly_detection.models.inline_detect_anomalies_request import (
    InlineDetectAnomaliesRequest,
)
from oci.ai_anomaly_detection.models.embedded_detect_anomalies_request import (
    EmbeddedDetectAnomaliesRequest,
)
from oci.ai_anomaly_detection.models.create_project_details import CreateProjectDetails
from oci.ai_anomaly_detection.models.create_data_asset_details import (
    CreateDataAssetDetails,
)
from oci.ai_anomaly_detection.models.data_source_details import DataSourceDetails
from oci.ai_anomaly_detection.models.data_source_details_object_storage import (
    DataSourceDetailsObjectStorage,
)
from oci.ai_anomaly_detection.models.create_model_details import CreateModelDetails
from oci.ai_anomaly_detection.models.model_training_details import ModelTrainingDetails
from oci.ai_anomaly_detection.models.change_project_compartment_details import (
    ChangeProjectCompartmentDetails,
)
from oci.ai_anomaly_detection.models.change_data_asset_compartment_details import (
    ChangeDataAssetCompartmentDetails,
)
from oci.ai_anomaly_detection.models.change_model_compartment_details import (
    ChangeModelCompartmentDetails,
)

from datetime import datetime
import json
import base64
def test_project_crud():
    # PROJECT
    print("-*-*-*-PROJECT-*-*-*-")

    # CREATE CALL
    proj_details = CreateProjectDetails(
        display_name="PythonSDKTestProject",
        description="PythonSDKTestProject description",
        compartment_id=compartment_id,
    )
    create_res = ad_client.create_project(create_project_details=proj_details)
    print("----CREATING----")
    print(create_res.data)
    time.sleep(5)
    project_id = create_res.data.id

    # GET CALL
    get_proj = ad_client.get_project(project_id=project_id)
    print("----READING---")
    print(get_proj.data)
    time.sleep(5)

    # ------------------------------  Move compartment  --------------------------
    mv_details = AnomalyDetectionClient(config)

    dest_compartment_id = (
        "REPLACE ME: ENTER YOUR COMPARTMENT OCID"
    )
    chg_details = ChangeProjectCompartmentDetails(compartment_id=dest_compartment_id)

    mv_compart_res = mv_details.change_project_compartment(project_id, chg_details)
    print(mv_compart_res)
    print(f"successfully moved to compartment {dest_compartment_id}")

    chg_orig_details = ChangeProjectCompartmentDetails(compartment_id=compartment_id)
    mv_bk_compart_res = mv_details.change_project_compartment(project_id, chg_orig_details)
    print(mv_bk_compart_res)
    print(f"successfully moved back to the original compartment {compartment_id}")

    # LIST CALL
    list_proj = ad_client.list_projects(compartment_id=compartment_id)
    print("----LISTING----")
    print(list_proj.data)
    time.sleep(5)

    # UPDATE CALL
    update_proj_details = UpdateProjectDetails(
        description="Updated PythonSDKTestProject description"
    )
    update_proj = ad_client.update_project(
        project_id=project_id, update_project_details=update_proj_details
    )
    print("----UPDATING----")
    print(update_proj.data)
    time.sleep(60)

    print("##### All Project CRUD operations successful #####")
    return project_id

def test_data_asset_crud(project_id:str):
    # DATA ASSET
    print("-*-*-*-DATA ASSET-*-*-*-")
    # CREATE CALL
    dDetails = DataSourceDetails(data_source_type="ORACLE_OBJECT_STORAGE")

    dObjDeatils = DataSourceDetailsObjectStorage(
        namespace="REPLACE ME: ENTER NAMESPACE",
        bucket_name="REPLACE ME: ENTER BUCKET NAME",
        object_name="latest_training_data.json",
    )

    da_details = CreateDataAssetDetails(
        display_name="PythonSDKTestDataAsset",
        description="description DataAsset",
        compartment_id=compartment_id,
        project_id=project_id,
        data_source_details=dObjDeatils,
    )
    create_res = ad_client.create_data_asset(create_data_asset_details=da_details)
    print("----CREATING----")
    print(create_res.data)
    time.sleep(5)
    da_id = create_res.data.id

    # READ CALL
    get_da = ad_client.get_data_asset(data_asset_id=da_id)
    print("----READING----")
    print(get_da.data)
    time.sleep(5)

    # ------------------------------  Move data asset  --------------------------
    mv_details = AnomalyDetectionClient(config)

    dest_compartment_id = (
        "REPLACE ME: ENTER YOUR COMPARTMENT OCID"
    )
    chg_da_details = ChangeDataAssetCompartmentDetails(compartment_id=dest_compartment_id)
    mv_da_res = mv_details.change_data_asset_compartment(da_id, chg_da_details)
    print(mv_da_res)
    print(f"successfully moved data asset {da_id} to compartment {dest_compartment_id}")

    time.sleep(60)

    chg_orig_da_details = ChangeDataAssetCompartmentDetails(compartment_id=compartment_id)
    mv_bk_da_res = mv_details.change_data_asset_compartment(da_id, chg_orig_da_details)
    print(mv_bk_da_res)
    print("successfully moved back data asset")

    # LIST CALL
    list_da = ad_client.list_data_assets(
        compartment_id=compartment_id, project_id=project_id
    )
    print("----LISTING----")
    print(list_da.data)
    time.sleep(30)

    # UPDATE CALL
    update_da_details = UpdateDataAssetDetails(description="Updated description DataAsset")
    update_da = ad_client.update_data_asset(
        data_asset_id=da_id, update_data_asset_details=update_da_details
    )
    print("----UPDATING----")
    print(update_da.data)
    time.sleep(60)
    print("##### All Data Asset CRUD operations successful #####")
    return da_id

def test_model_crud(project_id:str, da_id:str):
    # MODEL
    print("-*-*-*-MODEL-*-*-*-")
    # CREATE CALL
    dataAssetIds = [da_id]
    mTrainDetails = ModelTrainingDetails(
        target_fap=0.02, training_fraction=0.7, data_asset_ids=dataAssetIds
    )
    mDetails = CreateModelDetails(
        display_name="DisplayNameModel",
        description="description Model",
        compartment_id=compartment_id,
        project_id=project_id,
        model_training_details=mTrainDetails,
    )

    create_res = ad_client.create_model(create_model_details=mDetails)
    print("----CREATING----")
    print(create_res.data)
    time.sleep(60)
    model_id = create_res.data.id

    # READ CALL
    get_model = ad_client.get_model(model_id=model_id)
    print("----READING----")
    print(get_model.data)
    time.sleep(60)
    while get_model.data.lifecycle_state == Model.LIFECYCLE_STATE_CREATING:
        get_model = ad_client.get_model(model_id=model_id)
        time.sleep(60)
        print(get_model.data.lifecycle_state)

    mv_details = AnomalyDetectionClient(config)
    dest_compartment_id = (
        "REPLACE ME: ENTER YOUR COMPARTMENT OCID"
    )

    chg_mod_details = ChangeModelCompartmentDetails(compartment_id=dest_compartment_id)
    mv_mod_res = mv_details.change_model_compartment(model_id, chg_mod_details)
    print(mv_mod_res)
    print(f"successfully moved model {model_id} to compartment {dest_compartment_id}")

    time.sleep(30)

    chg_orig_mod_details = ChangeModelCompartmentDetails(compartment_id=compartment_id)
    mv_bk_mod_res = mv_details.change_model_compartment(model_id, chg_orig_mod_details)
    print(mv_bk_mod_res)
    print("successfully moved model back")

    time.sleep(60)

    # LIST CALL
    list_model = ad_client.list_models(compartment_id=compartment_id, project_id=project_id)
    print("----LISTING----")
    print(list_model.data)
    time.sleep(60)

    # UPDATE CALL
    update_model_details = UpdateModelDetails(description="Updated description Model")
    update_model = ad_client.update_model(
        model_id=model_id, update_model_details=update_model_details
    )
    print("----UPDATING----")
    print(update_model.data)
    time.sleep(60)
    print("##### All Model CRUD operations successful #####")
    return model_id

def test_detect_crud(model_id:str):
    # DETECT
    print("-*-*-*-DETECT-*-*-*-")
    signalNames = [
        "sensor1",
        "sensor2",
        "sensor3",
        "sensor4",
        "sensor5",
        "sensor6",
        "sensor7",
        "sensor8",
        "sensor9",
        "sensor10",
        "sensor11",
    ]
    timestamp = datetime.strptime("2020-07-13T20:44:46Z", "%Y-%m-%dT%H:%M:%SZ")
    values = [
        1.0,
        0.4713,
        1.0,
        0.5479,
        1.291,
        0.8059,
        1.393,
        0.0293,
        0.1541,
        0.2611,
        0.4098,
    ]
    dItem = DataItem(timestamp=timestamp, values=values)
    inlineData = [dItem]
    inline = InlineDetectAnomaliesRequest(
        model_id=model_id, request_type="INLINE", signal_names=signalNames, data=inlineData
    )

    detect_res = ad_client.detect_anomalies(detect_anomalies_details=inline)
    print("----DETECTING----")
    print(detect_res.data)

    payload = b"timestamp,sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7,sensor8,sensor9,sensor10,sensor11\n2020-07-13T20:44:46Z,1,0.4713,1,0.5479,1.291,0.8059,1.393,0.0293,0.1541,0.2611,0.4098\n"
    inlineData_b64 = base64.b64encode(payload)
    inline_b64 = EmbeddedDetectAnomaliesRequest(
        model_id=model_id, content_type="CSV", content=str(inlineData_b64, "utf-8")
    )

    detect_b64_res = ad_client.detect_anomalies(detect_anomalies_details=inline_b64)
    print("----DETECTING----")
    print(detect_b64_res.data)
    print("##### DETECT operation successful #####")



def teardown(project_id:str, da_id:str, model_id:str):
    # DELETE MODEL
    delete_model = ad_client.delete_model(model_id=model_id)
    print("----DELETING MODEL----")
    print(delete_model.data)
    time.sleep(60)

    # DELETE DATA ASSET
    delete_da = ad_client.delete_data_asset(data_asset_id=da_id)
    print("----DELETING DATA ASSET----")
    print(delete_da.data)
    time.sleep(60)

    # DELETE PROJECT
    print("----DELETING PROJECT----")
    delete_project = ad_client.delete_project(project_id=project_id)
    print(delete_project.data)

    print("### Teardown Successful ###")

def setup():
    print("Setting up the configurations...")
    global config, compartment_id, ad_client
    config = from_file("~/.oci/config")
    compartment_id = "REPLACE ME: ENTER YOUR COMPARTMENT OCID"
    ad_client = AnomalyDetectionClient(
        config,
        service_endpoint="https://anomalydetection.aiservice.us-phoenix-1.oci.oraclecloud.com",
    )  # /20210101
def main():
    print("### STARTING AD CRUD SDK ###")
    project_id = test_project_crud()
    da_id = test_data_asset_crud(project_id)
    model_id = test_model_crud(project_id, da_id)
    test_detect_crud(model_id)
    teardown(project_id, da_id, model_id)

    print("### ALL AD CRUD SDK SUCCESSFUL ###")

if __name__ == "__main__":
    setup()
    main()
