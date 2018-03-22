import mechanicalsoup
from bs4 import BeautifulSoup


url="https://www.icetex.gov.co/SIORI_WEB/Convocatorias.aspx?aplicacion=1&vigente=true"
browser = mechanicalsoup.StatefulBrowser()
browser.open(url)

#seleccionar todas las becas
browser.select_form("#form1")
browser["RBLOpcionBuscar"] = "Todas"
response = browser.submit_selected()

soup = BeautifulSoup(response.text,"html.parser")
children = list(soup.children)



opcion2 = soup.find_all(id="");

print(children)