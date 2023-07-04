#!/usr/bin/env python
# coding: utf-8

# In[19]:

 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from time import sleep
import pandas as pd
import numpy as np
import os
import json
import logging
import time
import threading
import tkinter as tk
from PIL import ImageTk, Image
import re


# cli params
import sys
cli_planilha = [x for x in sys.argv if '.xlsx' in x]
cli_logfile = [x for x in sys.argv if '.log' in x]
cli_gui = [x for x in sys.argv if 'gui' in x]
cli_profile= [x for x in sys.argv if 'profile' in x]
logfile_name = 'logfile.log'
if(len(cli_logfile)>0): logfile_name=cli_logfile[0]


profileDirectory = './chrome/profile_directory'
if(len(cli_profile)>0):
    profileDirectory = './chrome/'+cli_profile[0]
shared = {}
shared['vars'] = {'stop' : False, 'lastRow':{'ID':'1515405'}}
shared['texts'] = {
    't1': "No results yet",
    't2': "No results yet",
    't3': "No results yet",
    't4': "No results yet",
    # 'print': "No results yet",
    # 'img404': "No results yet",
    # 'buscaresult': "No results yet",
    # 'temcapa': "No results yet",
    # 'estante': "No results yet",
    # 'colocacapa': "No results yet",
    # 'busca': "No results yet",
    # 'busca404': "No results yet",
    # 'id404': "No results yet",
    # 'editproblem': "No results yet",
    # 'editaction': "No results yet",
    'imgpath': "",
}
file_excel =''



# In[24]:


def ifErrorRefresh(driver, count=5):
    if('ajuda' in driver.current_url) or ('stop' in driver.current_url):
        return 'stop';
    bodys = len(driver.find_elements(By.CSS_SELECTOR, 'tbody'))
    errors = len(driver.find_elements(By.CSS_SELECTOR, '.error-message'))
    if( bodys < 1 or  errors > 0):
        sleepsec = count
        if(sleepsec>30): sleepsec = 30;
        msg('Found an error.. Sleeping.. '+ str(sleepsec)+' seconds',)
        print('.. Sleeping ..'+ str(count)+'seconds                                   ', end='\r')
        time.sleep(sleepsec)
        driver.get(driver.current_url)
        
        ifErrorRefresh(driver, count+1)
    return True;
        

# open browser
def openBrowser():
    chrome_options = Options()

    # Set the user data directory to store the profile
    chrome_options.add_argument('--user-data-dir='+profileDirectory)
    cli_browser = len([x for x in sys.argv if 'browser' in x])
    if(cli_browser<1): 
        chrome_options.add_argument('--headless')    
    
    # Add cookies to the Chrome Preferences
    chrome_options.add_experimental_option('prefs', {
        'profile.default_content_settings.cookies': 1,
        'profile.default_content_setting_values.cookies': 1,
        'profile.managed_default_content_settings.cookies': 1,
        # Add more preferences as needed
    })
       
    # Create a new ChromeDriver instance with the configured options
    driver = webdriver.Chrome(options=chrome_options)
    return driver;




# set cookies for login
def setCookies(driver, site='www.estantevirtual.com.br', cookiesPath = 'cookies.txt'):
    driver.get('https://'+site);
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
            "domain" : site,
            # "domain" : cookie_parts[0],
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
   

# get excel file
def getExcelFile(directory='./'):
    if(len(cli_planilha)>0): 
        return cli_planilha[0]    

    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            return file
    return None


    

# # # # # # # # # # # # 
#     Browser Stuff
# # # # # # # # # # # #     


# DOM 
# get description text
def getDescr(driver):
    return driver.find_element(By.ID, 'form_descricao').get_attribute('innerHTML');
    
# DOM 
# get traca ID from description text 
def idFromDescription(driver):
    description = getDescr(driver)
    match = re.search(r'ID (\d+)', description)       
    return match.group(1);

# DOM 
# botao editar do primeiro elemento da lista de acervo (página de resultados da busca)
def getLinkEditar(driver):
    tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')
    trs = tbody.find_elements(By.CSS_SELECTOR, 'tr')    
    if(len(trs)>0):    
        editar_url = trs[0].find_elements(By.CSS_SELECTOR, 'a')[1].get_attribute('href')
        driver.get(editar_url)
        return True;
    else:
        return False;
        

# Browser
# url de busca pelo livro com id traca
def getBuscaId(idTraca):
    return 'https://www.estantevirtual.com.br/acervo?sub=listar&ativos=0&alvo=descr&pchave='+str(idTraca)


