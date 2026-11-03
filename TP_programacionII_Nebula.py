"""TRABAJO PRACTICO 2 - PROGRAMACION II
    Integrantes:
        - 1. Camila vivo
"""
import pandas as pd
import ast #permite convertir un string con formato de lista en una lista real
import matplotlib.pyplot as plt

""" FUNCIONES """
def cargar_datos ():
    #busca el dataset de peliculas y lo guarda en un dataframe y usa otro lector mas felixible para evitar errores de una fila mal formada  
    dfPeliculas = pd.read_csv("data/top_1000_popular_movies_tmdb.csv",engine="python")  
    return dfPeliculas

def limpiar_datos(dfPeliculas):
    #eliminamos fila corrupta
    dfPeliculas = dfPeliculas.drop(index=226)

    #Elimina columna innecesaria 
    dfPeliculas = dfPeliculas.drop(columns=["Unnamed: 0"])

    #Elimina fila con valores nulos
    dfPeliculas = dfPeliculas.dropna(
        subset=["budget", "production_companies", "revenue", "runtime"],#solo revisa estas columnas
        how="all") #solo si todas las columnas son nulas

    #vuelve a acomodar los indices del dataframe luego de eliminar la fila corrumpida
    dfPeliculas = dfPeliculas.reset_index(drop=True)

    #Transforma los 0 en runtime, budget y revenue en nulos
    for columna in ["runtime", "budget", "revenue"]:
        dfPeliculas[columna] = dfPeliculas[columna].replace(0, float("nan"))

    #transforma los 0 de vote_average que no tienen votos en nulos
    dfPeliculas.loc[ #trabaja con una columna y fila especifica
        dfPeliculas["vote_count"] == 0,"vote_average"] = float("nan")

    #convierte texto en una lista real en genres y en production_companies
    for columna in ["genres", "production_companies"]:
        dfPeliculas[columna] = dfPeliculas[columna].apply(ast.literal_eval)

    #Remplaza dentro de idiomas cn por catones
    dfPeliculas["original_language"] = (
        dfPeliculas["original_language"]
        .replace("cn", "Cantonese")
    )
    return dfPeliculas

def crear_df_generos(dfPeliculas):
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
    return dfGeneros

def analizar_por_categoria(df, columnaAgrupar, columnaAnalizar, minimoCantidad=0):
    #lista de generos con su valoracion y popularidad promedio y cantidad de peliculas por genero
    resultado = (
        df
        .groupby(columnaAgrupar)[columnaAnalizar] #junta todas las peliculas de una misma columna
        .agg(["mean", "count"]) #calcula la media y la cantidad de peliculas por genero simultaneamente con .agg
    )
    resultado = resultado[resultado["count"] >= minimoCantidad] #filtra las columnas con al menos minimoCantidad de peliculas
    resultado = resultado.sort_values("mean", ascending=False) #ordena de mayor a menor el genero 
    return resultado

def obtener_top_peliculas(dfPeliculas, columna, minimoVotos=0):
#top 50 peliculas por columna, filtrando por minimo de votos
    peliculas = dfPeliculas[
        dfPeliculas["vote_count"] >= minimoVotos
    ][
        ["title", "popularity", "vote_average", "vote_count"]
    ]
    topPeliculas = (peliculas.sort_values(columna, ascending=False).head(50))["title"].tolist()
    return topPeliculas

def comparar_popularidad_valoracion(dfPeliculas):
    #50 peliculas mas populares
    titulosPopulares = obtener_top_peliculas(dfPeliculas, "popularity")
    #50 peliculas mejor valoradas, (conmas de 100 votos)
    titulosMejorValoradas = obtener_top_peliculas(dfPeliculas, "vote_average", 100)
    coincidencias = []
    for titulo in titulosPopulares:
        if titulo in titulosMejorValoradas:
            coincidencias.append(titulo)
    return coincidencias

def crear_df_productoras(dfPeliculas):
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
    return dfProductoras

