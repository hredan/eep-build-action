from py_modules.info_base import InfoBase, CORE_DATA_DIR

class CoreList(InfoBase):
    def __init__(self):
        try:
            self.cores = self.load_json(f"{CORE_DATA_DIR}/core_list.json")
        except Exception as e:
            print(f"Error initializing CoreList: {e}")
            exit(1)
    
    def get_core_version(self, core_name):
        for core in self.cores:
            if core["core_name"] == core_name:
                return core["latest_version"]
        return None