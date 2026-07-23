import urequests as requests
import btree
import ujson as json
from utils import get_device_id_list


class Db(object):
    def __init__(self, url, db_name="default_db"):
        self.url = url
        self.device = get_device_id_list()
        self.f = self.db_init(db_name)
        self.db = btree.open(self.f)

    def __del__(self):
        self.f.close()
        self.db.close()

    def __call__(self, *args, **kwargs):
        self.process_data_get()
        return len([self.db.keys()]) > 0

    @staticmethod
    def db_init(dbname):
        try:
            f = open(dbname, "r+b")
            print("db opened")
        except OSError:
            f = open(dbname, "w+b")
            print("db created")
        return f

    def db_print(self):
        for key in self.db.keys():
            print(key)

    def db_delete(self):
        for key in self.db.keys():
            del self.db[key]

    def db_save(self, data):
        for key in data.keys():
            self.db[key] = json.dumps(data[key])
        self.db.flush()

    def db_load(self):
        ret_dict = {}
        for key in self.db.keys():
            ret_dict[key] = json.loads(self.db[key])
        return ret_dict

    def process_data_get(self):
        json_payload = {
            "deviceId": self.device,
            "$OPTION": [
                "$GET_DATA"
            ]
        }
        try:
            ret = False
            r = requests.get(self.url, json=json_payload)
            data = r.json()
            if data is not None:
                self.db_delete()
                self.db_save(data["data"])
                ret = True
            r.close()
            return ret
        except OSError:
            print("OSError in request")
        except MemoryError:
            print("MemoryError in request")
