import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from movie.utils import get_embedding, cosine_similarity  

class Command(BaseCommand):
    help = "Compare two movies and optionally a prompt using OpenAI embeddings"

    def handle(self, *args, **kwargs):
        movie1 = Movie.objects.get(title="Jack and the Beanstalk")
        movie2 = Movie.objects.get(title="Alice in Wonderland")

        #  Generate embeddings of both movies
        emb1 = get_embedding(movie1.description)
        emb2 = get_embedding(movie2.description)

        #  Compute similarity between movies
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(f"🎬 Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}")

        #  Optional: Compare against a prompt
        prompt = "Movie about fantasy"
        prompt_emb = get_embedding(prompt)

        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")