import os
import csv
import copy
import time
import mechanicalsoup
import requests
from bs4 import BeautifulSoup

# crear la lista de convocatorias
scholarchipCalls = []

# diccionario de cabecera y campos
terms = {}
terms["LblInfoPais"] = "País"
terms["LblInfoPrograma"] = "Programa"
terms["LblInfoArea"] = "Área"
terms["LblInfoOferente"] = "Oferente"
terms["LblInfoTipoCurso"] = "Tipo"
terms["LblInfoTituloaObtener"] = "Título"

# añadir la cabecera
# scholarchipCalls.append(terms)

# URL de la página del ICETEX a consultar las becas
url = "https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
browser = mechanicalsoup.StatefulBrowser(user_agent='UOCBot/0.1: https://github.com/danipilze/UOC_WebScraping')  # se define el browser

try:
    browser.open(url)  # se abre la URL
except requests.exceptions.ConnectionError:
    print("No connection")
    SystemExit.code(0)


# Esta página muestra las becas solo cuando se da click en la opción "Todas"
browser.select_form("#form1")  # seleccionamos el formulario
browser["RBLOpcionBuscar"] = "Todas"  # seleccionamos que busque con la opción "Todas"
response = browser.submit_selected()  # enviamos el fomulario y capturamos las respuestas
# en este punto ya tenemos la tabla #GVConvocatorias con la lista de becas
# hay que proceder a realizar la extracción de datos teniendo en cuenta la paginación

# Entrar a cada una de las convocatorias
for i in range(0, 3):
    time.sleep(5) # añadiendo delay
    browser2 = copy.copy(browser)
    browser2.select_form("#form1")
    # añadir los parámetros escondidos, usar force=True
    # opción de consulta de convocatoria
    browser2.get_current_form().set("__EVENTTARGET", "GVConvocatorias", True)
    # identificador de la convocatoria
    browser2.get_current_form().set("__EVENTARGUMENT", "$" + str(i), True)
    # enviar el formulario que consulta la convocatoria específica
    response2 = browser2.submit_selected()

    # obtener el soup a partir de la respuesta a la acción anterior
    soup = BeautifulSoup(response2.text, "html.parser")
    # obtener cada fila de la tabla
    rows = soup.findAll("span", {"class": "label1"})

    # diccionario de la convocatoria
    dict = {}
    # # alimentar el diccionario con las filas de la convocatoria
    for row in rows:
        if row.has_attr("id"):
            dict.update({row["id"]: row.text})
    print(dict)
    scholarchipCalls.append(copy.copy(dict))
    browser2.close()

browser.close()

# Current directory where is located the script
currentDir = os.path.dirname(__file__)
filename = "scholarships.csv"
filePath = os.path.join(currentDir, filename)


with open(filePath, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(terms.values())
    for scholarship in scholarchipCalls:
        list = []
        for term in terms:
            list.append(scholarship.get(term))
        writer.writerow(list)
