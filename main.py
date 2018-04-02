import os
import csv
import copy
import time
import mechanicalsoup
from tqdm import tqdm
from bs4 import BeautifulSoup

### PARAMETROS DE CAMPOS A LEER

ID_label = "LblInfoConvocatoria"

# diccionario de cabecera y campos
terms_dict = {}
terms_dict[ID_label] = "Código"
terms_dict["LblInfoPais"] = "País"
terms_dict["LblInfoPrograma"] = "Programa"
terms_dict["LblInfoArea"] = "Área"
terms_dict["LblInfoOferente"] = "Oferente"
terms_dict["LblInfoTipoCurso"] = "Tipo curso"
terms_dict["LblInfoTituloaObtener"] = "Título"
terms_dict["LblInfoFechaInicio"] = "Inicio"
terms_dict["LblInfoFechaTerminacion"] = "Fin"
terms_dict["LblInfoDuracion"] = "Duración"
terms_dict["LblInfoIdioma"] = "Idioma"
terms_dict["LblInfoFechaRecepcion"] = "Entrega documentos"
terms_dict["LblInfoFechaComite"] = "Fecha comité becas"
terms_dict["LblInfoInstitucion"] = "Institución"
terms_dict["LblInfoCiudad"] = "Ciudad"
# terms_dict["LblInfoPerfilAspirante"] = "Perfil"
# terms_dict["LblInfoObjetivosPrograma"] = "Objetivos"
# terms_dict["LblInfoContenidoPrograma"] = "Contenido"
terms_dict["NUMEROBECAS"] = "Cantidad"
terms_dict["PORCENTAJE"] = "Porcentaje"
terms_dict["TIPO"] = "Cubrimiento"
terms_dict["OBSERVACIONES"] = "Observaciones"

userAgent= 'UOCBot/0.1: https://github.com/danipilze/UOC_WebScraping'

def cleanValue(value):
    value = value.replace("\n", "")
    value = value.replace("\r", "")

    return value


def getPageNumber():
    # URL de la página del ICETEX a consultar las becas
    url = "https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
    # se define el browser con el user_agent
    browser = mechanicalsoup.StatefulBrowser(user_agent=userAgent)
    browser.open(url)  # se abre la URL

    # LISTAR TODAS LAS CONVOCATORIAS
    # esta página muestra las becas solo cuando se da click en la opción "Todas"
    # seleccionamos el formulario
    browser.select_form("#form1")
    # seleccionamos que busque con la opción "Todas"
    browser["RBLOpcionBuscar"] = "Todas"
    # enviamos el fomulario y capturamos las respuestas
    response = browser.submit_selected()
    # en este punto ya tenemos la tabla #GVConvocatorias con la lista de becas
    # hay que proceder a realizar la extracción de datos teniendo en cuenta la paginación

    soup = BeautifulSoup(response.text, "html.parser")
    tr =  soup.find("tr", {"align": "right"})
    table = tr.find("table")
    tds = table.findAll("td")
    number = len(tds)

    browser.close()

    return number


