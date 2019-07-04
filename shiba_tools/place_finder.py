import json
import urllib.request

class PlaceFinder():
    def __init__(self, key):
        self._key = key
        self._url_base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={x},{y}&radius={r}&key={key}"
    
    def find_place(self, x, y, r=30):
        request_url = self._url_base.format(x=x, y=y, r=r, key=self._key)
        contents = urllib.request.urlopen(request_url).read()
        results = contents.decode("utf-8")["results"]

        for place in results:
            # TODO process place
            pass