def comparar_por_mediana(dfPeliculas, columnaDividir, columnaAnalizar):
    # elimina las peliculas que no tengan datos en las columnas necesarias
    peliculasConDatos = dfPeliculas.dropna(
        subset=[columnaDividir, columnaAnalizar]
    )
    # calcula la mediana de la columna utilizada para dividir
    mediana = peliculasConDatos[columnaDividir].median()
    # divide las peliculas en dos grupos
    grupoBajo = peliculasConDatos[peliculasConDatos[columnaDividir] < mediana]
    grupoAlto = peliculasConDatos[peliculasConDatos[columnaDividir] >= mediana]
    # calcula el promedio de la columna a analizar
    promedioBajo = grupoBajo[columnaAnalizar].mean()
    promedioAlto = grupoAlto[columnaAnalizar].mean()
    return mediana, promedioBajo, promedioAlto, len(grupoBajo), len(grupoAlto)

def obtener_alto_desempeno(dfPeliculas):
    # elimina peliculas sin popularidad o valoracion
    peliculasConBuenDesempeno = dfPeliculas.dropna(
        subset=["popularity", "vote_average"]
    )
    # calcula las medianas
    medianaPopularidad = peliculasConBuenDesempeno["popularity"].median()
    medianaValoracion = peliculasConBuenDesempeno["vote_average"].median()
    #selecciona peliculas que igualan o superan ambas medianas
    peliculasAltoDesempeno = peliculasConBuenDesempeno[
        (peliculasConBuenDesempeno["popularity"] >= medianaPopularidad) &
        (peliculasConBuenDesempeno["vote_average"] >= medianaValoracion)
    ]
    return peliculasConBuenDesempeno, peliculasAltoDesempeno, medianaPopularidad, medianaValoracion

def comparar_categorias_lista(peliculasGenerales, peliculasAltoDesempeno, columnaLista, minimoCantidad=0):
    conteoGeneral = {}
    conteoAlto = {}
    # cuenta las categorias en todas las peliculas
    for i in range(len(peliculasGenerales)):
        pelicula = peliculasGenerales.iloc[i]
        for categoria in pelicula[columnaLista]:
            if categoria in conteoGeneral:
                conteoGeneral[categoria] += 1
            else:
                conteoGeneral[categoria] = 1
    # cuenta las categorias en las peliculas de alto desempeño
    for i in range(len(peliculasAltoDesempeno)):
        pelicula = peliculasAltoDesempeno.iloc[i]
        for categoria in pelicula[columnaLista]:
            if categoria in conteoAlto:
                conteoAlto[categoria] += 1
            else:
                conteoAlto[categoria] = 1
    # calcula la diferencia de presencia por categoria
    diferencias = {}
    for categoria in conteoGeneral:
        if conteoGeneral[categoria] >= minimoCantidad: #solo considera categorias con al menos minimoCantidad de peliculas
            porcentajeGeneral = (conteoGeneral[categoria] / len(peliculasGenerales)) * 100
            porcentajeAlto = (conteoAlto.get(categoria, 0) / len(peliculasAltoDesempeno)) * 100
            diferencias[categoria] = round(porcentajeAlto - porcentajeGeneral,2) # diferencia de porcentajes
    return diferencias

def comparar_categorias_simples(peliculasGenerales, peliculasAltoDesempeno, columna, minimoCantidad=0):
    conteoGeneral = {}
    conteoAlto = {}
    # cuenta categorias en todas las peliculas
    for i in range(len(peliculasGenerales)):
        pelicula = peliculasGenerales.iloc[i]
        categoria = pelicula[columna]
        if categoria in conteoGeneral:
            conteoGeneral[categoria] += 1
        else:
            conteoGeneral[categoria] = 1
    # cuenta categorias en peliculas de alto desempeño
    for i in range(len(peliculasAltoDesempeno)):
        pelicula = peliculasAltoDesempeno.iloc[i]
        categoria = pelicula[columna]
        if categoria in conteoAlto:
            conteoAlto[categoria] += 1
        else:
            conteoAlto[categoria] = 1
    # calcula diferencia de presencia
    diferencias = {}
    for categoria in conteoGeneral:
        if conteoGeneral[categoria] >= minimoCantidad:
            porcentajeGeneral = (conteoGeneral[categoria] /len(peliculasGenerales)) * 100
            porcentajeAlto = (conteoAlto.get(categoria, 0) /len(peliculasAltoDesempeno)) * 100
            diferencias[categoria] = round(porcentajeAlto - porcentajeGeneral,2)
    return diferencias

