import mechanicalsoup
import requests
from bs4 import BeautifulSoup

# URL de la página del ICETEX a consultar las becas
url="https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
browser = mechanicalsoup.StatefulBrowser()  # se define el browser
browser.open(url)                           # se abre la URL

# Esta página muestra las becas solo cuando se da click en la opción "Todas"
browser.select_form("#form1")               # seleccionamos el formulario
browser["RBLOpcionBuscar"] = "Todas"        # seleccionamos que busque con la opción "Todas"
response = browser.submit_selected()        # enviamos el fomulario y capturamos las respuestas
# en este punto ya tenemos la tabla #GVConvocatorias con la lista de becas
# hay que proceder a realizar la extracción de datos teniendo en cuenta la paginación

soup = BeautifulSoup(response.text,"html.parser")
children = list(soup.children)


print(children)