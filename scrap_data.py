import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from sqlalchemy import create_engine

def request_page(page_num: int) -> str:
    return requests.get(f"https://www.jeniferimoveis.com.br/imovel/?finalidade=venda&tipo=&vmi=1&bairro=0&sui=&ban=&gar=&dor=&pag={page_num}").text
   

i = 1
imovel_count = 1
imoveis_t = [0,]

cols_df = [ 'Estado',
            'Cidade', 
            'Bairro', 
            'Área', 
            'Terreno',
            'Dormitório',
            'Banheiro',
            'Vaga',
            'Útil',
            'Suíte',
            'Preço'
            ]
df = pd.DataFrame(columns=cols_df)

while len(imoveis_t) > 0:

    soup = bs(request_page(i), features="html.parser")
    imoveis = soup.find_all('div', {'class': 'imovelcard'})

    imoveis_t = [imovel for imovel in imoveis if not imovel.find('div', {'class': 'lista_imoveis_paginacao'})]

    for imovel in imoveis_t:
        insert_dict = dict()
        try:
            loc = imovel.find('h2', {"class": "imovelcard__info__local"}).text
        except:
            loc = None
        try:
            price = imovel.find('p', {"class": "imovelcard__valor__valor"}).text.split(' ')[-1]
        except:
            price = None

        try:
            feature = imovel.find_all('div', {"class": "imovelcard__info__feature"})
        except:
            feature = None

        for feat in feature:
            valor_feat = feat.find('b').text.split(' ')[0]
            nome_feat = feat.text.split(' ')[-1]
            if nome_feat[-1] == 's':
                nome_feat = nome_feat[0:-1]

            insert_dict[nome_feat] = valor_feat

        

        bairro = loc.split(',')[0]
        cidade = loc.split(',')[1].split('/')[0]
        estado = loc.split(',')[1].split('/')[1]

        insert_dict.update({'Preço': price, 'Bairro': bairro, 'Cidade': cidade, 'Estado': estado})
        df = df.append(insert_dict, ignore_index=True)

        # print(f'Imóvel {imovel_count}')
        # print(insert_dict)

        # imovel_count += 1

        

    i+=1
print('FIM DOS IMÓVEIS')
print('OLHADA NO DATASET:')
print(df.head())

assert len(df.columns) == len(cols_df), f'Your df has {len(df.columns)}, when it should have {len(cols_df)}'

df.to_csv('jennifer_imoveis.csv', sep=';', index=False)

engine = create_engine('postgresql://root:root@localhost:5432/imoveis_db')

df.to_sql(schema = 'public', name = 'imoveis_jennifer', con = engine,  if_exists = 'fail')

