import os
import unicodedata
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie
from PIL import Image

class Command(BaseCommand):
    help = "Update movie images in the database from the media folder"

    def normalize_title(self, title):
        """Normaliza el título eliminando prefijos, acentos y convirtiendo a minúsculas."""
        title = title.lower().strip()
        title_no_accents = ''.join(
            c for c in unicodedata.normalize('NFKD', title) if unicodedata.category(c) != 'Mn'
        )  # Mantiene caracteres pero sin acentos
        return title_no_accents

    def convert_to_jpg(self, file_path):
        """Intenta convertir un archivo a JPG."""
        try:
            # Intentar abrir y convertir el archivo
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                new_path = file_path + '.jpg'
                img.save(new_path, 'JPEG', quality=85)
            
            # Si la conversión fue exitosa, eliminar el original
            if os.path.exists(new_path):
                os.remove(file_path)
                return os.path.basename(new_path)
            return None
        except Exception as e:
            self.stderr.write(f"Error converting file {file_path}: {str(e)}")
            return None

    def find_movie_by_title(self, title):
        """Busca película manejando títulos con dos puntos y otros caracteres especiales."""
        try:
            # Limpia el título del archivo
            clean_title = title.replace('m_', '').strip().lower()
            
            # Buscar todas las películas
            movies = Movie.objects.all()
            
            for movie in movies:
                # Obtener la parte principal del título (antes de los dos puntos)
                db_title_parts = movie.title.split(':')[0].strip().lower()
                
                # Comparar la parte principal
                if clean_title == db_title_parts:
                    return movie
                    
                # Si no hay coincidencia exacta, buscar como parte del título
                if clean_title in db_title_parts or db_title_parts in clean_title:
                    return movie
                    
            return None
        except Exception as e:
            self.stderr.write(f"Error searching for movie: {str(e)}")
            return None

    def should_skip_file(self, filename):
        """Determina si un archivo debe ser ignorado."""
        # Lista de archivos del sistema y sus variantes
        SYSTEM_FILES = {
            'Captura', 'Captura.jpg', 'Captura.png',
            'default', 'default.jpg', 'default.png',
            'Sin_título', 'Sin_título.jpg', 'Sin_título.png'
        }
        
        base_name = os.path.splitext(filename)[0]
        return base_name in SYSTEM_FILES or filename in SYSTEM_FILES

    def handle(self, *args, **kwargs):
        # Ruta de la carpeta donde están las imágenes
        images_folder = os.path.join(settings.MEDIA_ROOT, 'movie', 'images')

        if not os.path.exists(images_folder):
            self.stderr.write(f"Folder '{images_folder}' not found.")
            return

        updated_count = 0

        # Recorremos los archivos en la carpeta
        for filename in os.listdir(images_folder):
            # Verificar si el archivo debe ser ignorado
            if self.should_skip_file(filename):
                self.stdout.write(self.style.WARNING(f"Skipping system file: {filename}"))
                continue

            file_path = os.path.join(images_folder, filename)

            # Si el archivo no tiene una extensión reconocida, intentar convertir a JPG
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.stdout.write(f"Found file without valid extension: {filename}, attempting to convert to JPG...")
                new_filename = self.convert_to_jpg(file_path)
                if new_filename:
                    filename = new_filename
                    self.stdout.write(f"Successfully converted to {filename}")
                else:
                    continue

            movie_title, _ = os.path.splitext(filename)  # Extrae el nombre sin extensión
            
            # Versiones del título para debug
            movie_title_original = movie_title.strip()
            movie_title_normalized = self.normalize_title(movie_title_original)
            movie_title_no_prefix = self.normalize_title(movie_title_original.replace('m_', '', 1))

            # Debug info
            self.stdout.write(f"Checking: Original='{movie_title_original}', Normalized='{movie_title_normalized}', No Prefix='{movie_title_no_prefix}'")

            image_path = os.path.join('movie/images', filename)

            try:
                # Usar el método de búsqueda
                movie = self.find_movie_by_title(movie_title_original)

                if movie:
                    movie.image = image_path
                    movie.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
                    # Debug: mostrar coincidencia
                    self.stdout.write(f"Matched file '{movie_title_original}' with DB title '{movie.title}'")
                else:
                    self.stderr.write(f"Movie not found: {movie_title_original}")
                    # Mostrar títulos similares para debug
                    similar = Movie.objects.filter(title__icontains=movie_title_no_prefix.split()[0])
                    if similar:
                        self.stderr.write("Similar titles found:")
                        for m in similar:
                            self.stderr.write(f"- {m.title}")
            
            except Exception as e:
                self.stderr.write(f"Failed to update {movie_title_original}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movie images."))