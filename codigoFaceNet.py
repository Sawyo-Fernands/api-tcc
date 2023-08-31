
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def validate_user():
    dataUser = request.json
    imageUser = dataUser['fotoUsuario']
    idUsuario = dataUser['idUsuario']

    # Carregar as imagens do banco de dados
    my_cursor = mysql.cursor()
    query = 'SELECT * FROM imagens WHERE id_usuario = %s'
    my_cursor.execute(query, (idUsuario,))
    imagem_data = my_cursor.fetchall()

    # Decodificar a imagem do usuário
    user_image = base64.b64decode(imageUser.split(",")[1])
    img_user = cv2.imdecode(np.frombuffer(user_image, np.uint8), cv2.IMREAD_COLOR)
    img_user_rgb = cv2.cvtColor(img_user, cv2.COLOR_BGR2RGB)

    # Detectar rostos na imagem do usuário usando MTCNN
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

        # Detectar rostos nas imagens do banco de dados usando MTCNN
        boxes, _ = mtcnn.detect(img_db_rgb)
        
        if boxes is None:
            continue

        db_faces = []
        for box in boxes:
            x, y, x1, y1 = box
            db_face = img_db_rgb[int(y):int(y1), int(x):int(x1)]
            db_faces.append(db_face)

        # Extrair embeddings das faces do usuário e do banco de dados
        user_embedding = resnet(torch.from_numpy(np.expand_dims(user_face.transpose(2, 0, 1), axis=0).astype(np.float32)))
        db_embedding = resnet(torch.from_numpy(np.expand_dims(db_faces[0].transpose(2, 0, 1), axis=0).astype(np.float32)))

        # Calcular distância Euclidiana entre os embeddings
        distance = np.linalg.norm(user_embedding.detach().numpy() - db_embedding.detach().numpy())

        if distance < similarity_threshold:
            recognized = True
            confidence_level = 1 - distance  # Ajuste conforme necessário
            break

    my_cursor.close()

    if recognized:
        result_message = "Usuário reconhecido"
    else:
        result_message = "Usuário não reconhecido"

    return make_response(
        jsonify({'result': result_message, 'confidence_level': confidence_level}), 200
    )