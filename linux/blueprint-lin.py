"""
Multi-VM Blueprint for Linux on AHV Utilizing AI datasets
"""
import os
from pathlib import Path
import yaml, json
from calm.dsl.builtins import *
from calm.dsl.providers import get_provider

project_root = Path(__file__).parent.parent.parent.parent.parent

ACCOUNT_NAME="NTNX_LOCAL_AZ"

#bp_root_folder = Path(__file__).parent.parent
bp_root_folder = "/nai-llm"

TSHIRT_SPEC_PATH = (f"{bp_root_folder}/tshirt-specs/tshirt_specs.yaml")
TSHIRT_SPECS = yaml.safe_load(read_file(TSHIRT_SPEC_PATH, depth=3))
COMMON_TASK_LIBRARY = f"{bp_root_folder}/common_task_library"
INSTALL_SCRIPTS_DIRECTORY = f"{COMMON_TASK_LIBRARY}/install"
DAY2_SCRIPTS_DIRECTORY = f"{COMMON_TASK_LIBRARY}/day-two"

#print('bp name is {}'.format(bp["name"]))
subnet_name = "Primary"
#print('subnet is {}'.format(subnet_name))
cluster_name = "DM3-POC127"
#print('cluster is {}'.format(cluster_name))
image_name = "ubuntu-22.04.1-100Gb"
#print('image is {}'.format(image_name))
AHVProvider = get_provider("AHV_VM")
ApiObj = AHVProvider.get_api_obj()
acct_ref = Ref.Account(ACCOUNT_NAME)
acct_data = acct_ref.compile()
account_uuid = acct_data["uuid"]
res_subnets = ApiObj.subnets(account_uuid=account_uuid)
#print('subnet data is {}'.format(res_subnets))
net_name_uuid_list = []
for entity in res_subnets.get("entities", []):
    if entity['status']['cluster_reference']['name'] == cluster_name and entity['status']['name'] == subnet_name:
        x = {"name": entity['status']['name'], "uuid": entity['metadata']['uuid']}
        net_name_uuid_list.append(x)
#print('net list is {}'.format(net_name_uuid_list))
res_images = ApiObj.images(account_uuid=account_uuid)
image_name_uuid_list = []
for entity in res_images.get("entities", []):
    if entity['status']['name'] == image_name:
        x = {"name": entity['status']['name'], "uuid": entity['metadata']['uuid']}
        image_name_uuid_list.append(x)
#print('image list is {}'.format(image_name_uuid_list))


# Secret Variables
if file_exists(f"{bp_root_folder}/.local/vm-key"):
    BP_CRED_cred_os_KEY = read_local_file(f"{bp_root_folder}/.local/vm-key")
    #print(BP_CRED_cred_os_KEY)
else:
    BP_CRED_cred_os_KEY = "nutanix"
if file_exists(f"{bp_root_folder}/.local/vm-key.pub"):
    BP_CRED_cred_os_public_KEY = read_local_file(f"{bp_root_folder}/.local/vm-key.pub")
    #print(BP_CRED_cred_os_public_KEY)
else:
    BP_CRED_cred_os_public_KEY = "nutanix"

# Credentials
BP_CRED_cred_os = basic_cred("ubuntu",BP_CRED_cred_os_KEY,name="cred_os",type="KEY",default=True)

class VM_Provision(Service):
    @action
    def NGTTools_Tasks():
        CalmTask.Exec.ssh(name="install_NGT",filename=INSTALL_SCRIPTS_DIRECTORY + "/ngt/install_ngt.sh",target=ref(VM_Provision),)

    @action
    def Configure_VM():
        CalmTask.Exec.ssh(name="ssh_key_copy",filename=INSTALL_SCRIPTS_DIRECTORY + "/ssh_key_copy.sh",target=ref(VM_Provision),)
        CalmTask.Exec.ssh(name="setup",filename=INSTALL_SCRIPTS_DIRECTORY + "/setup.sh",target=ref(VM_Provision),)
        CalmTask.Exec.ssh(name="validate driver",filename=INSTALL_SCRIPTS_DIRECTORY + "/validate_driver.sh",target=ref(VM_Provision),)
        CalmTask.Exec.ssh(name="nai setup",filename=INSTALL_SCRIPTS_DIRECTORY + "/nai_llm.sh",target=ref(VM_Provision),)
        

