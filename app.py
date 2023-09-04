from functools import wraps
from flask import Flask, jsonify, make_response, request
import mysql.connector
import base64
import os
import numpy as np
from flask_cors import CORS
import cv2
import os
import base64
import jwt
import datetime

mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password='projetotcc2023',
    database='tcc'
)

app = Flask(__name__)

key = "secret"

CORS(app)  # Isso permite solicitações de todas as origens. Você pode ajustar isso para permitir origens específicas.


print("Versão do OpenCV:", cv2.__version__)

# Carregar o modelo de detecção facial do OpenCV
detectorFace = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Criar o reconhecedor de faces
reconhecedor = cv2.face_EigenFaceRecognizer.create()
# Definir o tamanho das imagens de treinamento (largura, altura)
width, height = 220, 220

# Função responsável por gerar o token
def generate_token(username, password):
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {
        'exp': expiration_date,
        'iat': datetime.datetime.utcnow(),
        'sub': username,
        'password': password
    }
    token = jwt.encode(payload, key, algorithm='HS256')
    return token

# Função que Verifica se o Token é válido
def verify_token(token):
    try:
        payload = jwt.decode(token, key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token expirado. Faça login novamente.'
    except jwt.InvalidTokenError as e:
        return f'Token inválido. Faça login novamente.'

# Verificar se o token é valido
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token de autenticação não enviado!'}), 401
     
        payload = verify_token(token.split(' ')[1])
        if isinstance(payload, str):
            return jsonify({'message': payload}), 401

        return f(token, *args, **kwargs)
    
    return decorated

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

#pegar usuário
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
    query = 'SELECT * FROM users WHERE usuario = %s'
  
    my_cursor.execute(query, (requestData['username'],))

    usuario = my_cursor.fetchall()
    lista_usuarios = list()
    for user in usuario:
        lista_usuarios.append(
            {
                'id':user[0],
                'usuario':user[1],
                'email':user[2],
            }
        )
   
    my_cursor.close()

    if(len(lista_usuarios) > 0) :
        return make_response(
            jsonify(
                type='success',
                mensagem='Usuário presente na base de dados!',
                usuario=lista_usuarios
            ),200)
    else:
        return make_response(
            jsonify(
                type='warning',
                mensagem='Usuário não encontrado!',
                usuario=[]
            ),200)

#criar usuário
@app.route('/usuarios/criar', methods=['POST'])
def incluir_novo_usuario():
    usuario = request.json
    my_cursor = mysql.cursor()

    if 'usuario' in usuario and 'password' in usuario and 'email' in usuario:

        queryVerifyUser = 'SELECT * FROM users WHERE usuario = %s'
        my_cursor.execute(queryVerifyUser,(usuario['usuario'],))
        usuario_verificado = my_cursor.fetchall() 

        queryVerifyEmail = 'SELECT * FROM users WHERE email = %s'
        my_cursor.execute(queryVerifyEmail,(usuario['email'],))
        email_verificado = my_cursor.fetchall()  
        

        # if email_verificado and usuario_verificado:
        #     return make_response(
        #                 jsonify(
        #                     mensagem='Nome de Usuário e e-mail já Cadastrados!',
        #                     type='warning',
        #                 ),
        #                 200  
        #             )
        
        if usuario_verificado:
            return make_response(
                        jsonify(
                            mensagem='Nome de Usuário já Cadastrado!',
                            type='warning',
                        ),
                        200  
                    )

        if email_verificado:
            return make_response(
                        jsonify(
                            mensagem='Email já Cadastrado!',
                            type='warning',
                        ),
                        200  
                    )
        
        else:
            query = "INSERT INTO users (usuario, password, email) VALUES (%s, %s, %s)"
            values = (usuario['usuario'], usuario['password'], usuario['email'])

            my_cursor.execute(query,values)
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

#Adicionar imagem de usuário
@app.route('/imagens/visualizar', methods=['GET'])
def visualizar_imagens():
    idUsuario = request.args.get('usuarioId', type=int)
    paginacao = request.args.get('paginacao', type=int)
    my_cursor = mysql.cursor()
  
    if idUsuario:
        query = "SELECT * FROM imagens WHERE id_usuario = %s"
        if(paginacao > 0) :
             query = "SELECT * FROM imagens WHERE id_usuario = %s LIMIT %s"

        values = (idUsuario,paginacao)

        listaImagens = list()
        my_cursor.execute(query, values)
        fotos_user = my_cursor.fetchall()
        for image in fotos_user:
            listaImagens.append(
                {
                    'idImagem':image[0],
                    'imagemBase64':image[1],
                }
            )
   
        my_cursor.close()

        return make_response(
            jsonify(
               listaImagens
            ),
            200  
        )
    else:
        return jsonify({"mensagem": "Informe o Id do usuário.",'type':"warning"}), 400  

#Verificar Rosto Usuário
@app.route('/usuarios/verificarRosto', methods=['POST'])
@token_required
def recognize_face(token):
    data = request.json
    image_base64 = data['fotoUsuario']
    id_usuario = data['idUsuario']
    
    my_cursor = mysql.cursor()
    query = 'SELECT * FROM imagens'
    my_cursor.execute(query)
    imagens_data = my_cursor.fetchall()

    user_image = np.frombuffer(base64.b64decode(image_base64.split(",")[1]), np.uint8)
    user_image = cv2.imdecode(user_image, cv2.IMREAD_COLOR)

    gray_user = cv2.cvtColor(user_image, cv2.COLOR_BGR2GRAY)

    faceDetect = detectorFace.detectMultiScale(
        gray_user,
        scaleFactor=1.1,
        minSize=(35, 35),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    recognized = False
    confidence_level = 0
    user_info = None

    if len(faceDetect) > 0:
        x, y, w, h = faceDetect[0]
        user_face = gray_user[y:y+h, x:x+w]

        user_face_resized = cv2.resize(user_face, (width, height))

        labels = []
        face_images = []
       
        for img_data in imagens_data:
            img = img_data[1]
            bytes_decode = base64.b64decode(img.split(",")[1])
            img_db = cv2.imdecode(np.frombuffer(bytes_decode, np.uint8), cv2.IMREAD_COLOR)
            gray_db = cv2.cvtColor(img_db, cv2.COLOR_BGR2GRAY)
            db_face_resized = cv2.resize(gray_db, (width, height))

            face_images.append(db_face_resized)
            labels.append(img_data[2])

        reconhecedor.train(face_images, np.array(labels))
        label, confidence = reconhecedor.predict(user_face_resized)

        if label == id_usuario:
            recognized = True
            confidence_level = confidence

            cursor = mysql.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (id_usuario,))
            user_info = cursor.fetchone()

    if recognized:
        result_message = "Usuário reconhecido"
        bolReconhecido=True
    else:
        result_message = "Usuário não reconhecido"
        bolReconhecido=False
    response_data = {
        'mensagem': result_message,
        'confidence_level': confidence_level,
        'user_info': user_info,
        'reconhecido':bolReconhecido
    }

    return make_response(jsonify(response_data), 200)

#autenticar usuário
@app.route('/usuarios/gerarToken', methods=['POST'])
def auth_usuario():
    requestData = request.json
    # Decodificar a string Base64
    decoded_bytes = base64.b64decode(requestData['username'])
    # Converta os bytes decodificados de volta para uma string
    userNameDecode = decoded_bytes.decode('utf-8')
    my_cursor = mysql.cursor()
    query = 'SELECT * FROM users WHERE usuario = %s AND password = %s'
  
    my_cursor.execute(query, (userNameDecode,requestData['password']))
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
    token = generate_token(userNameDecode,requestData['password'])
    if(len(lista_usuarios) > 0) :
        return make_response(
            jsonify(
                type='success',
                mensagem='Usuário reconhecido com sucesso!',
                usuario= lista_usuarios,
                token = token
            ),200)
    else:
        return make_response(
            jsonify(
                type='warning',
                mensagem='Usuário não reconhecido!',
                usuario=[],
                token=''
            ),200)

#Listar itens
@app.route('/itens/listar', methods=['GET'])
@token_required
def itens_listar(token):
    idUsuario = request.args.get('idUsuario', type=int)
    my_cursor = mysql.cursor()
    if(idUsuario) :
        query = 'SELECT * FROM itensEstoque WHERE idUsuarioCriador = %s'
        my_cursor.execute(query, (idUsuario))
    else:
        query = 'SELECT * FROM itensEstoque'
        my_cursor.execute(query)

    itens = my_cursor.fetchall()
    lista_itens = [
        {
            'idItem': item[0],
            'nomeItem': item[1],
            'dataCriacao': item[2],
            'valorItem': item[3],
            'usuarioCriadorId': item[4],
            'nomeUsuarioCriador': item[5],
            'descricaoItem': item[6],
        }
        for item in itens
    ]
   
    my_cursor.close()

    if(len(lista_itens) > 0) :
        return make_response(
            jsonify(
                lista_itens
            ),200)
    else:
        return make_response(
            jsonify(
                lista_itens
            ),200)

#Remover Itens
@app.route('/itens/remover', methods=['POST'])
@token_required
def itens_remover(token):
    requestData = request.json
    my_cursor = mysql.cursor()
    if(requestData['itemId']) :
        query = 'DELETE  FROM itensEstoque WHERE itemId = %s'
        my_cursor.execute(query, (requestData['itemId'],))
    else:
         return make_response(
            jsonify(
                type='warning',
                mensagem='Informe o id do item!'
            ),200)
    mysql.commit()
    my_cursor.close()

    return make_response(
            jsonify(
                mensagem='Item removido com sucesso!',
                type='success',
                id=requestData['itemId']
            ),
            200  
        )

#Criar Itens
@app.route('/itens/criar', methods=['POST'])
@token_required
def itens_criar(token):
    requestData = request.json
    my_cursor = mysql.cursor()
    data_hora_atual = datetime.datetime.now()
    novo_id = 0
    if 'nomeItem' in requestData and 'valorItem' in requestData and 'idUsuarioCriador' in requestData and 'nomeUsuarioCriador' in requestData and 'descricao' in requestData:
        query = "INSERT INTO itensEstoque (nomeItem, valorItem, idUsuarioCriador, nomeUsuarioCriador, descricao) VALUES (%s, %s, %s, %s, %s)"
        my_cursor.execute(query, (requestData['nomeItem'],requestData['valorItem'],requestData['idUsuarioCriador'],requestData['nomeUsuarioCriador'],requestData['descricao']))
        novo_id = my_cursor.lastrowid 
    else:
         return make_response(
            jsonify(
                type='warning',
                mensagem='Preencha todos os campos!'
            ),200)
    mysql.commit()
    my_cursor.close()

    return make_response(
            jsonify(
                mensagem='Item adicionado com sucesso!',
                type='success',
                item={
            'idItem': novo_id,
            'nomeItem': requestData['nomeItem'],
            'dataCriacao': data_hora_atual.strftime('%Y-%m-%d %H:%M:%S'),
            'valorItem': requestData['valorItem'],
            'usuarioCriadorId': requestData['idUsuarioCriador'],
            'nomeUsuarioCriador': requestData['nomeUsuarioCriador'],
            'descricaoItem': requestData['descricao'],
        }
            ),
            200  
        )

#Alterar Valor Item
@app.route('/itens/alterarValor', methods=['POST'])
@token_required
def itens_alterar_valor(token):
    requestData = request.json
    my_cursor = mysql.cursor()
    novo_id = 0
    if 'itemId' in requestData and 'valorItem' in requestData:
        query = "UPDATE itensEstoque SET valorItem = %s WHERE itemId = %s"
        my_cursor.execute(query, (requestData['valorItem'],requestData['itemId']))

    else:
         
         return make_response(
            jsonify(
                type='warning',
                mensagem='Preencha todos os campos!'
            ),200)
    mysql.commit()
    my_cursor.close()
    print(novo_id)
    return make_response(
            jsonify(
                mensagem = 'Valor do item alterado com sucesso!',
                type='success',
                id=requestData['itemId']
            ),
            200  
        )


app.run(host='localhost',port=5000,debug=True)