def mostrar_diferencias(diccionario):
    for categoria, diferencia in sorted(
        diccionario.items(), #ordena el diccionario por valor
        key=lambda x: x[1], #ordena por el valor de la diferencia
        reverse=True #ordena de mayor a menor
    ):
        print(categoria, ":", diferencia)

def contar_combinaciones_genero_idioma(peliculas):
    conteoCombinaciones = {}
    for i in range(len(peliculas)):
        pelicula = peliculas.iloc[i]
        idioma = pelicula["original_language"]
        for genero in pelicula["genres"]:
            combinacion = genero + " - " + idioma
            if combinacion in conteoCombinaciones:
                conteoCombinaciones[combinacion] += 1
            else:
                conteoCombinaciones[combinacion] = 1
    return conteoCombinaciones

def calcular_porcentaje_alto_desempeno(conteoTotales,conteoAltoDesempeno,minimoCantidad=100):
    porcentajes = {}
    for combinacion in conteoTotales:
        if conteoTotales[combinacion] >= minimoCantidad:
            if combinacion in conteoAltoDesempeno:
                porcentajes[combinacion] = round((conteoAltoDesempeno[combinacion] /conteoTotales[combinacion]) * 100,2)
    return porcentajes

def graficar_promedio_por_categoria(resultado, titulo, nombreEjeX, nombreEjeY):
    #crea el espacio del grafico de 10x7 
    plt.figure(figsize=(10, 7)) 
    plt.barh( #grafico horizontal
        resultado.index, #toma el indice del dataframe como eje y
        resultado["mean"], #toma mean como valor de la barra
        color="#7957D5" 
    )
    plt.title(titulo) 
    plt.xlabel(nombreEjeX)
    plt.ylabel(nombreEjeY)
    #coloca la categoria con mayor promedio arriba
    plt.gca().invert_yaxis()
    #agrega una grilla solo en el eje x y hace qe sea transparente 
    plt.grid(axis="x", alpha=0.3)
    #ajusta el layout para que no se corten los labels
    plt.tight_layout()
    #muestra el gráfico
    plt.show()

def graficar_coincidencias(coincidencias, totalPeliculas=50):
    # calcula la cantidad de coincidencias y no coincidencias
    cantidadCoincidencias = len(coincidencias)
    cantidadNoCoincidencias = totalPeliculas - cantidadCoincidencias
    # crea una lista con las dos cantidades que se van a graficar
    cantidades = [cantidadCoincidencias, cantidadNoCoincidencias]
    # crea una lista con los nombres de cada parte del grafico
    etiquetas = ["Coinciden", "No coinciden"]
    colores = ["#7957D5", "#12182B"]
    #espacio donde se va a dibujar el grafico
    plt.figure(figsize=(7, 7))
    #grafico de torta
    plt.pie(
        cantidades,          # valores que determinan el tamaño de cada parte
        labels=etiquetas,    # nombre de cada parte
        colors=colores,      # colores de cada parte
        autopct="%1.1f%%",   # muestra el porcentaje dentro del grafico
        startangle=90        # hace que el grafico comience desde arriba
    )
    #titulo del grafico
    plt.title("Coincidencia entre películas más populares y mejor valoradas")
    # acomoda los elementos del grafico para evitar que se corten
    plt.tight_layout()
    # muestra el grafico
    plt.show()

def graficar_comparacion_grupos(nombreGrupoBajo,nombreGrupoAlto, promedioBajo, promedioAlto, titulo):
    # nombres que van a aparecer debajo de cada barra
    grupos = [nombreGrupoBajo, nombreGrupoAlto]
    # valores que determinan la altura de cada barra
    promedios = [ promedioBajo, promedioAlto]
    # crea el espacio donde se va a dibujar el grafico
    plt.figure(figsize=(8, 6))
    # crea las barras y las guarda en una variable
    barras = plt.bar(
        grupos,
        promedios,
        color="#7957D5"
    )
    # escribe el valor arriba de cada barra
    plt.bar_label(barras,fmt="%.2f") #formato con dos decimales
    #titulo
    plt.title(titulo)
    #nombre del eje Y
    plt.ylabel("Valoración promedio")
    # la valoración va de 0 a 10
    plt.ylim(0, 10)
    # agrega una cuadricula horizontal
    plt.grid(axis="y", alpha=0.3)
    #acomoda los elementos del grafico
    plt.tight_layout()
    # muestra el grafico
    plt.show()

