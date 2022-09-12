from fastapi import FastAPI
from pydantic import BaseModel
import matplotlib.pyplot as plt
import numpy as np
import random
import heartpy as hp
import scipy.io as sio
import base64
from fastapi.middleware.cors import CORSMiddleware

import io


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://ecg-plus.herokuapp.com",
    "http://ecg-plus.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Body(BaseModel):
    nameFile: str
    b64: str

@app.post("/ecg/")
async def create_item(body: Body):
    body.b64 = str.encode(body.b64)
    print(body)
    return getDataFromEcg(body.nameFile, body.b64)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

def getDataFromEcg (nameFile, b64):
    fh = open(nameFile, "wb")
    fh.write(base64.decodebytes(b64))
    fh.close()

    ecg = sio.loadmat(nameFile)['val'].reshape((-1))

    fs = 360
    time = np.arange(ecg.size) / fs
    plt.plot(time, ecg)
    plt.xlabel("Tiempo en segundos")
    plt.ylabel("ECG")
    lim = random.SystemRandom().uniform(0, 5)
    wd, m = hp.process(ecg, 250)

    # visualise in plot of custom size
    hp.plotter(wd, m)
    print(m)
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    d = dict();
    d['info'] = m
    d['b64'] = base64.b64encode(my_stringIObytes.read())
    return d

