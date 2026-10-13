"""TRABAJO PRACTICO 2 - PROGRAMACION II
    Integrantes:
        - 1. Camila vivo
        - 2. Rebecca Carizo
"""
import pandas as pd
import ast #permite convertir un string con formato de lista en una lista real

"""IMPORTACION DE DATASET DE PELICULAS"""
#busca el dataset de peliculas y lo guarda en un dataframe y usa otro lector mas felixible para evitar errores de una fila mal formada  
dfPeliculas = pd.read_csv("data/top_1000_popular_movies_tmdb.csv",engine="python")

"""LIMPIEZA DE DATOS"""
#eliminamos fila corrupta
dfPeliculas = dfPeliculas.drop(index=226)
#vuelve a acomodar los indices del dataframe luego de eliminar la fila corrumpida
dfPeliculas = dfPeliculas.reset_index(drop=True)

#Elimina columna innecesaria 
dfPeliculas = dfPeliculas.drop(columns=["Unnamed: 0"])

#Elimina fila con valores nulos
dfPeliculas = dfPeliculas.dropna(
    subset=["budget", "production_companies", "revenue", "runtime"],#solo revisa estas columnas
    how="all") #solo si todas las columnas son nulas
#vuelve a acomodar los indices del dataframe luego de eliminar la fila corrumpida
dfPeliculas = dfPeliculas.reset_index(drop=True)

#Transforma los 0 en runtime en nulos
dfPeliculas["runtime"] = dfPeliculas["runtime"].replace(0, float("nan"))

#Transforma los 0 en budget y revenue en nulos
dfPeliculas["budget"] = dfPeliculas["budget"].replace(0, float("nan"))
dfPeliculas["revenue"] = dfPeliculas["revenue"].replace(0, float("nan"))

#transforma los 0 de vote_average que no tienen votos en nulos
dfPeliculas.loc[ #trabaja con una columna y fila especifica
    dfPeliculas["vote_count"] == 0,"vote_average"] = float("nan")

#convierte texto en una lista real en genres
dfPeliculas["genres"] = dfPeliculas["genres"].apply(ast.literal_eval)

#convierte texto en una lista real en production_companies
dfPeliculas["production_companies"] = dfPeliculas["production_companies"].apply(ast.literal_eval)

#Remplaza dentro de idiomas cn por catones
dfPeliculas["original_language"] = (
    dfPeliculas["original_language"]
    .replace("cn", "Cantonese")
)


"""ANALISSIS DE DATOS"""

#lista de diccionarios con peliculas. generos y valoraciones
listaGeneros = []
for i in range(len(dfPeliculas)):
    pelicula = dfPeliculas.iloc[i]
    for genero in pelicula["genres"]:
        listaGeneros.append({
            "title": pelicula["title"],
            "genre": genero,
            "vote_average": pelicula["vote_average"],
            "vote_count": pelicula["vote_count"],
            "popularity": pelicula["popularity"]
        })
dfGeneros = pd.DataFrame(listaGeneros)

"""Que generos reciben mejora valoraciones"""
#lista de generos con su valoracion promedio y cantidad de peliculas por genero
valoracionPorGenero = (
    dfGeneros
    .groupby("genre")["vote_average"] #junta todas las peliculas de un mismo genero
    .agg(["mean", "count"]) #calcula la media y la cantidad de peliculas por genero simultaneamente con .agg
    .sort_values("mean", ascending=False) #ordena de mayor a menor el genero mejor valorado
)

#visualizacion de datos
print()
print("Valoración promedio por género:")
print(valoracionPorGenero)