def graficar_diferencias_categorias(diccionario, titulo, nombreEjeY):
    # ordena las categorias de menor a mayor segun su diferencia
    datosOrdenados = sorted(
        diccionario.items(),
        key=lambda x: x[1]
    )
    # crea una lista con los nombres de las categorias
    categorias = []
    # crea una lista con las diferencias de cada categoria
    diferencias = []
    # recorre los datos ordenados y separa nombre y valor
    for categoria, diferencia in datosOrdenados:
        categorias.append(categoria)
        diferencias.append(diferencia)
    # crea una lista de colores segun si la diferencia es positiva o negativa
    colores = []
    for diferencia in diferencias:
        # si aparece mas en alto desempeño usa violeta
        if diferencia >= 0:
            colores.append("#7957D5")
        # si aparece menos en alto desempeño usa azul oscuro
        else:
            colores.append("#12182B")
    # crea el espacio donde se va a dibujar el grafico
    plt.figure(figsize=(10, 7))
    # crea las barras horizontales
    plt.barh(
        categorias,
        diferencias,
        color=colores
    )
    # agrega una linea vertical en 0 para separar valores positivos y negativos
    plt.axvline(
        0,
        color="gray",
        linewidth=1 
    )
    #titulo del grafico
    plt.title(titulo)
    # indica que el eje X representa la diferencia entre ambos grupos
    plt.xlabel("Diferencia de presencia (puntos porcentuales)")
    # nombre eje Y
    plt.ylabel(nombreEjeY)
    # agrega una cuadricula sobre el eje X
    plt.grid(
        axis="x",
        alpha=0.3
    )
    # acomoda los elementos para evitar que se corten
    plt.tight_layout()
    # muestra el grafico
    plt.show()

def graficar_top_diccionario(diccionario, titulo, nombreEjeX, cantidad=10):
    # ordena los elementos de mayor a menor segun su valor
    datosOrdenados = sorted(
        diccionario.items(),
        key=lambda x: x[1],
        reverse=True
    )[:cantidad]
    # listas donde se guardan por separado los nombres y los valores
    categorias = []
    valores = []
    # recorre los datos ordenados
    for categoria, valor in datosOrdenados:
        categorias.append(categoria)
        valores.append(valor)
    # crea el espacio donde se dibuja el grafico
    plt.figure(figsize=(10, 7))
    #barras horizontales
    plt.barh(
        categorias,
        valores,
        color="#7957D5"
    )
    # titulo
    plt.title(titulo)
    #nombre del eje X
    plt.xlabel(nombreEjeX)
    #nombre del eje Y
    plt.ylabel("Combinación género - idioma")
    # invierte el eje para que el valor mas alto aparezca arriba
    plt.gca().invert_yaxis()
    # agrega una cuadricula sobre el eje X
    plt.grid(axis="x", alpha=0.3)
    # acomoda los elementos para que no se corten
    plt.tight_layout()
    # muestra el grafico
    plt.show()

