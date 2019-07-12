import base64

def decode_to_png(path):
    with open(path, "rt") as f:
        strs = f.readlines()
    str = ''.join(strs)
    
    imgdata = base64.b64decode(str)

    with open("test.png", 'wb') as f:
        f.write(imgdata)
    
    print(imgdata)

if __name__ == "__main__":
    decode_to_png("qwe@rty.com")