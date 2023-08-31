
from flask import Flask, jsonify, make_response, request
import mysql.connector
import PIL.Image as Image
import base64
from io import BytesIO
import os
import numpy as np
from flask_cors import CORS
import numpy as np
import tensorflow as tf
import cv2
import openface
from scipy.spatial import distance

mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password='projetotcc2023',
    database='tcc'
)

app = Flask(__name__)

CORS(app)  # Isso permite solicitações de todas as origens. Você pode ajustar isso para permitir origens específicas.

modelDir = 'models/'
net = openface.TorchNeuralNet(modelDir=modelDir, cuda=False)


@app.route('/usuarios/verificarRosto', methods=['POST'])
def Verificar_face():
    dataUser = request.json
    imageUser = dataUser['fotoUsuario']
    idUsuario = dataUser['idUsuario']
    my_cursor = mysql.cursor()
    # query = 'SELECT * FROM imagens WHERE id_usuario = %s'
    query = 'SELECT * FROM imagens'
    # my_cursor.execute(query,(idUsuario,))
    my_cursor.execute(query)

    imagem_data = my_cursor.fetchall()

     # Decodificar a imagem do usuário
    user_image = cv2.imdecode(
        bytes.fromhex(imageUser.split(",")[1]),
        cv2.IMREAD_COLOR
    )
    faceUser = net.forward(user_image)

    # Detectar rostos nas imagens do banco de dados e obter suas características
    facesDB = []
    featuresDB = []
    for imgPath in imagem_data:
        image_db = cv2.imread(imgPath)
        face_db = net.forward(image_db)
        facesDB.append(face_db)
        featuresDB.append(face_db[0])

    similarity_threshold = 0.5

    recognized = False
    user_info = None

    for idx, features in enumerate(featuresDB):
        dist = distance.cosine(faceUser[0], features)
        
        if dist < similarity_threshold:
            recognized = True
            user_info = idx  # ou informações sobre o usuário correspondente
            break

    if recognized:
        result_message = "Usuário reconhecido"
    else:
        result_message = "Usuário não reconhecido"

    response_data = {
        'result': result_message,
        'user_info': user_info
    }

    return jsonify(response_data)

