import os
import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Selecciona una película al azar y muestra sus embeddings"

    def handle(self, *args, **kwargs):
        # Obtener todas las películas con embeddings almacenados
        movies_with_emb = Movie.objects.exclude(emb__isnull=True).exclude(emb=b'')
        
        if not movies_with_emb.exists():
            self.stderr.write("❌ No hay películas con embeddings almacenados.")
            return
        
        # Seleccionar una película al azar
        movie = random.choice(movies_with_emb)
        
        # Convertir los embeddings binarios a un array de numpy
        emb_array = np.frombuffer(movie.emb, dtype=np.float32)
        
        # Mostrar información
        self.stdout.write(self.style.SUCCESS(f" Película seleccionada: {movie.title}"))
        self.stdout.write(f" Primeros 10 valores del embedding: {emb_array[:10]}")
