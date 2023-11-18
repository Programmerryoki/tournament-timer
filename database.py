import pandas as pd

class PlayerDatabase:
    def __init__(self, file_path):
        self._data = pd.read_excel(file_path)[['Name', 'Firstname', 'Middlename', 'Gender']]
        self._data['Middlename'].fillna('', inplace=True)
        self._name2acro = {}
        self._acro2name = {}
        self._namesearch = {}
        used = {}
        for ind, row in self._data.iterrows():
            acro = row["Firstname"][0] + row["Name"][0]
            if acro not in used:
                used[acro] = 1
            index = str(used[acro])
            used[acro] += 1
            name = f"{row['Firstname']}{' ' + row['Middlename'] if row['Middlename'] else ''} {row['Name']}".title()
            self._acro2name[acro + index] = name
            self._name2acro[name] = [acro + index]
            self._namesearch[name] = row

    def search_acro(self, string):
        ret = []
        for name in self._namesearch:
            if name.lower().startswith(string):
                ret.append((name, self._name2acro[name]))
        return ret

    def search_name(self, string):
        ret = []
        for name in self._namesearch:
            if name.lower().startswith(string):
                ret.append(name)
        return ret