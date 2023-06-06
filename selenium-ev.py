#!/usr/bin/env python
# coding: utf-8

# In[383]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pandas as pd
import re
import requests
import os
import json
import logging
import time


# In[ ]:


# read cookies file
def read_cookies(p = 'cookies.txt'):
    cookies = []
    with open(p, 'r') as f:
        for e in f:
            e = e.strip()
            if e.startswith('#'): 
                continue
            k = e.split('\t')
            if len(k) < 3: continue	# not enough data
            # with expiry
            cookies.append({'name': k[-2], 'value': k[-1], 'expiry': int(k[-3])})
    return cookies;


def tryGet(self, url):
    try:
        self.get(url)
        ifErrorRefresh(self)
    except Exception as e:
        print(f"An error occurred while trying to get the URL: {e}")
    
# open browser with cookies
def openBrowser(cookiesPath=''):
    # Patch the tryGet() method to the existing driver object
    webdriver.Chrome.tryGet = tryGet
    browser = webdriver.Chrome()
    if(cookiesPath!=''):
        cookies = read_cookies(cookiesPath)
        for c in cookies: 
            browser.add_cookie(c);
    return browser;


# --------


# download img from url
def downloadImg(image_url='https://www.traca.com.br/capas/1547/1547564.jpg',save_path = 'image.jpg'):
    # Send a GET request to the image URL
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print("Image downloaded successfully.")
    else:
        print("Failed to download the image.")
        
    
# generates EV edit url
def getEditURL(ev_id):
    editBaseURL = 'https://www.estantevirtual.com.br/acervo/editar?livro='
    return editBaseURL+str(ev_id);

# opens new tab 
def newTab(browser):
    browser.execute_script("window.open('about:blank', '_blank');")
    return browser;

# open tab 
def changeTab(browser, number):
    browser.switch_to.window(browser.window_handles[number])
    return browser;

# close current tab
def closeTab(browser):
    browser.close()
    return browser;

# get description text
def getDescr(driver):
    return driver.find_element(By.ID, 'form_descricao').get_attribute('innerHTML');
    
# get traca image url
def getTracaImage(id):
    return 'http://192.168.200.201/rapiscan/data/'+ str(id) + '.jpg'
    # 'https://www.traca.com.br/capas/' + str(id)[0:4] + '/' + str(id) + '.jpg'

# get traca ID from description text 
def idFromDescription(description):
    match = re.search(r'ID (\d+)', description)       
    return match.group(1);


# save cookies
def saveCookies(filepath="cookies.json"):
    cookies = driver.get_cookies()
    with open(filepath, "w") as file:
        json.dump(cookies, file)

# set cookies for login
def setCookies(driver, site='www.estantevirtual.com.br', cookiesPath = 'cookies.txt'):
    driver.get(site);
    # Read the Netscape format cookies from a file
    with open(cookiesPath, "r") as file:
        cookies = file.read()   
    cookie_lines = cookies.splitlines()
    
    # Iterate through each cookie line and add it to the browser
    for line in cookie_lines:
        # Skip blank lines and comments starting with #
        if line.strip() == "" or line.startswith("#"):
            continue
        cookie_parts = line.split("\t")

        newCookie = {
            "domain" : cookie_parts[0],
            "path" : cookie_parts[2],
            "secure" : cookie_parts[3].lower() == "true",
            "expiry" : int(cookie_parts[4]),
            "name" : cookie_parts[5],
            "value" : cookie_parts[6],
        }
        # print(newCookie)
        driver.add_cookie(newCookie)

    driver.refresh()
    return ;
   

# url de busca pelo livro com id traca
def getBuscaId(idTraca):
    return 'https://www.estantevirtual.com.br/acervo?sub=listar&ativos=0&alvo=descr&pchave='+str(idTraca)


# remove 'editora' da string em suas diversas formas
def removeEditora(str):
    return str.replace('Editora','').replace('editora','').replace('EDITORA','').replace('  ',' ')

    
# editar do primeiro elemento da lista de acervo
def getLinkEditar(driver):
    tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')
    trs = tbody.find_elements(By.CSS_SELECTOR, 'tr')    
    if(len(trs)>0):    
        editar_url = trs[0].find_elements(By.CSS_SELECTOR, 'a')[1].get_attribute('href')
        driver.get(editar_url)
        return True;
    else:
        return False;
        
# get excel file
def getExcelFile(directory='./'):
    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            return file
    return None
    

# salvar 
def clickSalvar(driver):
    botaoSalvar = driver.find_element(By.CSS_SELECTOR, "#js-btn-acervo-label")
    botaoSalvar.click()

