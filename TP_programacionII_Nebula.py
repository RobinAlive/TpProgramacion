"""TRABAJO PRACTICO 2 - PROGRAMACION II
    Integrantes:
        - 1. Camila vivo
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

#Transforma los 0 en runtime, budget y revenue en nulos
dfPeliculas["runtime"] = dfPeliculas["runtime"].replace(0, float("nan"))
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
titulosPopulares = peliculasMasPopulares["title"].tolist() #hace una lista con los títulos de las películas más populares
titulosMejorValoradas = peliculasMejorValoradas["title"].tolist() #hace una lista con los títulos de las películas mejor valoradas
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

"""Qué características tienen las películas que combinan alta popularidad y alta valoración"""
#datafrane con unicamente peliculas que tengan popularidad y valoracion
peliculasConBuenDesempeno = dfPeliculas.dropna(
    subset=["popularity", "vote_average"]
)
#calcula la mediana de popularidad y valoracion
medianaPopularidad = peliculasConBuenDesempeno["popularity"].median()
medianaValoracion = peliculasConBuenDesempeno["vote_average"].median()
#filtra las peliculas que tengan popularidad y valoracion mayor o igual a la mediana
peliculasAltoDesempeno = peliculasConBuenDesempeno[
    (peliculasConBuenDesempeno["popularity"] >= medianaPopularidad) & (peliculasConBuenDesempeno["vote_average"] >= medianaValoracion)
]
#lista de generos de peliculas con alto desempeño
listaGenerosAltoDesempeno = []
for i in range(len(peliculasAltoDesempeno)):
    pelicula = peliculasAltoDesempeno.iloc[i]
    for genero in pelicula["genres"]:
        listaGenerosAltoDesempeno.append(genero)
#conteo de generos de peliculas con alto desempeño
conteoGeneros = {}
for genero in listaGenerosAltoDesempeno:
    if genero in conteoGeneros:
        conteoGeneros[genero] += 1
    else:
        conteoGeneros[genero] = 1
#determina el porcentaje de peliculas de alto desempeño por genero
porcentajeGeneros = {}
for genero in conteoGeneros:
    porcentajeGeneros[genero] = round((conteoGeneros[genero] / len(peliculasAltoDesempeno)) * 100, 2
    )
#lista de generos de todas las peliculas con popularidad y valoracion
listaGenerosTotales = []
for i in range(len(peliculasConBuenDesempeno)):
    pelicula = peliculasConBuenDesempeno.iloc[i]
    for genero in pelicula["genres"]:
        listaGenerosTotales.append(genero)
#conteo de generos de todas las peliculas con popularidad y valoracion
conteoGenerosTotales = {}
for genero in listaGenerosTotales:
    if genero in conteoGenerosTotales:
        conteoGenerosTotales[genero] += 1
    else:
        conteoGenerosTotales[genero] = 1
#determina el porcentaje de peliculas de todas las peliculas con popularidad y valoracion por genero
porcentajeGenerosTotales = {}
for genero in conteoGenerosTotales:
    porcentajeGenerosTotales[genero] = round((conteoGenerosTotales[genero] / len(peliculasConBuenDesempeno)) * 100, 2
    )
#diferencia de presencia por genero entre peliculas con alto desempeño y todas las peliculas con popularidad y valoracion
diferenciaGeneros = {}
for genero in porcentajeGeneros:
    diferenciaGeneros[genero] = round(porcentajeGeneros[genero] - porcentajeGenerosTotales[genero],2
    )

#diccionario con idiomas de peliculas con alto desempeño y su cantidad
conteoIdiomasAltoDesempeno = {}
for i in range(len(peliculasAltoDesempeno)):
    pelicula = peliculasAltoDesempeno.iloc[i]
    idioma = pelicula["original_language"]
    if idioma in conteoIdiomasAltoDesempeno:
        conteoIdiomasAltoDesempeno[idioma] += 1
    else:
        conteoIdiomasAltoDesempeno[idioma] = 1
#determina el porcentaje de peliculas de alto desempeño por idioma
porcentajeIdiomasAltoDesempeno = {}
for idioma in conteoIdiomasAltoDesempeno:
    porcentajeIdiomasAltoDesempeno[idioma] = round((conteoIdiomasAltoDesempeno[idioma] / len(peliculasAltoDesempeno)) * 100,2
    )
#diccionario con idiomas de todas las peliculas con popularidad y valoracion y su cantidad
conteoIdiomasTotales = {}
for i in range(len(peliculasConBuenDesempeno)):
    pelicula = peliculasConBuenDesempeno.iloc[i]
    idioma = pelicula["original_language"]
    if idioma in conteoIdiomasTotales:
        conteoIdiomasTotales[idioma] += 1
    else:
        conteoIdiomasTotales[idioma] = 1
#determina el porcentaje de peliculas de todas las peliculas con popularidad y valoracion por idioma
porcentajeIdiomasTotales = {}
for idioma in conteoIdiomasTotales:
    porcentajeIdiomasTotales[idioma] = round(
        (conteoIdiomasTotales[idioma] / len(peliculasConBuenDesempeno)) * 100,
        2
    )
#diferencia de presencia por idioma entre peliculas con alto desempeño y todas las peliculas con popularidad y valoracion
diferenciaIdiomas = {}
for idioma in porcentajeIdiomasAltoDesempeno:
    if conteoIdiomasTotales[idioma] >= 100:
        diferenciaIdiomas[idioma] = round(porcentajeIdiomasAltoDesempeno[idioma] - porcentajeIdiomasTotales[idioma],2
        )

conteoProductorasAltoDesempeno = {}

# Conteo de productoras de peliculas con alto desempeño
for i in range(len(peliculasAltoDesempeno)):
    pelicula = peliculasAltoDesempeno.iloc[i]
    for productora in pelicula["production_companies"]:
        if productora in conteoProductorasAltoDesempeno:
            conteoProductorasAltoDesempeno[productora] += 1
        else:
            conteoProductorasAltoDesempeno[productora] = 1
# Determina el porcentaje de peliculas de alto desempeño por productora
porcentajeProductorasAltoDesempeno = {}
for productora in conteoProductorasAltoDesempeno:
    porcentajeProductorasAltoDesempeno[productora] = round((conteoProductorasAltoDesempeno[productora] / len(peliculasAltoDesempeno)) * 100,2
    )
# Diccionario con productoras de todas las peliculas con popularidad y valoracion y su cantidad
conteoProductorasTotales = {}
for i in range(len(peliculasConBuenDesempeno)):
    pelicula = peliculasConBuenDesempeno.iloc[i]
    for productora in pelicula["production_companies"]:
        if productora in conteoProductorasTotales:
            conteoProductorasTotales[productora] += 1
        else:
            conteoProductorasTotales[productora] = 1
# Determina el porcentaje de peliculas de todas las peliculas con popularidad y valoracion por productora
porcentajeProductorasTotales = {}
for productora in conteoProductorasTotales:
    porcentajeProductorasTotales[productora] = round((conteoProductorasTotales[productora] / len(peliculasConBuenDesempeno)) * 100,2
    )
# Diferencia de presencia por productora entre peliculas con alto desempeño y todas las peliculas con popularidad y valoracion
diferenciaProductoras = {}
for productora in porcentajeProductorasAltoDesempeno:
    if conteoProductorasTotales[productora] >= 100:
        diferenciaProductoras[productora] = round(porcentajeProductorasAltoDesempeno[productora] - porcentajeProductorasTotales[productora],2
        )
# Visualización de datos
print()
print("Películas con alto desempeño:", len(peliculasAltoDesempeno))
print("Mediana de popularidad:", medianaPopularidad)
print("Mediana de valoración:", medianaValoracion)
#dif por genero
print()
print("Diferencia de presencia por género:")
for genero, diferencia in sorted(
    diferenciaGeneros.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(genero, ":", diferencia)
#dif por idioma
print()
print("Diferencia de presencia por idioma:")
for idioma, diferencia in sorted(
    diferenciaIdiomas.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(idioma, ":", diferencia)
#dif por productora
print()
print("Diferencia de presencia por productora:")
for productora, diferencia in sorted(
    diferenciaProductoras.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(productora, ":", diferencia)

"""Qué combinaciones de género e idioma tienen una mayor proporción de películas de alto desempeño"""
# Conteo total de combinaciones de genero e idioma
conteoCombinacionesTotales = {}
for i in range(len(peliculasConBuenDesempeno)):
    pelicula = peliculasConBuenDesempeno.iloc[i]
    idioma = pelicula["original_language"]
    for genero in pelicula["genres"]:
        combinacion = genero + " - " + idioma
        if combinacion in conteoCombinacionesTotales:
            conteoCombinacionesTotales[combinacion] += 1
        else:
            conteoCombinacionesTotales[combinacion] = 1
# Conteo de combinaciones de genero e idioma en peliculas de alto desempeño
conteoCombinacionesAltoDesempeno = {}
for i in range(len(peliculasAltoDesempeno)):
    pelicula = peliculasAltoDesempeno.iloc[i]
    idioma = pelicula["original_language"]
    for genero in pelicula["genres"]:
        combinacion = genero + " - " + idioma
        if combinacion in conteoCombinacionesAltoDesempeno:
            conteoCombinacionesAltoDesempeno[combinacion] += 1
        else:
            conteoCombinacionesAltoDesempeno[combinacion] = 1
# Porcentaje de peliculas de alto desempeño por combinacion de genero e idioma
porcentajeAltoDesempenoPorCombinacion = {}
for combinacion in conteoCombinacionesTotales:
    if conteoCombinacionesTotales[combinacion] >= 100:
        if combinacion in conteoCombinacionesAltoDesempeno:
            porcentajeAltoDesempenoPorCombinacion[combinacion] = round((conteoCombinacionesAltoDesempeno[combinacion]/ conteoCombinacionesTotales[combinacion]) * 100,2
            )
#visualizacion de datos
print()
print("Top 50 combinaciones con mayor porcentaje de alto desempeño:")
top50Porcentaje = sorted(
    porcentajeAltoDesempenoPorCombinacion.items(),
    key=lambda x: x[1],
    reverse=True
)[:50]
for combinacion, porcentaje in top50Porcentaje:
    print(
        combinacion,":",porcentaje,"%","- Alto desempeño:",conteoCombinacionesAltoDesempeno[combinacion],"- Total:",conteoCombinacionesTotales[combinacion]
    )


"""Qué combinaciones de género e idioma aparecen con mayor frecuencia entre las películas de alto desempeño"""
#visualizacion de datos 
print()
print("Top 50 combinaciones más frecuentes entre películas de alto desempeño:")
top50Cantidad = sorted(
    conteoCombinacionesAltoDesempeno.items(),
    key=lambda x: x[1],
    reverse=True
)[:50]
for combinacion, cantidad in top50Cantidad:
    print(combinacion, ":", cantidad)


"""La duración de una película se relaciona con su valoración"""
#Peliculas que tengan duracion y valoracion
peliculasConDuracion = dfPeliculas.dropna(
    subset=["runtime", "vote_average"]
)
#Mediana de duracion
medianaDuracion = peliculasConDuracion["runtime"].median()
#Peliculas con duracion menor y mayor a la mediana
duracionCorta = peliculasConDuracion[
    peliculasConDuracion["runtime"] < medianaDuracion
]
duracionLarga = peliculasConDuracion[
    peliculasConDuracion["runtime"] >= medianaDuracion
]
#valoracion promedio de peliculas con duracion corta y larga
valoracionPromedioDuracionCorta = duracionCorta["vote_average"].mean()
valoracionPromedioDuracionLarga = duracionLarga["vote_average"].mean()
#visualizacion de datos
print()
print("Valoracion promedio de peliculas cortas:", valoracionPromedioDuracionCorta)
print("Valoracion promedio de peliculas largas:", valoracionPromedioDuracionLarga)
print("Cantidad de peliculas cortas:", len(duracionCorta))
print("Cantidad de peliculas largas:", len(duracionLarga))