class AHVVM_Default(Substrate):
    os_type = "Linux"
    provider_type = "AHV_VM"
    provider_spec = read_ahv_spec("specs/ahv-provider-spec.yaml")
    provider_spec_editables = read_spec(os.path.join("specs", "create_spec_editables.yaml"))
    readiness_probe = readiness_probe(connection_type="SSH",disabled=False,retries="5",connection_port=22,address="@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",delay_secs="30",credential=ref(BP_CRED_cred_os),)
    # update CPU, Memory based on environment specific configs =============================================vvvvvv
    provider_spec.spec["resources"]["num_sockets"] = TSHIRT_SPECS["linux-os"]["global"]["tshirt_sizes"]["default"]["num_sockets"]
    provider_spec.spec["resources"]["num_vcpus_per_socket"] = TSHIRT_SPECS["linux-os"]["global"]["tshirt_sizes"]["default"]["num_vcpus_per_socket"]
    provider_spec.spec["resources"]["memory_size_mib"] = TSHIRT_SPECS["linux-os"]["global"]["tshirt_sizes"]["default"]["memory_size_mib"]
    # update nic ===========================================================================================vvvvvv
    provider_spec.spec["resources"]["nic_list"][0]["subnet_reference"]["name"] = str(net_name_uuid_list[0]['name'])
    provider_spec.spec["resources"]["nic_list"][0]["subnet_reference"]["uuid"] = str(net_name_uuid_list[0]['uuid'])
    # update image ==========================================================================================vvvvvv
    provider_spec.spec["resources"]["disk_list"][0]["data_source_reference"]["name"] = str(image_name_uuid_list[0]['name'])
    provider_spec.spec["resources"]["disk_list"][0]["data_source_reference"]["uuid"] = str(image_name_uuid_list[0]['uuid'])

class AHV_Package_Def(Package):
    services = [ref(VM_Provision)]

    @action
    def __install__():
        VM_Provision.NGTTools_Tasks(name="Install NGT")
        VM_Provision.Configure_VM(name="Configure VM")

class AHV_Deployment_Def(Deployment):
    min_replicas = "1"
    max_replicas = "100"
    default_replicas = "@@{WORKER}@@"
    packages = [ref(AHV_Package_Def)]
    substrate = ref(AHVVM_Default)

