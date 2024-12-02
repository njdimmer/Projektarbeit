import imdb as IMDb

def get_movie_info(movie_name):
    ia = IMDb.IMDb()
    movies = ia.search_movie(movie_name)
    if len(movies) == 0:
        return None
    movie = movies[0]
    ia.update(movie)
    ia.update(movie, ['external reviews'])
    ia.update(movie, ['reviews'])
    ia.update(movie, ['critic reviews'])    
    return movie

if __name__ == '__main__':
    movie = get_movie_info('The Dark Knight')
    print(movie.keys())

    print(movie.infoset2keys['external reviews'])
    print(movie.infoset2keys['reviews'])
    print(movie.infoset2keys['critic reviews'])