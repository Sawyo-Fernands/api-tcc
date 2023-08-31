from flask import Flask, jsonify, make_response, request
import mysql.connector
import PIL.Image as Image
import base64
from io import BytesIO
import os
import cv2
import numpy as np
from flask_cors import CORS
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1


mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password='projetotcc2023',
    database='tcc'
)

app = Flask(__name__)

CORS(app)  # Isso permite solicitações de todas as origens. Você pode ajustar isso para permitir origens específicas.

mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()


#listar usuários
@app.route('/usuarios/listar',methods=['GET'])
def obter_usuarios():
    my_cursor = mysql.cursor()
    my_cursor.execute('SELECT * FROM users')
    usuarios = my_cursor.fetchall()
    lista_usuarios = list()
    for user in usuarios:
        lista_usuarios.append(
            {
                'id':user[0],
                'usuario':user[1],
                'email':user[3],
            }
        )
    my_cursor.close() 
    return jsonify(lista_usuarios,200)

#listar usuário
@app.route('/usuarios/listarUsuario/<int:idUsuario>',methods=['GET'])
def obter_usuario_por_id(idUsuario):
    my_cursor = mysql.cursor()
    query = 'SELECT * FROM users WHERE id = %s'
    my_cursor.execute(query,(idUsuario,))
    usuario = my_cursor.fetchall()
    lista_usuarios = list()
    for user in usuario:
        lista_usuarios.append(
            {
                'id':user[0],
                'usuario':user[1],
                'email':user[3],
            }
        )
    my_cursor.close()
    if(len(lista_usuarios) > 0) :
        return make_response(
            jsonify(
                type='success',
                mensagem='Usuário encontrado com sucesso!',
                usuario=lista_usuarios
            ),200)
    else:
        return make_response(
            jsonify(
                type='warning',
                mensagem='Usuário não encontrado!',
                usuario=[]
            ),200)

#Verificar usuário
@app.route('/usuarios/consultar',methods=['POST'])
def obter_usuario():
    requestData = request.json
    my_cursor = mysql.cursor()
    query = 'SELECT * FROM users WHERE usuario = %s AND password = %s'
  
    my_cursor.execute(query, (requestData['username'], requestData['senha']))

    usuario = my_cursor.fetchall()
    lista_usuarios = list()
    for user in usuario:
        lista_usuarios.append(
            {
                'id':user[0],
                'usuario':user[1],
                'email':user[3],
            }
        )
   
    my_cursor.close()

    if(len(lista_usuarios) > 0) :
        return make_response(
            jsonify(
                type='success',
                mensagem='Usuário encontrado com sucesso!',
                usuario=lista_usuarios
            ),200)
    else:
        return make_response(
            jsonify(
                type='warning',
                mensagem='Usuário não encontrado com sucesso!',
                usuario=[]
            ),200)

#criar usuário
@app.route('/usuarios/criar', methods=['POST'])
def incluir_novo_usuario():
    usuario = request.json
    my_cursor = mysql.cursor()
    print(usuario)
    if 'usuario' in usuario and 'password' in usuario and 'email' in usuario:
        query = "INSERT INTO users (usuario, password, email) VALUES (%s, %s, %s)"
        values = (usuario['usuario'], usuario['password'], usuario['email'])

        my_cursor.execute(query, values)
        mysql.commit()
        novo_id = my_cursor.lastrowid 
        my_cursor.close()

        return make_response(
            jsonify(
                mensagem='Usuário cadastrado com sucesso!',
                usuario=usuario,
                type='success',
                id=novo_id
            ),
            200  
        )
    else:
        return jsonify({"mensagem": "Campos faltando.",'type':"warning"}), 400  

#Adicionar imagem de usuário
@app.route('/imagens/criar', methods=['POST'])
def incluir_nova_imagem():
    data_requisicao = request.json
    my_cursor = mysql.cursor()
  
    if 'imagem' in data_requisicao and 'idUsuario' in data_requisicao:
        query = "INSERT INTO imagens (imagem, id_usuario) VALUES (%s, %s)"
        values = (data_requisicao['imagem'], data_requisicao['idUsuario'])

        my_cursor.execute(query, values)
        mysql.commit()
        novo_id = my_cursor.lastrowid 
        my_cursor.close()

        return make_response(
            jsonify(
                mensagem='Imagem cadastrado com sucesso!',
                usuario=data_requisicao,
                type='success',
                id=novo_id
            ),
            200  
        )
    else:
        return jsonify({"mensagem": "Campos faltando.",'type':"warning"}), 400  


#Verificar Usuário
@app.route('/usuarios/verificarRosto', methods=['POST'])
def recognize_face():
    dataUser = request.json
    imageUser = dataUser['fotoUsuario']
    idUsuario = dataUser['idUsuario']

    my_cursor = mysql.cursor()
    query = 'SELECT * FROM imagens'
    my_cursor.execute(query)
    imagem_data = my_cursor.fetchall()

    user_image = np.frombuffer(base64.b64decode(imageUser.split(",")[1]), np.uint8)
    img_user = cv2.imdecode(user_image, cv2.IMREAD_COLOR)
    img_user_rgb = cv2.cvtColor(img_user, cv2.COLOR_BGR2RGB)

    boxes, _ = mtcnn.detect(img_user_rgb)
    
    if boxes is None:
        result_message = "Nenhum rosto detectado na imagem do usuário"
        return make_response(
            jsonify({'result': result_message}), 400
        )

    user_faces = []
    for box in boxes:
        x, y, x1, y1 = box
        user_face = img_user_rgb[int(y):int(y1), int(x):int(x1)]
        user_faces.append(user_face)

    similarity_threshold = 0.7  # Defina um limiar de similaridade adequado

    recognized = False
    confidence_level = 0

    for img in imagem_data:
        img_ = img[1]
        base64Result = img_.split(",")[1]
        bytes_decode = base64.b64decode(base64Result)
        img_db = cv2.imdecode(np.frombuffer(bytes_decode, np.uint8), cv2.IMREAD_COLOR)
        img_db_rgb = cv2.cvtColor(img_db, cv2.COLOR_BGR2RGB)

        boxes, _ = mtcnn.detect(img_db_rgb)
        
        if boxes is None:
            continue

        db_faces = []
        for box in boxes:
            x, y, x1, y1 = box
            db_face = img_db_rgb[int(y):int(y1), int(x):int(x1)]
            db_faces.append(db_face)

        for db_face in db_faces:
            user_embedding = resnet(torch.from_numpy(np.expand_dims(user_face.transpose(2, 0, 1), axis=0).astype(np.float32)))
            db_embedding = resnet(torch.from_numpy(np.expand_dims(db_face.transpose(2, 0, 1), axis=0).astype(np.float32)))

            distance = np.linalg.norm(user_embedding.detach().numpy() - db_embedding.detach().numpy())

            if distance < similarity_threshold:
                recognized = True
                confidence_level = distance  # Ajuste conforme necessário
                break

        if recognized:
            break

    my_cursor.close()

    if recognized:
        result_message = "Usuário reconhecido"
    else:
        result_message = "Usuário não reconhecido"

    return make_response(
        jsonify({'result': result_message, 'confidence_level': float(confidence_level)}), 200
    )

app.run(host='localhost',port=5000,debug=True)