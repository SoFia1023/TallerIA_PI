from django.shortcuts import render
from movie.models import Movie
from movie.utils import get_embedding, cosine_similarity  
import numpy as np


def recommendations(request):
    if request.method == "POST":
        prompt = request.POST.get("prompt", "")
        if not prompt:
            return render(request, "recommendations.html", {"error": "Por favor, ingresa un prompt"})

        # Obtener embedding del prompt
        prompt_embedding = get_embedding(prompt)

        # Obtener todas las películas y comparar similitud
        movies = Movie.objects.all()
        best_match = None
        best_score = -1

        for movie in movies:
            movie_embedding = np.frombuffer(movie.emb, dtype=np.float32)  
            score = cosine_similarity(prompt_embedding, movie_embedding)  

            if score > best_score:
                best_score = score
                best_match = movie

        return render(request, "results.html", {"movie": best_match, "score": best_score})

    return render(request, "recommendations.html")