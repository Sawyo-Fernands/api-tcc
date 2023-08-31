def Verificar_face(idUsuario):
    dataUser = request.json
    imageUser = dataUser['fotoUsuario']

    # Carregar as imagens do banco de dados
    my_cursor = mysql.cursor()
    query = 'SELECT * FROM imagens WHERE id_usuario = %s'
    my_cursor.execute(query, (idUsuario,))
    imagem_data = my_cursor.fetchall()

    nome_pasta = f'usuario-{idUsuario}'
    os.makedirs(nome_pasta, exist_ok=True)

    # Decodificar a imagem do usuário
    user_image = base64.b64decode(imageUser.split(",")[1])
    img_user = cv2.imdecode(np.frombuffer(user_image, np.uint8), cv2.IMREAD_COLOR)

    gray_user = cv2.cvtColor(img_user, cv2.COLOR_BGR2GRAY)

    # Ajustar os parâmetros do detectMultiScale
    faces = face_cascade.detectMultiScale(gray_user, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        x, y, w, h = faces[0]
        user_face = gray_user[y:y+h, x:x+w]

        # Inicializar o reconhecedor Eigenfaces
        eigen_recognizer = cv2.face_EigenFaceRecognizer.create()

        recognized = False
        confidence_level = 0

        face_images = []
        labels = []

        user_face_resized = cv2.resize(user_face, (100, 100))  # Redimensionar a imagem do usuário

        for img in imagem_data:
            img_ = img[1]
            base64Result = img_.split(",")[1]
            bytes_decode = base64.b64decode(base64Result)
            img_db = cv2.imdecode(np.frombuffer(bytes_decode, np.uint8), cv2.IMREAD_COLOR)

            gray_db = cv2.cvtColor(img_db, cv2.COLOR_BGR2GRAY)
            db_face_resized = cv2.resize(gray_db, (100, 100))  # Redimensionar as imagens do banco de dados

            face_images.append(db_face_resized)
            labels.append(idUsuario)

            cv2.imwrite(f'{nome_pasta}/imagem-{len(face_images)}.jpg', db_face_resized)

        # Treinar o reconhecedor Eigenfaces
        eigen_recognizer.train(face_images, np.array(labels))

        # Realizar o reconhecimento facial
        label, confidence = eigen_recognizer.predict(user_face_resized)

        # Normalizar o valor de confiança para uma escala de 0 a 100
        normalized_confidence = 100 - confidence / 100.0  # Dividir por 100.0 para obter um valor entre 0 e 1
        print(confidence)
        print(normalized_confidence)
        if label == idUsuario and normalized_confidence >= 70:  # Ajuste o valor de confiança conforme necessário
            recognized = True
            confidence_level = normalized_confidence 

        my_cursor.close()

        if recognized:
            result_message = "Usuário reconhecido"
        else:
            result_message = "Usuário não reconhecido"

    else:
        result_message = "Nenhum rosto encontrado na imagem do usuário"

    return make_response(
        jsonify({'result': result_message, 'confidence_level': confidence_level}), 200
    )