def getScholarships():
    # crear la lista de convocatorias
    scholarchipCalls = []

    calls_max_index = 9
    pages_max_index = getPageNumber()
    total_calls = (calls_max_index + 1) * pages_max_index
    progress_bar = tqdm(total=total_calls)

    ### INICIAR LA NAVEGACIÖN

    # Entrar a cada una de las páginas
    for page in range(1, pages_max_index + 1):

        # TODO contar el numero de convocatorias

        # entrar a cada una de las convocatorias desplegadas en esa página
        for call in range(0, calls_max_index + 1):

            # URL de la página del ICETEX a consultar las becas
            url = "https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
            # se define el browser con el user_agent
            browser = mechanicalsoup.StatefulBrowser(
                user_agent=userAgent)
            browser.open(url)  # se abre la URL

            # LISTAR TODAS LAS CONVOCATORIAS
            # esta página muestra las becas solo cuando se da click en la opción "Todas"
            # seleccionamos el formulario
            browser.select_form("#form1")
            # seleccionamos que busque con la opción "Todas"
            browser["RBLOpcionBuscar"] = "Todas"
            # enviamos el fomulario y capturamos las respuestas
            response = browser.submit_selected()
            # en este punto ya tenemos la tabla #GVConvocatorias con la lista de becas
            # hay que proceder a realizar la extracción de datos teniendo en cuenta la paginación

            if (page > 1):
                # IR A LA PAGINACIÓN
                browser.select_form("#form1")
                # añadir los parámetros escondidos, usar force=True
                # opción de consulta de convocatoria
                browser.get_current_form().set("__EVENTTARGET", "GVConvocatorias", True)
                # identificador de la convocatoria
                browser.get_current_form().set("__EVENTARGUMENT", "Page$" + str(page), True)
                # enviar el formulario que consulta la convocatoria específica
                responsePage = browser.submit_selected()

            # ENTRAR A LA CONVOCATORIA
            browser.select_form("#form1")
            # añadir los parámetros escondidos, usar force=True
            # opción de consulta de convocatoria
            browser.get_current_form().set("__EVENTTARGET", "GVConvocatorias", True)
            # identificador de la convocatoria
            browser.get_current_form().set("__EVENTARGUMENT", "$" + str(call), True)
            # enviar el formulario que consulta la convocatoria específica
            responseCall = browser.submit_selected()

            # OBTENER DATOS DE LA CONVOCATORIA
            # obtener el soup a partir de la respuesta a la acción anterior
            soup = BeautifulSoup(responseCall.text, "html.parser")
            # obetner el ID de la convocatoria
            ID_element = soup.find("span", {"id": ID_label})
            if ID_element is not None:
                ID_value = ID_element.text
                # crear diccionario de la convocatoria
                dict = {}
                # agregar el ID
                dict.update({ID_label: ID_value})

                # obtener cada fila de la tabla las cuales contienen los datos
                rows = soup.findAll("span", {"class": "label1"})

                # alimentar el diccionario con las filas de la convocatoria
                for row in rows:
                    # si es un un campo que nos interesa
                    if row.has_attr("id") & terms_dict.keys().__contains__(row["id"]):
                        value = cleanValue(row.text)
                        dict.update({row["id"]: value})

                modalitiesTable = soup.find("table", {"id": "GVNumeroBecas"})
                modalities = modalitiesTable.findAll("tr")
                tittles = modalitiesTable.findAll("th")

                # diferenciar beca por cada una de las modalidades que se ofrece
                for modality in modalities:
                    dict2 = copy.copy(dict)
                    # obtener el contenido de las celdas
                    cells = modality.findAll('td')
                    # si efectivamente es una de las filas de contenido
                    if (len(cells) == 4):
                        for j in range(0,4):
                            # si es un campo que nos interesa
                            if(terms_dict.keys().__contains__(tittles[j].text)):
                                value = cleanValue(cells[j].text)
                                dict2.update({tittles[j].text: value})
                        scholarchipCalls.append(dict2)

            # cerrar el navegador
            browser.close()
            # actualizar la barra de progreso
            progress_bar.update(1)
            # añadiendo delay
            time.sleep(0.1)

    # cerrar barra de priogreso
    progress_bar.close()
    return scholarchipCalls


scholarchipCalls = getScholarships()

### PARAMETROS ESCRITURA DEL ARCHIVO DE SALIDA

# directorio actual donde se va a ubicar el archivo
currentDir = os.path.dirname(__file__)
# nombre del archivo
filename = "scholarships.csv"
# ruta completa del archivo
filePath = os.path.join(currentDir, filename)
# separador de columnas
fieldSeparator = ','

### ESCRIBIR ARCHIVO DE SALIDA

# escribir archivo de salida
with open(filePath, 'w', newline='', encoding='utf-8') as csvFile:
    # se usa un escritor de diccionarios
    writer = csv.DictWriter(csvFile, delimiter=fieldSeparator, fieldnames=terms_dict, quoting=csv.QUOTE_ALL)

    # escribir cabecera personalizada
    writer.writerow(terms_dict)

    # escribir valores por cada beca
    for scholarship in scholarchipCalls:
        writer.writerow(scholarship)