"""Que géneros presentan mayor popularidad"""
#lista de generos con su popularidad promedio y cantidad de peliculas por genero
popularidadPorGenero = (
    dfGeneros
    .groupby("genre")["popularity"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
)

#visualizacion de datos
print()
print("Popularidad promedio por género:")
print(popularidadPorGenero)


"""Las peliculas mas populares son las mejor valoradas"""
#50 peliculas mas populares
peliculasMasPopulares = (
    dfPeliculas[
        ["title", "popularity", "vote_average", "vote_count"]
    ]
    .sort_values("popularity", ascending=False)
    .head(50)
)

#50 peliculas mejor valoradas, (conmas de 100 votos)
peliculasMejorValoradas = (
    dfPeliculas[
        dfPeliculas["vote_count"] >= 100
    ][
        ["title", "popularity", "vote_average", "vote_count"]
    ]
    .sort_values("vote_average", ascending=False)
    .head(50)
)

#compara las dos listas y devuelve las peliculas que aparecen en ambas
titulosPopulares = peliculasMasPopulares["title"].tolist() #obtiene los títulos de las películas más populares
titulosMejorValoradas = peliculasMejorValoradas["title"].tolist() #obtiene los títulos de las películas mejor valoradas
coincidencias = []
for titulo in titulosPopulares:
    if titulo in titulosMejorValoradas:
        coincidencias.append(titulo)

#visualizacion de datos
print()
print("Películas que aparecen en ambas listas:")
print(coincidencias)
print("Cantidad de coincidencias:", len(coincidencias))


"""Que idiomas presentan mayor popularidad promedio"""
#lista de idiomas con su popularidad promedio y cantidad de peliculas por idioma
popularidadPorIdioma = (
    dfPeliculas
    .groupby("original_language")["popularity"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
)

#filtra los idiomas con al menos 100 peliculas
popularidadPorIdiomaFiltrado = (
    popularidadPorIdioma[
        popularidadPorIdioma["count"] >= 100
    ]
)

#visualizacion de datos
print()
print("Popularidad promedio por idioma con al menos 100 películas:")
print(popularidadPorIdiomaFiltrado)


"""Que productoras presentan mayor popularidad promedio"""
#lista de diccionarios con peliculas, productoras y popularidad
listaProductoras = []
for i in range(len(dfPeliculas)):
    pelicula = dfPeliculas.iloc[i]
    for productora in pelicula["production_companies"]:
        listaProductoras.append({
            "title": pelicula["title"],
            "production_company": productora,
            "popularity": pelicula["popularity"]
        })
dfProductoras = pd.DataFrame(listaProductoras)

#calcula popularidad promedio por productora
popularidadPorProductora = (
    dfProductoras
    .groupby("production_company")["popularity"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
)

#filtra las productoras con al menos 100 peliculas
popularidadPorProductoraFiltrado = (
    popularidadPorProductora[
        popularidadPorProductora["count"] >= 100
    ]
    .sort_values("mean", ascending=False)
)

#visualizacion de datos
print()
print("Popularidad promedio por productora con al menos 100 películas:")
print(popularidadPorProductoraFiltrado)


"""Las películas con presupuestos más altos reciben mejores valoraciones"""
# Guarda únicamente películas que tengan presupuesto y valoración
peliculasConPresupuesto = dfPeliculas.dropna(
    subset=["budget", "vote_average"])
medianaPresupuesto = peliculasConPresupuesto["budget"].median() #Calcula la mediana del presupuesto

# Películas con presupuesto menor a la mediana
presupuestoBajo = peliculasConPresupuesto[peliculasConPresupuesto["budget"] < medianaPresupuesto]
# Películas con presupuesto igual o mayor a la mediana
presupuestoAlto = peliculasConPresupuesto[peliculasConPresupuesto["budget"] >= medianaPresupuesto]

#visualizacion de datos
print()
print("Mediana del presupuesto:", medianaPresupuesto)
#valoracion promedio de peliculas con presupuesto bajo
print(
    "Valoración promedio - presupuesto bajo:",
    presupuestoBajo["vote_average"].mean()
)
#valoracion promedio de peliculas con presupuesto alto
print(
    "Valoración promedio - presupuesto alto:",
    presupuestoAlto["vote_average"].mean()
)
#cantidad de peliculas con presupuesto bajo y alto
print("Cantidad presupuesto bajo:", len(presupuestoBajo))
print("Cantidad presupuesto alto:", len(presupuestoAlto))