class Common(Profile):
    os_cred_public_key = CalmVariable.Simple.Secret(BP_CRED_cred_os_public_KEY,label="OS Cred Public Key",is_hidden=True,description="SSH public key for OS CRED user.")
    NFS_PATH = CalmVariable.Simple("",label="NFS Share Path",regex="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}:(\/[a-zA-Z0-9_-]+)+$",validate_regex=True,is_mandatory=True,is_hidden=False,runtime=True,description="Enter the path to your IP NFS share.  For example 10.10.10.10:/sharename")
    WORKER = CalmVariable.Simple("1",label="",is_mandatory=False,is_hidden=False,runtime=True,description="")
    NVIDIA_DRIVER_VERSION = CalmVariable.WithOptions.Predefined.string(["515.86.01"],label="Please select the NVidia driver version to be used.",default="515.86.01",is_mandatory=True,is_hidden=False,runtime=True,description="",)
    NAI_LLM_REVISION = CalmVariable.WithOptions.Predefined.string(["0.1"],label="NAI LLM Revision.",default="0.1",is_mandatory=True,is_hidden=False,runtime=True,description="",)
    
    @action
    def AIStartInferenceService(name="AI Start Inference Service"):
        CalmTask.Exec.ssh(name="AI Start Inference Service",filename=DAY2_SCRIPTS_DIRECTORY + "/ai_inference_start.sh",target=ref(VM_Provision),)
        AI_MODEL_NAME = CalmVariable.WithOptions.Predefined.string(["mpt_7b","falcon_7b","llama2_7b","phi-1_5"],label="Please select the model to be used.",default="mpt_7b",is_mandatory=True,is_hidden=False,runtime=True,description="",)
        AI_MODEL_REVISION = CalmVariable.Simple("",label="Model Revision",is_mandatory=False,is_hidden=False,runtime=True,description="OPTIONAL - Leave blank if using default revision",)
        
    @action
    def AIStopInferenceService(name="AI Stop Inference Service"):
        CalmTask.Exec.ssh(name="AI Stop Inference Service",filename=DAY2_SCRIPTS_DIRECTORY + "/ai_inference_stop.sh",target=ref(VM_Provision),)

    @action
    def Model_Download(name="Download AI Model"):
        CalmTask.Exec.ssh(name="Download AI Model",filename=DAY2_SCRIPTS_DIRECTORY + "/download_model.sh",target=ref(VM_Provision),)
        AI_MODEL_NAME = CalmVariable.WithOptions.Predefined.string(["mpt_7b","falcon_7b","llama2_7b","phi-1_5"],label="Please select the model to be downloaded.",default="mpt_7b",is_mandatory=True,is_hidden=False,runtime=True,description="",)
        AI_MODEL_REVISION = CalmVariable.Simple("",label="Model Revision",is_mandatory=False,is_hidden=False,runtime=True,description="OPTIONAL - Leave blank if using default revision",)
        
        # AI_TRAINING_OUTPUT_FOLDER = CalmVariable.Simple("",label="AI Training Output Folder",is_mandatory=False,is_hidden=False,runtime=True,description="OPTIONAL - Leave blank if not needed",)
        # AI_TRAINING_OUTPUT_FOLDER_DEFAULT = CalmVariable.Simple("training-output",label="AI Training Output Folder Default Value",is_mandatory=False,is_hidden=True,runtime=False,description="Default value for the AI Training Output Folder",)
        # AI_TRAINING_OUTPUT_FILE = CalmVariable.Simple("",label="AI Training Output File",is_mandatory=False,is_hidden=False,runtime=True,description="OPTIONAL - Leave blank if not needed",)
        # AI_TRAINING_OUTPUT_FILE_DEFAULT = CalmVariable.Simple("resnet.pth",label="AI Training Output File Default Value",is_mandatory=False,is_hidden=True,runtime=False,description="Default value for the AI Training Output File",)
        # EXTRA_PARAMS = CalmVariable.Simple("",label="AI Inference Optional Extra Parameters",is_mandatory=False,is_hidden=False,runtime=True,description="OPTIONAL - Leave blank if not needed - Enter any extra parameters needed, e.g., --quiet, etc.",)
        # AI_MODEL_NAME = CalmVariable.Simple("",label="AI Training Model Name",is_mandatory=False,is_hidden=False,runtime=True,description="OPTIONAL - Leave blank if not needed - Enter the AI model name if not using the default value",)
        # AI_MODEL_NAME_DEFAULT = CalmVariable.Simple("resnet50",label="AI Training Model Name Default Value",is_mandatory=False,is_hidden=True,runtime=False,description="Default value for the AI model name",)


class AHV_Default(Common):
    deployments = [AHV_Deployment_Def]

    @action
    def Scaleout(name="Scale Out"):
        increase_count = CalmVariable.Simple("1",label="",is_mandatory=False,is_hidden=False,runtime=True,description="",)
        CalmTask.Scaling.scale_out("@@{increase_count}@@", name="ScaleOut",target=ref(AHV_Deployment_Def),)

    @action
    def Scalein(name="Scale In"):
        decrease_count = CalmVariable.Simple("1",label="",is_mandatory=False,is_hidden=False,runtime=True,description="",)
        CalmTask.Scaling.scale_in("@@{decrease_count}@@", name="ScaleIn",target=ref(AHV_Deployment_Def),)


class Linux(Blueprint):

    services = [VM_Provision]
    packages = [AHV_Package_Def]
    substrates = [AHVVM_Default]
    profiles = [AHV_Default]
    credentials = [BP_CRED_cred_os]

Linux.__doc__ = read_file('mp_meta/bp-description.md')

def main():
    print(Linux.json_dumps(pprint=True))

if __name__ == "__main__":
    main()