# @app.route('/usuarios/verificarRosto/<int:idUsuario>', methods=['POST'])
# def Verificar_face(idUsuario):
#     dataUser = request.json
#     imageUser = dataUser['fotoUsuario']
#     my_cursor = mysql.cursor()
#     query = 'SELECT * FROM imagens WHERE id_usuario = %s'
#     my_cursor.execute(query,(idUsuario,))
#     imagem_data = my_cursor.fetchall()
#     index = 0

#     nome_pasta = f'usuario-{idUsuario}'
#     os.makedirs(nome_pasta, exist_ok=True)

#     for img in imagem_data:
#         img_ = img[1]
#         base64Result = img_.split(",")[1]
#         bytes_decode = base64.b64decode(base64Result)
#         img = Image.open(BytesIO(bytes_decode))
#         # img.show()  mostrar as imagens
#         out_jpg=img.convert('RGB')
#         nome_arquivo = f'{nome_pasta}/imagem-{index}.jpg'
#         out_jpg.save(nome_arquivo)
#         index +=1
#     my_cursor.close()
#     index = 0
#     return make_response(
#         jsonify(
#         {'result':"MENSAGEM DE USUÁRIO RECONHECIDO OU NÃO E SEUS DADOS"},200
#         )
#     )