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
    subset=["budget", "production_companies", "revenue", "runtime"],
    how="all"
)
#vuelve a acomodar los indices del dataframe luego de eliminar la fila corrumpida
dfPeliculas = dfPeliculas.reset_index(drop=True)

#Transforma los 0 en runtime en nulos
dfPeliculas["runtime"] = dfPeliculas["runtime"].replace(0, float("nan"))

#Transforma los 0 en budget y revenue en nulos
dfPeliculas["budget"] = dfPeliculas["budget"].replace(0, float("nan"))
dfPeliculas["revenue"] = dfPeliculas["revenue"].replace(0, float("nan"))

#transforma los 0 de vote_average que no tienen votos en nulos
dfPeliculas.loc[
    dfPeliculas["vote_count"] == 0,
    "vote_average"
] = float("nan")

#convierte texto en una lista real en genres
dfPeliculas["genres"] = dfPeliculas["genres"].apply(ast.literal_eval)

#convierte texto en una lista real en production_companies
dfPeliculas["production_companies"] = dfPeliculas["production_companies"].apply(ast.literal_eval)


