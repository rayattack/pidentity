class Ref(object):
    def __init__(self, key: str):
        self._key = key

    @property
    def key(self):
        return self._key

    def extract(self):
        walkway = self._key.split('.')
        data = self._payload.get(walkway[0])
        for step in walkway[1:]:
            data = data.get(step)
        return data


class Rule(object):
    def __init__(self, symbol: str, value: any):
        self._payload = {
            'sym': symbol,
            'val': value
        }

    @property
    def operator(self):
        return self._payload.get('sym')

    @property
    def value(self):
        return self._payload.get('val')