# remove 'editora' da string em suas diversas formas
def removeEditora(str):
    return str.replace('Editora','').replace('editora','').replace('EDITORA','').replace('  ',' ')

  

    
# DOM 
# clica em salvar (página de edição do livro)
def clickSalvar(driver):
    botaoSalvar = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#js-btn-acervo-label")))
    botaoSalvar.click()


# local
# procura o path da imagem nos arquivos locais
def getImageFilePath(id):
    id = str(id)
    with open('folders.txt', 'r') as file:
        folders = file.readlines()
        folders = [line.replace('\n','') for line in folders]

    # folders = [
    #     '/home/nathan/traca/imgs/',
    #     '/home/nathan/traca/capas/',
    #     '/home/nathan/traca/capas/capas/',
    #     '/home/nathan/traca/capas/capas/flat/',
    #     '/home/nathan/traca/capas/data/',
    #     '/home/nathan/traca/capas/datantigo/',
    #     './capas/',
    #           ]

    for basePath in folders:
        pathimg = basePath+str(id)+'.jpg'
        if(os.path.exists(pathimg)):
            return pathimg
        pathimg = basePath+str(id)+'.jpeg'
        if(os.path.exists(pathimg)):
            return pathimg
        pathimg = basePath+str(id)+'.jpe'
        if(os.path.exists(pathimg)):
            return pathimg

    msg('Imagem não encontrada em lugar algum: '+  str(id), type='img404')
    return False;
    


# # # # # # # # 
# Messaging     
# # # # # # # #     


# wrap for tkinter
def setText(name,value):
    if(type(shared['texts'][name]=='str')):
        shared['texts'][name] = value;
    else:
        shared['texts'][name] = value;


def msg(msg, type='print'):
    sp = ' ' * 66
    if type in ['print', 'img404','buscaresult', 'temcapa', 'estante','colocacapa', 'busca','busca404', 'id404', 'editproblem','editaction']:
        print(msg + sp, end='\r')
    if type in ['img404', 'buscaresult', 'temcapa','colocacapa','busca404','id404']:
        log(msg)

    if('busca' in type):
        setText('t2',msg)
    elif('capa' in type):
        setText('t3',msg)
    elif('404' in type):
        setText('t4',msg)
    else:#(type in ['print'])
        setText('t1',msg)


def log(str):
    logging.basicConfig(filename=logfile_name, level=logging.INFO)
    logging.info(time.strftime('%x %X') + ':   ' +str)        

def checaRepetidos(driver,opts):
    qtde = len(driver.find_elements(By.CSS_SELECTOR, '.acervo-titulo'))
    if qtde > 1:
        msg('Multiple results found, ID: '+ opts['tracaId'].zfill(7),type='buscaresult')
    else: 
        msg(str(qtde)+' results found: '+ opts['tracaId'].zfill(7), type='buscaresult')
        
# para ler os IDs etc
def loadExcelFile(file_name=''):
    if file_name=='':
        file_excel = getExcelFile()
        print('Carregando arquivo: '+ str(file_excel))
        df0 = pd.read_excel(getExcelFile(), converters={'ID': int})
    else:
        print('Carregando arquivo: '+ file_name)
        df0 = pd.read_excel(file_name, converters={'ID': int})        
    return df0


# para parar o bot
def stopBots():
    shared['vars']['stop'] = True
    return ;


def saveLastRow(row,save):
    if save!='':
        shared['vars']['lastRow'] = row;
    else:        
        shared['vars'][save] = row;
    return ;





# In[25]:


# Robô mais enxuto:
# capa cadastrada para esse livro?
def temCapa(driver):
    txtSemCapa = 'Nenhuma capa cadastrada'
    textoCapa = txtSemCapa
    try:
        e = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".preview-div p")))
        # e = driver.find_element(By.CSS_SELECTOR, '.preview-div p')
        textoCapa = e.get_attribute('innerHTML')
    except NoSuchElementException:
        return True;
    return not (txtSemCapa in textoCapa) ;

# altera ano para 1989 (Onde o ISBN não é necessário)
def alteraAno(driver, anoPara='1989'):
    try:
        ano = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_ano")))
        ano.clear()
        ano.send_keys(anoPara)
    except NoSuchElementException:
        return False;
    return True;

