# def Verificar_face(idUsuario):
#     dataUser = request.json
#     imageUser = dataUser['fotoUsuario']

#     # Carregar as imagens do banco de dados
#     my_cursor = mysql.cursor()
#     query = 'SELECT * FROM imagens WHERE id_usuario = %s'
#     my_cursor.execute(query, (idUsuario,))
#     imagem_data = my_cursor.fetchall()

#     nome_pasta = f'usuario-{idUsuario}'
#     os.makedirs(nome_pasta, exist_ok=True)

#     # Decodificar a imagem do usuário
#     user_image = base64.b64decode(imageUser.split(",")[1])
#     img_user = cv2.imdecode(np.frombuffer(user_image, np.uint8), cv2.IMREAD_COLOR)

#     gray_user = cv2.cvtColor(img_user, cv2.COLOR_BGR2GRAY)
    
#     # Ajustar os parâmetros do detectMultiScale
#     faces = face_cascade.detectMultiScale(gray_user, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))

#     if len(faces) > 0:
#         x, y, w, h = faces[0]
#         user_face = gray_user[y:y+h, x:x+w]

#         # Inicializar o reconhecedor LBPH
#         lbph_recognizer = cv2.face.LBPHFaceRecognizer_create()

#         recognized = False
#         confidence_level = 0
#         index = 0

#         for img in imagem_data:
#             img_ = img[1]
#             base64Result = img_.split(",")[1]
#             bytes_decode = base64.b64decode(base64Result)
#             img_db = cv2.imdecode(np.frombuffer(bytes_decode, np.uint8), cv2.IMREAD_COLOR)

#             gray_db = cv2.cvtColor(img_db, cv2.COLOR_BGR2GRAY)
            
#             # Ajustar os parâmetros do detectMultiScale para as imagens do banco de dados
#             db_faces = face_cascade.detectMultiScale(gray_db, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))

#             if len(db_faces) > 0:
#                 x, y, w, h = db_faces[0]
#                 db_face = gray_db[y:y+h, x:x+w]

#                 # Treinar o reconhecedor LBPH com a face do banco de dados
#                 lbph_recognizer.update([db_face], np.array([idUsuario]))

#                 # Realizar o reconhecimento facial
#                 label, confidence = lbph_recognizer.predict(user_face)

#                 if label == idUsuario and confidence >= 50:  # Ajuste o valor de confiança conforme necessário
#                     recognized = True
#                     confidence_level = confidence

#                     break

#             cv2.imwrite(f'{nome_pasta}/imagem-{index}.jpg', img_db)
#             index += 1

#         my_cursor.close()

#         if recognized:
#             result_message = "Usuário reconhecido"
#         else:
#             result_message = "Usuário não reconhecido"

#     else:
#         result_message = "Nenhum rosto encontrado na imagem do usuário"

#     return make_response(
#         jsonify({'result': result_message, 'confidence_level': confidence_level}), 200
#     )