def getImageFilePath(id):
    id = str(id)
    folders = [
        './imgs/',
        './capas/data/',
        './imgs/datantigo/',
        './capas/capas/',
        './capas/capas/flat/',
              ]
    for basePath in folders:
        if(os.path.exists(basePath+str(id)+'.jpg')):
            return basePath+str(id)+'.jpg';
        if(os.path.exists(basePath+str(id)+'.jpeg')):
            return basePath+str(id)+'.jpeg';
        if(os.path.exists(basePath+str(id)+'.jpe')):
            return basePath+str(id)+'.jpe';
    print('Imagem não encontrada em nenhuma pasta')
    return False
    
    
#lista imagens do path
def listaImagens(path = './imgs'):
    return [f for f in os.listdir('./imgs') if f.endswith(".jpg")] 

def tracaDownloadImgById(id):
    id = str(int(id)).replace('.0','')
    image_url = getTracaImage(str(id))
    response = requests.get(image_url)    
    filepath = getImageFilePath(str(id))
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print("Image downloaded successfully:                       ", filepath, end="\r")
    else:
        print("Failed to download the image:                " + image_url)
        print(response)
           


def log(str):
    logging.basicConfig(filename='logfile.log', level=logging.INFO)
    logging.info(str)        

def checaRepetidos(driver,opts):
    qtde = len(driver.find_elements(By.CSS_SELECTOR, '.acervo-titulo'))
    if qtde > 1:
        log(time.strftime('%x %X') + ' Multiple results found, ID: '+ opts['tracaId'])
    else: 
        log(time.strftime('%x %X') + ' Processando, ID: '+ opts['tracaId'])

def ifErrorRefresh(driver, count=5):
    bodys = len(driver.find_elements(By.CSS_SELECTOR, 'tbody'))
    errors = len(driver.find_elements(By.CSS_SELECTOR, '.error-message'))
    if( bodys < 1 or  errors > 0):
        print('.. Sleeping ..'+ str(count)+'seconds                                   ', end='\r')
        time.sleep(count)
        driver.refresh()
        ifErrorRefresh(driver, count+1)


# In[391]:


# le os dados e coloca a capa no livro
def colocarCapa(driver, opts = {}):       
    trocouCapa = False

    # pega ID
    tracaId = ''
    if(not 'tracaId' in opts.keys()):
        print('ID traca não passado, tentando pegar da página..')
        descr = getDescr(driver)
        tracaId = idFromDescription(descr)
    else: 
        tracaId = opts['tracaId']
        tracaImg = getTracaImage(tracaId)

    # se o livro não tem capa, coloca
    try:
        e = driver.find_element(By.CSS_SELECTOR, '.preview-div p')
        textoCapa = e.get_attribute('innerHTML')
    except NoSuchElementException:
        return False;        

    
    if( 'Nenhuma capa cadastrada' in textoCapa):
        try:
            # coloca a imagem no form
            # capa = driver.find_element(By.CSS_SELECTOR, "#form_capa")
            capa = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_capa")))
            image_path = os.getcwd() + "/imgs/" + str(tracaId) + '.jpg'
            if os.path.exists(image_path):
                capa.send_keys(image_path)
                log(time.strftime('%x %X') + ' Colocando capa '+ image_path)
                trocouCapa = True;
                time.sleep(2)
            else:
                log(time.strftime('%x %X') + ' Capa não encontrada '+ image_path)
                print("Image file does not exist")
                trocouCapa = False;
        except NoSuchElementException:
            return False;        
    else:
        log(time.strftime('%x %X') + ' Já possui capa ')


    # Adiciona texto na descrição
    if(trocouCapa):
        try:
            descricao = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_descricao")))
            descricao.send_keys(' A imagem corresponde ao exemplar anunciado.')
            time.sleep(0.1)
        except NoSuchElementException:
            return False;
    


        
    # se não tem ISBN coloca o ano 1989
    isbn = opts['row']['ISBN/ISSN']
    ano = opts['row']['Ano*']
    if(trocouCapa and ano>1989 and str(isbn)=='nan'):
        try:
            ano = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_ano")))
            # ano = driver.find_element(By.CSS_SELECTOR, "#form_ano")
            ano.clear()
            ano.send_keys('1989')
        except NoSuchElementException:
            return False;

            
        
    # se passado estante nos opts, trocar a estante
    if(trocouCapa and 'estante' in opts.keys()):
        print('Livro colocado na estante: ' + str(opts['estante']) + '            ', end="\r")
        estante = driver.find_element(By.CSS_SELECTOR, "#form_estante")
        estante.send_keys(opts['estante'])

    # arrumar nome da editora
    estante = driver.find_element(By.CSS_SELECTOR, "#form_editora")
    if trocouCapa and ('editora' in estante.get_attribute('value')
      or 'Editora' in estante.get_attribute('value') 
      or 'EDITORA' in estante.get_attribute('value') 
      ):
        estante.clear()
        estante.send_keys(removeEditora(estante.get_attribute('value')))   
    return trocouCapa;