# atualiza descrição conforme solicitado
def alteraDescricao(driver):
    addTexto = ' A imagem corresponde ao exemplar anunciado.'
    try:
        descricao = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_descricao")))
        descricaoTexto = descricao.get_attribute('innerHTML')
        if not (addTexto in descricaoTexto):
            descricao.send_keys(' A imagem corresponde ao exemplar anunciado.')
    except NoSuchElementException:
        return False;
    return True;

# coloca o livro na estante
def alteraEstante(driver,estante):
    e = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_estante")))
    msg('Livro colocado na estante: ' + estante, type="estante")
    e.send_keys(estante)
    return True;

# arruma o nome da editora
def alteraEditora(driver):
    edForm = driver.find_element(By.CSS_SELECTOR, "#form_editora")
    edNome = edForm.get_attribute('value')
    if ('editora' in edNome.lower()):
        msg('Alterando nome da editora',type='editaction')
        edForm.clear()
        edForm.send_keys(removeEditora(edNome))            
    return True;


# coloca a imagem no form
def alteraCapa(driver, path):
    try:
        capa = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_capa")))
        capa.send_keys(path)
        msg('Colocando capa ' + path, type='colocacapa')
    except Exception as e:
        return False;
    setText('imgpath',path)
    return True;




def editaLivro(driver, capaPath, estante, idTraca=0, editaEditora=True, editaDescricao=True, ano1989=True):
    idTraca = str(idTraca).zfill(7)
    time.sleep(0.1)
    jaTemCapa = temCapa(driver)

    # se já tem capa não faz o resto
    if(jaTemCapa):
        msg('Capa já existe'+capaPath, type='temcapa')
        return False;

    # se não tiver capa edita tudo que precisa
    tudoOk = True;
    if(editaEditora): 
        tudoOk = tudoOk and alteraEditora(driver);
    if(not tudoOk): msg('Problema na alteração da Editora',type='editproblem')

    if(editaDescricao): 
        tudoOk = tudoOk and alteraDescricao(driver);
    if(not tudoOk): msg('Problema na alteração da Descrição',type='editproblem')
    
    if(ano1989): 
        tudoOk = tudoOk and alteraAno(driver);
    if(not tudoOk): msg('Problema na alteração do Ano',type='editproblem')

    est = alteraEstante(driver,estante)
    if(not est): msg('Problema na alteração da Estante',type='editproblem')
    
    capa = alteraCapa(driver, capaPath)
    if(not capa): msg('Problema na alteração da Capa',type='editproblem')
    msg('tudoOk = '+str(tudoOk) + ' ; est = '+str(est) + ' ; capa = '+str(capa),type='print')
    return (tudoOk and est and capa);
    


# v2
# entra na página de edição do livro
def getBookEditPage(driver, myId):
    msg('buscando livro de ID: ' + str(myId), type='busca')
    driver.get(getBuscaId(myId))

    run = ifErrorRefresh(driver)
    if(run=='stop'): return 'stop';

    checaRepetidos(driver, {'tracaId' : str(myId)})
    temResultado = getLinkEditar(driver)
    if(not temResultado):
        return False;
    else:
        msg('Editando livro de ID: ' + str(myId),type="edit")
        return True



def callRobot_v2(driver, row):

    # dados da row
    idTraca = int(str(row['ID']).replace('.0',''))

    # Dado da Estante
    if('Estante*' in row):
        estante = row['Estante*']
    elif('Estante' in row):
        estante = row['Estante']
    else: 
        return False;

    isbn = row['ISBN/ISSN']

    # Dado do Ano
    if('Ano*' in row):
        ano = row['Ano*']
    elif('Ano' in row):
        ano = row['Ano']
    else: 
        return False;

    # confere ID 
    if(idTraca == 'nan'): 
        msg('linha sem ID.. ID Estante: '+ str(row['ID Estante']), type='id404')
        return False;

    # procura capa
    capaPath = getImageFilePath(str(idTraca))    
    if(not capaPath):
        msg('Capa não encontrada: ' + str(idTraca),type="print")        
        return False;
    else:
        msg('Capa encontrada: ' + str(capaPath),type="print")        


    # BROWSER - busca livro no site da EV 
    buscaLivro = getBookEditPage(driver, idTraca)
    if not buscaLivro:
        msg('Livro não encontrado', type='busca404')
        return ifErrorRefresh(driver);
    if(ifErrorRefresh(driver)=='stop'): return 'stop';

    # BROWSER - edita livro no site da EV 
    edicaoLivro = editaLivro(driver, capaPath, estante, 
               editaEditora = True, 
               editaDescricao = True, 
               idTraca = idTraca,             
               ano1989= (ano>1989 and str(isbn).lower()=='nan'))

    # retornou da edição
    if(edicaoLivro):
        msg('Tudo Ok... Salvando', type='print')
        clickSalvar(driver);    
    else: 
        msg('Teve alguma exceção na edição, este não será salvo', type='print')
        return False

    # refresh if Error
    return ifErrorRefresh(driver);



def read_last_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        last_line = lines[-1].strip()  # Remove any leading/trailing whitespace
        last_line2 = lines[-2].strip()  # Remove any leading/trailing whitespace
        return str(last_line)+str(last_line2)

def extract_tracaId(string):
    pattern = r'\d{7}'  # Matches a sequence of 7 digits
    matches = re.findall(pattern, string)
    return matches        

def getLastIdFromLogsFile():
    return(extract_tracaId(read_last_line(logfile_name)))[0]




# In[26]:


df0 = ''
# Main Loop
def startRobot(df=df0, minID=1, maxID=1600000, driver='', namespace=''):
    print('Iniciando Robô entre IDs '+ str(minID) + ' e ' + str(maxID))

    # filtra dados
    df1 = df;
    print('Lendo dados... '+str(len(df1)) + ' rows')
    df1 = df1[df1['ID'] >= int(minID)]
    df1 = df1[df1['ID'] <= int(maxID)]    
    df1 = df1.sort_values(by=['ID'], ascending=False, ignore_index=True)
    print('Filtrando dados... '+str(len(df1)) + ' rows')
    if(len(df1)<1): 
        print('Nenhuma row?')    
        return;

    # abre driver
    if(driver==''):
        driver = openBrowser();
    driver.get('https://www.estantevirtual.com.br/acervo')
    print('Browser Aberto')
    
    # iterate over the wqhole df
    print('Iniciando iterador')
    for ind in df1.index:

        # save last processed row for later 
        row = df1.iloc[ind]
        saveLastRow(row,namespace)
        msg('file ' + str(file_excel) + ' row '+str(ind) ,type='print')

        # stop flag
        if(shared['vars']['stop'] == True):
            msg(' Stop Flag detected, stopping..',type='print')
            shared['vars']['stop'] = False
            break;

        # max ID already reached
        if(str(row['ID']).zfill(8) > str(maxID).zfill(8)):
            msg('ID máximo ultrapassado... ignoring',type='print')
            continue ;

        # min ID reached
        if(str(row['ID']).zfill(8) < str(minID).zfill(8)):
            msg('Índice mínimo ultrapassado... Robot Stopping',type='print')
            break;

        # Refresh if Errors
        if(ifErrorRefresh(driver)=='stop'):
            msg(' Robot Stopping',type='print')
            break;
        
        # If nothing stopped it so far ... call the robot on the current row
        msg('Calling robot...',type='print')
        run = callRobot_v2(driver, row)


# In[28]:


# utils
   
    
def stopMainRobot():
    shared['vars']['stop'] = True
def startMainRobot(restarted=False):
    shared['vars']['stop'] = False
    if(restarted==False):
        try:
            shared['vars']['lastRow']['ID'] = id_entry.get()
        except: 
            shared['vars']['lastRow']['ID'] = getLastIdFromLogsFile()

    bot_thread = threading.Thread(target = lambda: startRobot(df=df0, maxID=shared['vars']['lastRow']['ID'], minID=1, driver='', namespace='lastRow'))
    bot_thread.daemon = False
    bot_thread.start()
    return bot_thread
def restartRobot():
    stopMainRobot()
    time.sleep(10)
    startMainRobot(restarted=True)

def autoRestartRobotNoGUI():
    restartRobot()
    print('Starting without Tkinter GUI...')
    try: window.after(1 * 60 * 60 * 1000, autoRestartRobot)
    except: pass;

def loginBrowser():
    shared['vars']['stop'] = False
    driver = openBrowser()
    driver.get('https://www.estantevirtual.com.br/acervo')
    time.sleep(120)
def setAndRestart():
    try:
        shared['vars']['lastRow']['ID'] = id_entry.get()
    except: 
        shared['vars']['lastRow']['ID'] = getLastIdFromLogsFile()
    autoRestartRobot()


def openBrowserForLogin():
    browser_thread = threading.Thread(target=loginBrowser, daemon=True)
    browser_thread.start() 
