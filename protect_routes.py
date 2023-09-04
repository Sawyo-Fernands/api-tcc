import jwt
import datetime

#Função responsável por gerar o token
def generate_token(username,password,app):
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {
        'exp': expiration_date,
        'iat': datetime.datetime.utcnow(),
        'sub': username,
        'password': password
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

#Função que Verifica se o Token é valido
def verify_token(token,app):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    
    except jwt.ExpiredSignatureError:
        return 'Token expirado. Faça login novamente.'
    except jwt.InvalidTokenError:
        return 'Token inválido. Faça login novamente.'