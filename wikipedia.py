from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Funcion para extraer los datos de wikipedia
def extraer_datos_wikipedia(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error en la solicitud: {response.status_code}")
        return None
    
    # Manejar la información que hemos extraído del reponse
    sopa = BeautifulSoup(response.content, "html.parser") #Nos lo parsea todo a HTLM
  
    # Hacemos nuestro DataFrame buscando los elementos dentro del html
    Tabla = sopa.find("table", {"class": "infobox"})
    Liga = Tabla.findAll("tr")
    datos = []
    for x in Liga:
        filas = x.findAll(["td", "th"])
        if len(filas) > 1:
            clave = filas[0].text.strip()
            valor = filas[1].text.strip()
            datos.append([clave, valor])
    df_1 = pd.DataFrame(datos, columns=["Atributo", "Valor"])
       
    return df_1

# Hacemos DataFrame individual de cada liga
datos_LaLiga = extraer_datos_wikipedia("https://es.wikipedia.org/wiki/Primera_Divisi%C3%B3n_de_Espa%C3%B1a")

datos_Premier = extraer_datos_wikipedia("https://es.wikipedia.org/wiki/Premier_League")

datos_Ligue1 = extraer_datos_wikipedia("https://es.wikipedia.org/wiki/Ligue_1")

datos_Bundesliga = extraer_datos_wikipedia("https://es.wikipedia.org/wiki/Bundesliga_(Alemania)")

datos_SerieA = extraer_datos_wikipedia("https://es.wikipedia.org/wiki/Serie_A_(Italia)")

# Renombrar columna con nombre de cada liga
datos_LaLiga = datos_LaLiga.rename(columns={"Valor": "LaLiga"})
datos_Premier = datos_Premier.rename(columns={"Valor": "Premier League"})
datos_Ligue1 = datos_Ligue1.rename(columns={"Valor": "Ligue 1"})
datos_Bundesliga = datos_Bundesliga.rename(columns={"Valor": "Bundesliga"})
datos_SerieA = datos_SerieA.rename(columns={"Valor": "Serie A"})

# Unir los df
df_final1 = datos_LaLiga.merge(datos_Premier, on="Atributo", how="outer").merge(datos_Ligue1, on="Atributo", how="outer").merge(datos_Bundesliga, on="Atributo", how="outer").merge(datos_SerieA, on="Atributo", how="outer")

# Combinar filas
df_final1.iloc[17] = df_final1.iloc[17].combine_first(df_final1.iloc[18])
df_final1.iloc[15] = df_final1.iloc[15].combine_first(df_final1.iloc[16])

# Modificar datos de una celda
df_final1.iloc[15,5] = df_final1.iloc[15,5].replace("Serie A", "") 

# Crear los df para las graficas
# DF1
df_participantes = df_final1[df_final1["Atributo"] == "Participantes"].T
df_participantes = df_participantes.drop(df_participantes.index[0])
df_participantes.columns = [str(col) if isinstance(col, int) else col for col in df_participantes.columns]
df_participantes = df_participantes.rename(columns={'22': 'Numero_Equipos'})
df_participantes.map(str)
df_participantes.reset_index()
df_participantes['Numero_Equipos'] = df_participantes['Numero_Equipos'].replace(r'\D', '', regex=True).astype(int)
df_participantes.iloc[2] = df_participantes.iloc[2].replace(182324, 18)
# Grafica 1
sns.barplot(x=df_participantes.index, 
            y=df_participantes["Numero_Equipos"],
            data=df_participantes,
            palette=["#33B5FF", "#FFBB33"])

plt.gca().spines["top"].set_visible(False)
plt.ylabel("Número")
plt.xlabel("Liga")
plt.title('Participantes por liga')
plt.show

# DF2
df_ganadores = df_final1[df_final1["Atributo"] == "Más Campeonatos"].T
df_ganadores.drop(df_ganadores.index[0])
df_ganadores['Equipo_Nombre'] = df_ganadores[17].str.extract(r'([^(]+)')
df_ganadores['Numero'] = df_ganadores[17].str.extract(r'\((\d+)')
df_ganadores = df_ganadores.drop(df_ganadores.index[0])
df_ganadores = df_ganadores.drop(17, axis = 1)
df_ganadores["Numero"] = df_ganadores["Numero"].astype(int)

# Grafica 2
fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (15, 5))
sns.barplot(x=df_ganadores["Equipo_Nombre"],
            y=df_ganadores["Numero"],
            data=df_ganadores,
            hue = df_ganadores.index)
axes.set_title('Equipos con más nº de ligas')
axes.set_ylabel("")
axes.set_xlabel("")
plt.show

# DF3
df_fundacion = df_final1[df_final1["Atributo"] == "Fundación"]
df_fundacion = df_fundacion.drop("Atributo", axis = 1)
df_fundacion = df_fundacion.reset_index()
df_fundacion = df_fundacion.drop("index", axis = 1)
df_fundacion = df_fundacion.replace({"10 de febrero de 1928": 1928, "15 de agosto de 1992": 1992, "24 de agosto de 1963": 1963, "6 de octubre de 1929": 1929})
df_fundacion["Ligue 1"].astype("int64")
df_fundacion = df_fundacion.reset_index()
df_fundacion = df_fundacion.rename(columns={'index': 'Liga'})
df_fundacion=df_fundacion.rename(columns={0: 'Año'})
df_fundacion["Año"] = df_fundacion["Año"].astype("int64")
df_fundacion = df_fundacion.sort_values(by="Año", ascending=True)
fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (15, 8))

sns.lineplot(   x = df_fundacion["Liga"], y = df_fundacion["Año"],
                data = df_fundacion,
                linewidth = 1, 
                palette="mako",
                marker = "o", 
                linestyle = "dashed", 
                errorbar = None)
plt.title("Año fundación ligas")
plt.show