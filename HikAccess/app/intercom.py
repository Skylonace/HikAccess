from .dbmanager import purge_entries, get_active_entries
import xml.etree.ElementTree as ET
import requests
from requests.auth import HTTPDigestAuth

API_USER = "admin"
API_PASSWORD = "Neodomo17"
DEVICE_IP = "192.168.1.182"

def update_codes():
    purge_entries()
    update_intercom(get_active_entries())

def update_intercom(active_entries):
    managed_codes = get_managed_codes()
    avaliable_codes = []
    # Removing invalid codes
    valid_entry_ids = [entry.id for entry in active_entries]
    for code in managed_codes:
        if code.configured is False:
            avaliable_codes.append(code)
        if code.id not in valid_entry_ids:
            delete_code(code.slot_number)
            avaliable_codes.append(code)
    # Adding new codes
    if(len(avaliable_codes) < len(active_entries)):
        raise Exception("Not enough writeable codes")
    for index, entry in enumerate(active_entries):
        upload_code(entry.code, f"AUTO-{entry.id}-{entry.code}", avaliable_codes[index].slot_number)

def upload_code(code, description, slot_number, active=1):
    url = f"http://{DEVICE_IP}:8090/ISAPI/VideoIntercom/PrivilegePasswordCfg?format=json"
    auth = HTTPDigestAuth(API_USER, API_PASSWORD)
    payload = f"""{{"PrivilegePasswordCfg":{{"passwordType":{slot_number},"newPassword":"{code}","lockIDList":[{active},0],"passwordAlias":"{description}"}}}}"""
    req = requests.put(url, auth=auth, data=payload)
    if req.status_code != 200:
        raise Exception("Failed to upload code")

def delete_code(slot_number):
    upload_code("", "", slot_number, active=0)

def get_managed_codes():
    codes = parse_codes(request_intercom_codes())
    writeable_codes = []
    for code in codes:
        if not code.configured or code.auto_configured:
            writeable_codes.append(code)
    return writeable_codes

def request_intercom_codes():
    url = f"http://{DEVICE_IP}:8090/ISAPI/VideoIntercom/PrivilegePasswordStatus"
    auth = HTTPDigestAuth(API_USER, API_PASSWORD)
    req = requests.get(url, auth=auth)
    if req.status_code != 200:
        raise Exception("Failed to get intercom codes")
    return req.content

def parse_codes(XML_string):
    root = ET.fromstring(XML_string)
    code_status = []
    pw_info_list = root.find("{http://www.isapi.org/ver20/XMLSchema}passwordInfoList")
    if pw_info_list is None:
        return code_status
    for pw_info in pw_info_list.findall("{http://www.isapi.org/ver20/XMLSchema}passwordInfo"):
        pw_type = pw_info.find("{http://www.isapi.org/ver20/XMLSchema}passwordType")
        pw_type = pw_type.text if pw_type is not None else "1"
        pw_index = int(pw_type.replace("public", "") if pw_type is not None else 1)
        description = pw_info.find("{http://www.isapi.org/ver20/XMLSchema}passwordAlias")
        description = description.text if description is not None else ""
        configured = root.find(f"{{http://www.isapi.org/ver20/XMLSchema}}public{pw_index}Configured")
        configured = "true" == configured.text if configured is not None else False
        code_status.append(Code(pw_index + 5, description, configured))
    return code_status

class Code:
    def __init__(self, slot_number, description, configured):
        self.slot_number = slot_number
        self.description = description
        self.configured = configured

    @property
    def auto_configured(self):
        return self.description.startswith("AUTO-")

    @property
    def id(self):
        if self.auto_configured:
            return int(self.description.split("-")[1])
        else:
            return None

    @property
    def code(self):
        if self.auto_configured:
            return self.description.split("-")[2]
        else:
            return None