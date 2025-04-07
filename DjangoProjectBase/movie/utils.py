import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv('../api_keys.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

# Función para obtener embeddings
def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# Función para calcular similitud de coseno
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))