def main():
    """IMPORTACION DE DATASET DE PELICULAS"""
    dfPeliculas = cargar_datos()

    """LIMPIEZA DE DATOS""" 
    dfPeliculas = limpiar_datos(dfPeliculas)

    """ANALISSIS DE DATOS""" 
    dfGeneros = crear_df_generos(dfPeliculas)

    """Que generos reciben mejora valoraciones"""
    valoracionPorGenero = analizar_por_categoria(dfGeneros, "genre", "vote_average")
    #visualizacion de datos
    print()
    print("Valoración promedio por género:")
    print(valoracionPorGenero)

    graficar_promedio_por_categoria(valoracionPorGenero,"Valoración promedio por género","Valoración promedio","Genero")

    """Que géneros presentan mayor popularidad"""
    popularidadPorGenero = analizar_por_categoria(dfGeneros, "genre", "popularity")
    #visualizacion de datos
    print()
    print("Popularidad promedio por género:")
    print(popularidadPorGenero)

    graficar_promedio_por_categoria(popularidadPorGenero, "Popularidad promedio por género", "Popularidad promedio", "Genero")

    """Las peliculas mas populares son las mejor valoradas"""
    coincidencias=comparar_popularidad_valoracion(dfPeliculas)
    #visualizacion de datos
    print()
    print("Películas que aparecen en ambas listas:")
    print(coincidencias)
    print("Cantidad de coincidencias:", len(coincidencias))

    graficar_coincidencias(coincidencias)

    """Que idiomas presentan mayor popularidad promedio"""
    #lista de idiomas con su popularidad promedio y cantidad de peliculas por idioma
    popularidadPorIdioma = analizar_por_categoria(dfPeliculas, "original_language", "popularity",100)
    #visualizacion de datos
    print()
    print("Popularidad promedio por idioma con al menos 100 películas:")
    print(popularidadPorIdioma)

    graficar_promedio_por_categoria(popularidadPorIdioma,"Popularidad promedio por idioma","Popularidad promedio", "Idioma")

    """Que productoras presentan mayor popularidad promedio"""
    dfProductoras = crear_df_productoras(dfPeliculas)
    #calcula popularidad promedio por productora
    popularidadPorProductora = analizar_por_categoria(dfProductoras, "production_company", "popularity",100)
    #visualizacion de datos
    print()
    print("Popularidad promedio por productora con al menos 100 películas:")
    print(popularidadPorProductora)

    top10Productoras = popularidadPorProductora.head(10)
    graficar_promedio_por_categoria( top10Productoras,"Top 10 productoras con mayor popularidad promedio","Popularidad promedio", "Productora")

    """Las películas con presupuestos más altos reciben mejores valoraciones"""
    medianaPresupuesto, PresupuestoBajo, PresupuestoAlto, cantidadPresupuestoBajo, cantidadPresupuestoAlto = comparar_por_mediana(dfPeliculas,"budget","vote_average")
    #visualizacion de datos
    print()
    print("Mediana del presupuesto:", medianaPresupuesto)
    print("Valoración promedio presupuesto bajo:", PresupuestoBajo)
    print("Valoración promedio presupuesto alto:", PresupuestoAlto)
    print("Cantidad presupuesto bajo:", cantidadPresupuestoBajo)
    print("Cantidad presupuesto alto:", cantidadPresupuestoAlto)

    graficar_comparacion_grupos("Presupuesto bajo","Presupuesto alto",PresupuestoBajo,PresupuestoAlto,"Valoración promedio según nivel de presupuesto")

    """Qué características tienen las películas que combinan alta popularidad y alta valoración"""
    peliculasConBuenDesempeno, peliculasAltoDesempeno, medianaPopularidad, medianaValoracion = obtener_alto_desempeno(dfPeliculas)
    #diferencia de presencia por genero entre peliculas con alto desempeño y todas las peliculas con popularidad y valoracion
    diferenciaGeneros = comparar_categorias_lista(peliculasConBuenDesempeno,peliculasAltoDesempeno,"genres") 
    #diccionario con idiomas de peliculas con alto desempeño y su cantidad
    diferenciaIdiomas = comparar_categorias_simples(peliculasConBuenDesempeno, peliculasAltoDesempeno, "original_language", 100)
    #diferencia de presencia por productora entre peliculas con alto desempeño y todas las peliculas con popularidad y valoracion
    diferenciaProductoras = comparar_categorias_lista(peliculasConBuenDesempeno,peliculasAltoDesempeno,"production_companies",100)
    # Visualización de datos
    print()
    print("Películas con alto desempeño:", len(peliculasAltoDesempeno))
    print("Mediana de popularidad:", medianaPopularidad)
    print("Mediana de valoración:", medianaValoracion)
    # diferencia por genero
    print()
    print("Diferencia de presencia de géneros en películas de alto desempeño:")
    mostrar_diferencias(diferenciaGeneros)
    # diferencia por idioma
    print()
    print("Diferencia de presencia por idioma:")
    mostrar_diferencias(diferenciaIdiomas)
    # diferencia por productora
    print()
    print("Diferencia de presencia por productora:")
    mostrar_diferencias(diferenciaProductoras)

    graficar_diferencias_categorias( diferenciaGeneros, "Presencia de géneros en películas de alto desempeño", "Género")
    graficar_diferencias_categorias(diferenciaIdiomas,"Presencia de idiomas en películas de alto desempeño","Idioma")
    graficar_diferencias_categorias(diferenciaProductoras,"Presencia de productoras en películas de alto desempeño","Productora")

    """Qué combinaciones de género e idioma tienen una mayor proporción de películas de alto desempeño"""
    # cantidad total de peliculas por combinacion
    conteoCombinacionesTotales = contar_combinaciones_genero_idioma(peliculasConBuenDesempeno)
    # cantidad de peliculas de alto desempeño por combinacion
    conteoCombinacionesAltoDesempeno = contar_combinaciones_genero_idioma(peliculasAltoDesempeno)
    # porcentaje de alto desempeño dentro de cada combinacion
    porcentajeAltoDesempenoPorCombinacion = calcular_porcentaje_alto_desempeno(conteoCombinacionesTotales,conteoCombinacionesAltoDesempeno, 100)
    #visualizacion de datos
    print()
    print("Top 50 combinaciones con mayor porcentaje de alto desempeño:")
    top50Porcentaje = sorted(
        porcentajeAltoDesempenoPorCombinacion.items(), #ordena el diccionario por valor
        key=lambda x: x[1], #ordena por el valor del porcentaje
        reverse=True)[:50] #toma las primeras 50
    for combinacion, porcentaje in top50Porcentaje:
        print(combinacion,":",porcentaje,"%","- Alto desempeño:",conteoCombinacionesAltoDesempeno[combinacion],"- Total:",conteoCombinacionesTotales[combinacion])

    graficar_top_diccionario(porcentajeAltoDesempenoPorCombinacion, "Top 10 combinaciones con mayor proporción de alto desempeño","Porcentaje de películas de alto desempeño")

    """Qué combinaciones de género e idioma aparecen con mayor frecuencia entre las películas de alto desempeño"""
    #visualizacion de datos 
    print()
    print("Top 50 combinaciones más frecuentes entre películas de alto desempeño:")
    top50Cantidad = sorted(
        conteoCombinacionesAltoDesempeno.items(),
        key=lambda x: x[1],
        reverse=True)[:50]
    for combinacion, cantidad in top50Cantidad:
        print(combinacion, ":", cantidad)

    graficar_top_diccionario( conteoCombinacionesAltoDesempeno, "Top 10 combinaciones más frecuentes entre películas de alto desempeño","Cantidad de películas")

    """La duración de una película se relaciona con su valoración"""
    medianaDuracion, valoracionDuracionCorta, valoracionDuracionLarga, cantidadDuracionCorta, cantidadDuracionLarga = comparar_por_mediana(dfPeliculas,"runtime","vote_average")
    # visualizacion de datos
    print()
    print("Mediana de duración:", medianaDuracion)
    print("Valoración promedio duración corta:", valoracionDuracionCorta)
    print("Valoración promedio duración larga:", valoracionDuracionLarga)
    print("Cantidad duración corta:", cantidadDuracionCorta)
    print("Cantidad duración larga:", cantidadDuracionLarga)

    # crea el nombre del grupo de peliculas con duracion menor a la mediana
    nombreDuracionCorta = "Menos de " + str(int(medianaDuracion)) + " min"
    # crea el nombre del grupo de peliculas con duracion igual o mayor a la mediana
    nombreDuracionLarga = str(int(medianaDuracion)) + " min o más"
    graficar_comparacion_grupos( nombreDuracionCorta,nombreDuracionLarga, valoracionDuracionCorta, valoracionDuracionLarga, "Valoración promedio según duración de la película")
main()