# Download Images for Ids in the excel file
def downloadImgs(df, startingindex=1, limitIndex=1000):
    for index, row in df.iterrows():
        idTraca = row['ID']
        if(startingindex>=index and index<limitIndex and str(idTraca) != 'nan'):
            tracaDownloadImgById(idTraca);

# robot handler
def runRobotOnId(idTraca, estanteNome, row):
    # driver.get('https://www.estantevirtual.com.br/acervo')
    driver.get(getBuscaId(idTraca))
    run = ifErrorRefresh(driver)
    if(run=='stop'): return 'stop';
    print('buscando livro de ID = ' + str(idTraca) + '                ' ,end="\r")   
    checaRepetidos(driver, {'tracaId' : str(idTraca)})
    temResultado = getLinkEditar(driver)
    if(not temResultado):
        return ;
    print('Editando livro de ID = ' + str(idTraca) + '                ',end="\r")
    trocouCapa = False
    trocouCapa = colocarCapa(driver,{'estante' : estanteNome, 'tracaId':idTraca, 'row':row})
    if trocouCapa: 
        clickSalvar(driver)
    

# bot call
def robotCall(index,row):
        if(row['ID'] == 'nan'): 
            print('linha sem ID: ', index)
            return ;
        idTraca = int(str(row['ID']).replace('.0',''))
        isbn = row['ISBN/ISSN']
        pathimg = getImageFilePath(str(idTraca))
        estanteNome = row['Estante*']
        # print('livro...' + str(index), idTraca, estanteNome)
        if(estanteNome and os.path.exists(pathimg)):                
            # print('certinho?')
            return runRobotOnId(int(idTraca),estanteNome, row)
        else:
            log('Imagem não encontrada: ' +  pathimg)
            print('Imagem não encontrada: ', pathimg + '                                 ', end='\r')

  

# robot calling
def startRobot(minindex, maxindex):
    for index, row in df.iterrows():
        run = 'running'
        if('quero-ajuda' in driver.current_url):
            print('Detectado página de ajuda... Robot Stopping')
            return 'stop';
        if(index>maxindex):
            break;
        elif(index>minindex): 
            ifErrorRefresh(driver)
            run = robotCall(index,row)



# In[104]:


# para ler os IDs etc
df0 = pd.read_excel(getExcelFile(), converters={'ID': str})


# In[122]:


# abre o browser
driver = openBrowser()
driver.get('https://www.estantevirtual.com.br/')
setCookies(driver, 'https://www.estantevirtual.com.br', 'cookies.txt')
driver.get('https://www.estantevirtual.com.br/acervo')


# In[ ]:


df = df0[df0['ID'] < '1532265']
startRobot(5000,50000)




# In[372]:





# In[378]:


# driver.get('https://www.estantevirtual.com.br/')
# setCookies(driver, 'https://www.estantevirtual.com.br', 'cookies.txt')

# driver.get('https://www.estantevirtual.com.br/acervo')
# setCookies(driver, 'https://www.estantevirtual.com.br/acervo', 'cookies.txt')
# driver.get(getBuscaId(613080))
# getLinkEditar(driver).click()

# # ou #  driver.get('https://www.estantevirtual.com.br/acervo/editar?livro=3867086856')

# colocarCapa(driver)

# limitIndex= 1000
# downloadImgs(df,startingindex=10000, limitIndex=100000)


# runRobotOnId(1547138, 'outros')


# tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')
# trs = tbody.find_elements(By.CSS_SELECTOR, 'tr')


# driver.get(getBuscaId(1541032))
# getLinkEditar(driver)


# df = df0[df0['ID'] < '1544605']
# df = df0[df0['ID'] < '1538904']
# df = df0[df0['ID'] < '1538725']
# df = df0[df0['ID'] < '1537395']
# df = df0[df0['ID'] < '1532704']
# df = df0[df0['ID'] < '1532265']



# df['ID'].head(5)

# 1544605

# driver.get('https://www.estantevirtual.com.br/acervo?sub=listar&ativos=0&alvo=descr&pchave=1544605')
# tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')
# trs = tbody.find_elements(By.CSS_SELECTOR, 'tr')


# trs[0].get_attribute('innerHTML')


# 
# 'quero-ajuda' in driver.current_url


# In[ ]:




