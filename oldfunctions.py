# old stuff

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



# get traca image url
def getTracaImage(id):
    return 'http://192.168.200.201/rapiscan/data/'+ str(id) + '.jpg'
    # 'https://www.traca.com.br/capas/' + str(id)[0:4] + '/' + str(id) + '.jpg'

# download from traca
def tracaDownloadImgById(id):
    id = str(int(id)).replace('.0','')
    image_url = getTracaImage(str(id))
    response = requests.get(image_url)    
    filepath = getImageFilePath(str(id))
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print("Image downloaded successfully:"+(' '*20), filepath, end="\r")
    else:
        print("Failed to download the image:                " + image_url)
        print(response)
           



# save cookies
def saveCookies(filepath="cookies.json"):
    cookies = driver.get_cookies()
    with open(filepath, "w") as file:
        json.dump(cookies, file)

#lista imagens do path
def listaImagens(path = './imgs'):
    return [f for f in os.listdir('./imgs') if f.endswith(".jpg")] 

# Download Images for Ids in the excel file
def downloadImgs(df, startingindex=1, limitIndex=1000):
    for index, row in df.iterrows():
        idTraca = row['ID']
        if(startingindex>=index and index<limitIndex and str(idTraca) != 'nan'):
            tracaDownloadImgById(idTraca);





# handler antigo


# le os dados e coloca a capa no livro
def colocarCapa(driver, opts = {}):       
    trocouCapa = False

    # pega ID
    tracaId = ''
    if(not 'tracaId' in opts.keys()):
        print('ID traca não passado, tentando pegar da página..')
        tracaId = idFromDescription(driver)
    else: 
        return 'False'

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
                print("Image file does not exist              ", end='\r')
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



# v1
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
        msg('Livro não encontrado na EV, ID: '+str(idTraca),type='busca404')
        return False;
    msg('Livro encontrado na EV, ID: ' + str(idTraca),type="busca")

    trocouCapa = colocarCapa(driver,{'estante' : estanteNome, 'tracaId':idTraca, 'row':row})
    if trocouCapa: 
        clickSalvar(driver)
    

# v1
# bot call
def robotCall(index,row):
        if(row['ID'] == 'nan'): 
            print('linha sem ID: ', index)
            return ;
        idTraca = int(str(row['ID']).replace('.0',''))
        isbn = row['ISBN/ISSN']
        pathimg = getImageFilePath(str(idTraca))
        if pathimg:
            estanteNome = row['Estante*']
            # print('livro...' + str(index), idTraca, estanteNome)
            if(estanteNome and os.path.exists(pathimg)):                
                # print('certinho?')
                return runRobotOnId(int(idTraca),estanteNome, row)
        else:
            return ;

  


