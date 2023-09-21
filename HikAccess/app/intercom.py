from .dbmanager import purge_old_entries, get_active_entries, CodeEntry
import xml.etree.ElementTree as ET
import requests, time, sys
from requests.auth import HTTPDigestAuth

API_USER = "admin"
API_PASSWORD = "Neodomo17"
DEVICE_IP = "192.168.1.182"

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

def intercom_thread():
    while True:
        update_codes()
        time.sleep(60)

def update_codes():
    purge_old_entries()
    try:
        update_intercom(get_active_entries())
    except Exception as e:
        print(e, file=sys.stderr)

def update_intercom(active_entries : list[CodeEntry]):
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
        raise Exception(f"Failed to change code (status code: {str(req.status_code)})")

def delete_code(slot_number):
    upload_code("", "", slot_number, active=0)

def get_managed_codes() -> list[Code]:
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
        raise Exception(f"Failed to get intercom codes (status code: {str(req.status_code)})" )
    return req.content

def parse_codes(XML_string) -> list[Code]:
    root = ET.fromstring(XML_string)
    code_status = []
    pw_info_list = root.find("{http://www.isapi.org/ver20/XMLSchema}passwordInfoList")
    if pw_info_list is None:
        raise Exception("Failed to parse intercom codes (bad passwordInfoList)")
    for pw_info in pw_info_list.findall("{http://www.isapi.org/ver20/XMLSchema}passwordInfo"):
        pw_type = pw_info.find("{http://www.isapi.org/ver20/XMLSchema}passwordType")
        if pw_type is None:
            raise Exception("Failed to parse intercom codes (bad passwordType)")
        pw_type = pw_type.text
        if pw_type is None:
            raise Exception("Failed to parse intercom codes (bad passwordType)")
        pw_index = int(pw_type.replace("public", ""))
        description = pw_info.find("{http://www.isapi.org/ver20/XMLSchema}passwordAlias")
        if description is None:
            raise Exception("Failed to parse intercom codes (bad passwordAlias)")
        description = description.text
        configured = root.find(f"{{http://www.isapi.org/ver20/XMLSchema}}public{pw_index}Configured")
        if configured is None:
            raise Exception("Failed to parse intercom codes (bad publicXConfigured)")
        configured = "true" == configured.text
        code_status.append(Code(pw_index + 5, description, configured))
    return code_status