from drafter import *
from PIL import Image as PILImage
from dataclasses import dataclass

def encodemessage(message:str):
    fmessage = []
    return [format(ord(char), "08b") for char in message]

def pixelator(pix:str,message:str):
    binarylist = encodemessage(message)
    lenbinary = len(binarylist)
    ipix = iter(pix)
    for i in range(lenbinary):
        pixels = [value for value in next(ipix)[:3] + next(ipix)[:3] + next(ipix)[:3]]
        for p in range(8):
            if binarylist[i][p] == '0' and pixels[p] % 2 != 0:
                pixels[p] -= 1
            elif binarylist[i][p] == '1' and pixels[p] % 2 == 0:
                pixels[p] = pixels[p] - 1 if pixels[p] != 0 else pixels[p] + 1
        if i == lenbinary - 1:
            pixels[-1] |= 1
        else:
            pixels[-1] &= ~1
        yield tuple(pixels[:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

def encodeimage(newimg, message):
    w = newimg.size[0]
    (x, y) = (0, 0)
    for pixel in pixelator(newimg.getdata(), message):
        newimg.putpixel((x, y), pixel)
        x = 0 if x == w - 1 else x + 1
        y += 1 if x == 0 else 0

def encode(message:str):
    img = PILImage.open("original.png","r")
    newimg = img.copy()
    encodeimage(newimg,message)
    newimg.save("secret.png")

def decode():
    img = "secret.png"
    image = PILImage.open(img,"r")
    imgdata = iter(image.getdata())
    data = ""
    
    while True:
        pixels = [value for value in next(imgdata)[:3] + next(imgdata)[:3] + next(imgdata)[:3]]
        binstr = ''.join(['1' if i % 2 else '0' for i in pixels[:8]])
        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            break
    return data

@dataclass
class State:
    message:str
    code:str

@dataclass
class Encryption:
    message:str
    code:str

@route
def index(state:State)->Page:
    return Page(state,["Welcome to the steganography site, please select if youd want to decrypt or encrypt a message.",
                       Button("Encrypt Message", encrypt),
                       Button("Decrypt Message",decrypt)
                       ])

@route
def encrypt(state:State)->Page:
    return Page(state, [Image("original.png"),
                        "Encrypt Message into this image?",
                        Button("Back",index),
                        TextBox("Encryptionmessage","Insert Message to encrypt"),
                        TextBox("Encryptioncode","Insert Password to encrypt by"),
                        Button("Encrypt!",encryptionresult)
                        ])

@route
def decrypt(state:State)->Page:
    return Page(state, ["Decrypt Message?",
                        Button("Back",index),
                        TextBox("Decryptioncode","Insert Decryption Code"),
                        Button("Decrypt",decryptresult)
                        ])

@route
def encryptionresult(state:State,Encryptionmessage:str,Encryptioncode:str)->Page:
    state.message = Encryptionmessage
    state.code = Encryptioncode
    encode(Encryptionmessage)
    return Page(state,[Image("secret.png"),
                       "Message Encoded.",
                       Button("Return to Start",index)
                       ])

@route
def decryptresult(state:State, Decryptioncode:str)->Page:
    if Decryptioncode != state.code:
        return Page(state,["Incorrect Decryption code.",Button("Try Again",decrypt),Button("Return to start",index)
                           ])
    return Page(state,["Your Decrypted message:" + decode(),
                       Button("Return to Start",index)
                       ])

start_server(State("", ""))