def translateLabel(label):
    if(label=='t1'): return 'Bot Main Action'
    if(label=='t2'): return 'Busca na EV'
    if(label=='t3'): return 'Última Edição na EV'
    if(label=='imgpath'): return 'Última Capa Adicionada'
    if(False):
        return 'abc'
    else:
        return label


# GUI
def startTk():
    print('Starting Tkinter GUI...')
    def autoRestartRobot():
        if('Active' in button3["text"]):
            return;
        button3["bg"] = "#379b37"
        button3["text"] = button3["text"] + ' (Active)'
        restartRobot()
        window.after(1 * 60 * 60 * 1000, autoRestartRobot)

    # Create the main window
    window = tk.Tk()
    window.columnconfigure(3, weight=1)
    window.columnconfigure(3, weight=3)

    
    fgcolor = "#1976d2"
    
    # Set the window size and title
    window.geometry("600x700")
    window.title("Selenium Bot Results")

    # stop robot button
    button1 = tk.Button(window, text="Stop Robot", command=stopMainRobot, bg="#A33", fg='white')
    button1.pack(pady=(1,2))

    #starting ID
    label1 = tk.StringVar(window, "Id para começar (Ordem decrescente): ")    
    label1 = tk.Label(window, textvariable=label1, fg=fgcolor)
    label1.pack(pady=(1,2))

    id_entry = tk.Entry(window, width = 30)
    fromTracaId = shared['vars']['lastRow']['ID']
    if not type(fromTracaId): fromTracaId = 0
    id_entry.insert(0,fromTracaId)
    id_entry.pack(pady=(1,2))

    # ações
    label2 = tk.StringVar(window, "Ações ")    
    label2 = tk.Label(window, textvariable=label2,fg=fgcolor)
    label2.pack(pady=(1,2))

    button2 = tk.Button(window, text="Start Robot", command=startMainRobot)
    button2.pack(pady=(1,2))

    # auto restart robot button
    button3 = tk.Button(window, text="Start + Auto ReStart Robot", command=setAndRestart)
    button3.pack(pady=(1,2))

    # auto restart robot button
    button4 = tk.Button(window, text="Open Browser for login (2min)", command=openBrowserForLogin)
    button4.pack(pady=(1,2))

    # logs
    label3 = tk.StringVar(window, "Logs ")    
    label3 = tk.Label(window, textvariable=label3,fg=fgcolor)
    label3.pack(pady=(1,2))

    
    # reset text vars to change type
    # for key in shared['texts']:
    #     value = str(shared['texts'][key])
    #     shared['texts'][key] = tk.StringVar(window,value)
    
    tklabels = {}
    labels = {}
    for key in shared['texts']:
        labels[key] = tk.StringVar(window, translateLabel(key))
        labels[key] = tk.Label(window, textvariable=labels[key],fg=fgcolor)
        labels[key].pack(pady=(1,2))
        
        # tklabels[key] = tk.Label(window, textvariable=shared['texts'][key])
        tklabels[key] = tk.Label(window, text=shared['texts'][key])
        tklabels[key].pack(pady=(1,2))

    
    def update_labels():
        try:
            # Update the text of each label based on the shared['texts'] dictionary
            for key, text in shared['texts'].items():
                if key == 'imgpath' and key!='' and os.path.exists(shared['texts'][key]):
                    # Update the image if the key is 'imgpath'
                    image = Image.open(text)
                    imageRatio = image.width / image.height
                    image = image.resize((200,int(200/imageRatio)))  # Adjust the size as needed
                    photo = ImageTk.PhotoImage(image)
                    tklabels[key].configure(image=photo)
                    tklabels[key].image = photo
                else:
                    # Update the text for other keys
                    tklabels[key].config(text=text)
        
            # Schedule the update_labels function to run again after 1000 milliseconds (1 second)
            window.after(1000, update_labels)
        except:
            return;

    # Create a separate thread for updating labels
    label_thread = threading.Thread(target=update_labels, daemon=True)
    label_thread.start()
    
    window.mainloop()



# In[7]:


# Carrega planilha da EV
df0 = loadExcelFile()


# In[29]:


# 
# 
# RUN THIS TO START
# 
# 
# 

# Arquivo novos
shared['vars'] = {'stop' : False, 'lastRow':{'ID':getLastIdFromLogsFile()}}


if(len(cli_gui)>0):
    startTk()
else:
    autoRestartRobotNoGUI()    










