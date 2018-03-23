import mechanicalsoup
import requests
from bs4 import BeautifulSoup

# URL de la página del ICETEX a consultar las becas
url = "https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
browser = mechanicalsoup.StatefulBrowser()  # se define el browser
browser.open(url)  # se abre la URL

# Esta página muestra las becas solo cuando se da click en la opción "Todas"
browser.select_form("#form1")  # seleccionamos el formulario
browser["RBLOpcionBuscar"] = "Todas"  # seleccionamos que busque con la opción "Todas"
response = browser.submit_selected()  # enviamos el fomulario y capturamos las respuestas
# en este punto ya tenemos la tabla #GVConvocatorias con la lista de becas
# hay que proceder a realizar la extracción de datos teniendo en cuenta la paginación

""""
# obtener el soup a partir de la respuesta a la acción anterior
soup = BeautifulSoup(response.text, "html.parser")
# obtener la tabla que contiene las becas
table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "GVConvocatorias")
# obtener cada fila de la tabla de becas
rows = table.findAll(lambda tag: tag.name == 'tr')

# para cada fila
for row in rows:
    cells = row.findAll('td')  # encontrar las celdas
    if (len(cells) > 0):
           print(cells[0])
"""""


# Entrar a cada una de las convocatorias
#for i in (0,9):
browser2 = browser
browser2.select_form("#form1")
browser2.get_current_form().set("__EVENTTARGET", "GVConvocatorias",  True)
browser2.get_current_form().set("__EVENTARGUMENT", "$0",  True) # activar el for y reemplazar el 0 con i


response2 = browser2.submit_selected()

print(response2.text)

