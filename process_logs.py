import pandas as pd
import time
import re
import subprocess


# Matches a sequence of 7 digits
def extract_tracaId(string):
    matches = re.findall(r'\d{7}', string)
    if(len(matches)>0):
        return matches[0] 
    return ''

def intOrNothing(ipt):
    try: return int(ipt)
    except: return ''

def trataID(s):
    return str(s).replace('.0','')


#Planilha mãe da Ev    
pathPĺanilhaEv = 'planilhs/exportada_2023-06-01-11-41-43_365ca294c1fc7dffa601643a9ba7d936.xlsx'

# timestamp pra usar nos nomes
timestr = str(int(time.time()))

# all Logs
pathAllLogs = './logs/catlogs_'+timestr+'.log'
shellResult = subprocess.run(['mkdir ./logs'], shell=True, capture_output=True, text=True)
shellResult = subprocess.run(['cat *.log ./logs/*.log > '+pathAllLogs], shell=True, capture_output=True, text=True)
allLines = open(pathAllLogs, 'r').readlines()

# interpreta os logs que colocou capa
colocandoCapa = [extract_tracaId(x)+'\n' for x in allLines if 'olocando capa' in x]
colocandoCapa = list(dict.fromkeys(colocandoCapa))
colocandoCapa.append('Last update: ' + str(time.ctime()))

# interpreta os logs que deu multiplo resultado
multipleResults = [extract_tracaId(x)+'\n' for x in allLines if 'ultiple results found' in x]
multipleResults = list(dict.fromkeys(multipleResults))

# interpreta os logs nao encontrou imagem
imagem404 = [extract_tracaId(x)+'\n' for x in allLines if 'Imagem não encontrada' in x]
imagem404 = list(dict.fromkeys(imagem404))




# salva os dados num txt
open('multiplos_restultados.txt', 'w').writelines(multipleResults)
open('capa_colocada.txt', 'w').writelines(colocandoCapa)
open('imagens_nao_encontradas.txt', 'w').writelines(imagem404)



# ... isso aqui vai deixar de ser relevante em breve
# Lê a planilha da EV mais antiga pra ver o que já foi colocado/o que não foi
df0 = pd.read_excel(pathPĺanilhaEv)

# Read the IDs from the text file
with open('capa_colocada.txt', 'r') as file:
    ids = file.read().splitlines()
df = df0.copy()


# Extrai os ids 
ids = [id_ for id_ in ids if id_!='']
ids = list(map(intOrNothing, ids))
df['ID'] = df['ID'].apply(trataID)
df = df[df['ID']!= 'nan']
df['ID'] = df['ID'].apply(lambda x: int(x))

# Filter the DataFrame based on the IDs
df_filtered_not_contains = df[~df['ID'].isin(ids)]
df_filtered_contains = df[df['ID'].isin(ids)]

# Save the filtered DataFrame to a new Excel file
df_filtered_not_contains.to_excel('not_processed_'+str(int(time.time()))+'.xlsx', index=False)
df_filtered_contains.to_excel('already_processed'+str(int(time.time()))+'.xlsx', index=False)


# limpa a pasta
result = subprocess.run(['mv *.log ./logs'], shell=True, capture_output=True, text=True)
result = subprocess.run(['mv '+pathAllLogs+' ./logs'], shell=True, capture_output=True, text=True)


