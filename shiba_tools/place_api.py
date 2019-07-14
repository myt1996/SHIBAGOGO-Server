import urllib.request
import json

myt_api_key = "AIzaSyC9Dnt3CPN-jb9GeLBiajk9IPwlz0S9wOs"
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={x},{y}&radius={r}&key={key}"


def find_place(x, y, r=30):
    request_url = url.format(x=x, y=y, r=r, key=myt_api_key)
    contents = urllib.request.urlopen(request_url).read()
    results = json.loads(contents.decode("utf-8"))["results"]
    for info in results:
        # print(info)
        if "political" in info["types"] or "locality" in info["types"] or "sublocality" in info["types"] or "route" in info["types"]:
            continue
        return info
    return None

if __name__ == "__main__":
    place_info = find_place(34.979495, 135.964372)
    print(place_info)