import websocket
import json

import pickle
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

# https://github.com/aspnet/SignalR/blob/release/2.2/specs/HubProtocol.md

ws = None

# Cargar el modelo
modelo = load_model('modelo_texto_final.h5')

# Cargar el Tokenizer
with open('tokenizer.pkl', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Cargar el LabelEncoder
with open('label_encoder.pkl', 'rb') as handle:
    label_encoder = pickle.load(handle)

max_longitud = modelo.layers[0].input_shape[1]

# Funció per a preprocesar el text
def preprocesar_texto(texto, tokenizer, max_longitud):
    secuencia = tokenizer.texts_to_sequences([texto])
    secuencia_pad = pad_sequences(secuencia, maxlen=max_longitud, padding='post')
    return secuencia_pad


# Funció per a predir categories
def predecir_categorias(texto, modelo, tokenizer, max_longitud):
    secuencia_pad = preprocesar_texto(texto, tokenizer, max_longitud)
    predicciones = modelo.predict(secuencia_pad)
    top_indices = predicciones.argsort()[0][-12:][::-1]
    top_categorias = label_encoder.inverse_transform(top_indices)
    top_porcentajes = predicciones[0][top_indices]

    top_porcentajes = [x for x in top_porcentajes if x >= 0.01]

    top_categorias_con_porcentaje = [(cat, porc) for cat, porc in zip(top_categorias, top_porcentajes) if porc >= 0.05]
    if len(top_categorias_con_porcentaje) > 3:
        top_porcentajes = [x for x in top_porcentajes if x >= 0.05]

    else:
        top_porcentajes = top_porcentajes[:3]



    return top_categorias, top_porcentajes


def encode_json(obj):
    # All JSON messages must be terminated by the ASCII character 0x1E (record separator).
    # Reference: https://github.com/aspnet/SignalR/blob/release/2.2/specs/HubProtocol.md#json-encoding
    return json.dumps(obj) + chr(0x1e)

def ws_on_message(ws, message: str):
    ignore_list = ['{"type":6}', '{}']
    # Split using record seperator, as records can be received as one message
    for msg in message.split(chr(0x1E)):
        if msg and msg not in ignore_list:
            msg_decoded = json.loads(msg)
            if(msg_decoded['target'] == 'connectionId'):
                global connectionId 
                connectionId = msg_decoded['arguments'][0]

                ws.send(encode_json({
                    "type": 1,
                    "target": "conectClientPython",
                    "arguments": [connectionId]
                }))
            elif(msg_decoded['target'] == 'messageForIA'):
                top_categorias, top_porcentajes = predecir_categorias(msg_decoded['arguments'][1], modelo, tokenizer, max_longitud)
                text = text=f"{'<br/>'.join([f'{cat} ({porcentaje:.2%})' for cat, porcentaje in zip(top_categorias, top_porcentajes)])}"
                ws.send(encode_json({
                    "type": 1,
                    "target": "newMessage",
                    "arguments": [33, text, msg_decoded['arguments'][2]]
                }))

def ws_on_error(ws, error):
    print(error)

def ws_on_close(ws):
    print("### Disconnected from SignalR Server ###")

def ws_on_open(ws):
    print("### Connected to SignalR Server via WebSocket ###")
    
    # Do a handshake request
    print("### Performing handshake request ###")
    ws.send(encode_json({
        "protocol": "json",
        "version": 1
    }))

    # Handshake completed
    print("### Handshake request completed ###")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://172.16.0.10:5000/hub",
                              on_message = ws_on_message,
                              on_error = ws_on_error,
                              on_close = ws_on_close,
                              on_open = ws_on_open)
    # ws.on_open = ws_on_open
    ws.run_forever()

