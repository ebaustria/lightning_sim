from typing import Dict


class ModuleDataStruct:
    def __init__(self):
        self.id_counter = 0
        self.mod_name_dictionary: Dict[str, int] = {}
        self.mod_id_dictionary: Dict[int, str] = {}


    def module_name_exists(self, mod_name: str) -> bool:
        if mod_name in self.mod_name_dictionary:
            mod_id: int = self.mod_name_dictionary[mod_name]

            if mod_id in self.mod_id_dictionary:
                return True

        return False


    def module_id_exists(self, mod_id: int) -> bool:
        if mod_id in self.mod_id_dictionary:
            mod_name: str = self.mod_id_dictionary[mod_id]

            if mod_name in self.mod_name_dictionary:
                return True

        return False


    def add_module_if_not_present(self, mod_name: str):
        if self.module_name_exists(mod_name):
            return

        self.id_counter += 1

        self.mod_name_dictionary[mod_name] = self.id_counter
        self.mod_id_dictionary[self.id_counter] = mod_name


    def get_module_id_if_present(self, mod_name: str) -> int:
        if self.module_name_exists(mod_name):
            return self.mod_name_dictionary[mod_name]

        return -1


    def get_module_name_if_present(self, mod_id: int) -> str:
        if self.module_id_exists(mod_id):
            return self.mod_id_dictionary[mod_id]

        return ""
