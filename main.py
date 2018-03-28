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
terms_dict = {}
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
#terms_dict["LblInfoPerfilAspirante"] = "Perfil"
#terms_dict["LblInfoObjetivosPrograma"] = "Objetivos"
#terms_dict["LblInfoContenidoPrograma"] = "Contenido"
terms_dict["NUMEROBECAS"] = "Cantidad"
terms_dict["PORCENTAJE"] = "Porcentaje"
terms_dict["TIPO"] = "Cubrimiento"
terms_dict["OBSERVACIONES"] = "Observaciones"


# TODO contar el número de páginas

# Entrar a cada una de las páginas
for page in range(1, 4+1):

    #TODO contar el numero de convocatorias

    # Entrar a cada una de las convocatorias
    for call in range(0, 9+1):

        print("Checking page: ",page,", call: ", call)

        # URL de la página del ICETEX a consultar las becas
        url = "https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
        browser = mechanicalsoup.StatefulBrowser(
            user_agent='UOCBot/0.1: https://github.com/danipilze/UOC_WebScraping')  # se define el browser
        browser.open(url)  # se abre la URL

        # LISTAR TODAS LAS CONVOCATORIAS
        # Esta página muestra las becas solo cuando se da click en la opción "Todas"
        browser.select_form("#form1")  # seleccionamos el formulario
        browser["RBLOpcionBuscar"] = "Todas"  # seleccionamos que busque con la opción "Todas"
        response = browser.submit_selected()  # enviamos el fomulario y capturamos las respuestas
        # en este punto ya tenemos la tabla #GVConvocatorias con la lista de becas
        # hay que proceder a realizar la extracción de datos teniendo en cuenta la paginación

        if(page>1):
            # IR A LA PAGINACIÓN
            browser.select_form("#form1")
            # añadir los parámetros escondidos, usar force=True
            # opción de consulta de convocatoria
            browser.get_current_form().set("__EVENTTARGET", "GVConvocatorias", True)
            # identificador de la convocatoria
            browser.get_current_form().set("__EVENTARGUMENT", "Page$" + str(page), True)
            # enviar el formulario que consulta la convocatoria específica
            responsePage= browser.submit_selected()

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
        # obtener cada fila de la tabla
        rows = soup.findAll("span", {"class": "label1"})

        # diccionario de la convocatoria
        dict = {}
        # alimentar el diccionario con las filas de la convocatoria
        for row in rows:
            if row.has_attr("id"):
                dict.update({row["id"]: row.text})

        numberTable = soup.find("table", {"id": "GVNumeroBecas"})

        if numberTable is not None:
            numbers= numberTable.findAll("tr")

            for number in numbers:
                dict2=copy.copy(dict);
                cells = number.findAll('td')
                if(len(cells)==4):
                    dict2.update({"NUMEROBECAS":cells[0].text})
                    dict2.update({"PORCENTAJE   ": cells[1].text})
                    dict2.update({"TIPO": cells[2].text})
                    dict2.update({"OBSERVACIONES": cells[3].text.replace('\n', ' ').replace('\r', '')})
                    scholarchipCalls.append(dict2)

            browser.close()
            time.sleep(5)  # añadiendo delay



# Current directory where is located the script
currentDir = os.path.dirname(__file__)
filename = "scholarships.csv"
filePath = os.path.join(currentDir, filename)

with open(filePath, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(terms_dict.values())
    for scholarship in scholarchipCalls:
        list = []
        for term in terms_dict:
            list.append(scholarship.get(term))
        writer.writerow(list)
