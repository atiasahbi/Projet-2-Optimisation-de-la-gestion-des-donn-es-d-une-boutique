#!/usr/bin/env python
# coding: utf-8

# In[17]:


import numpy as np #importation classique du numpy sous l'alias np
import pandas as pd #importation classique du pandas sous l'alias pd
import  matplotlib.pyplot as plt #importation classique du module matplotlib.pyplot sous l'alias plt
import seaborn as sns


# In[6]:


cd "C:\Users\narje\Desktop\données_P5"


# # 1) Importation des exports

# In[8]:


erp = pd.read_csv('erp.csv',sep = ";",dtype={'price':float}) #importer le fichier erp
erp.head()
erp.describe(include = 'all')


# In[9]:


liaison = pd.read_csv('liaison.csv',sep = ';') #importer le fichier liaison
liaison.head()
print(f'sku:{liaison.id_web.nunique()}')
print(f'sku:{liaison.id_web.count()}')
liaison.describe(include = 'all')


# In[10]:


web = pd.read_csv('web.csv',sep = ";",encoding = 'ANSI') #importer le fichier web
print(f'sku_unique:{web.sku.nunique()}') #nombre des valeurs uniques pour le variable sku
print(f'sku_total:{web.sku.count()}') #nombre des valeurs non null du variable sku
web.describe(include = 'all')
web.shape
web.describe(include = 'all')
web.head()


# # 2) Nettoyage des dataframes et vérification de l'unicité des clés

# In[11]:


#nettoyage du dataframe erp
erp.dropna(axis = 1 , how = 'all' , inplace = True)
erp.dropna(axis = 0 ,how = 'all' , inplace = True)
erp.dropna(subset = ['product_id'] , axis = 0 ,how = 'any' , inplace = True)
print(erp.drop_duplicates(['product_id']).shape)
erp = erp.drop_duplicates(['product_id'])
erp.describe (include = 'all')
print(f'product_id:{erp.product_id.nunique()}') #vérification de l'unicité du clé de la table erp
erp.info()


# In[12]:


#nettoyage du dataframe liaison
liaison.dropna(axis = 1 , how = 'all' , inplace = True) # supprimer les colonnes entièrement vide
liaison.dropna(axis = 0 ,how = 'all' , inplace = True) # supprimer les lignes entièrement vide
print(f'product_id:{liaison.product_id.nunique()}')
print(f'id_web:{liaison.id_web.nunique()}')
print(liaison.drop_duplicates().shape) #vérification de l'unicité du clé de la table liaison
liaison = liaison.drop_duplicates(['product_id'])
liaison.info()


# In[358]:


#vérifier l'unicité du clé sku pour la table web
print(f'id_web:{web.sku.nunique()}')
print(web.shape)
web [ web ['sku'] == 'bon-cadeau-25-euros'] #pour un meme sku on a 2 différent post_type (product et attachement)


# In[13]:


web_notnull = web [ web ['sku'].notnull()] #recherche des SKU non null
web_notnull.shape


# In[360]:


web_notnull.drop_duplicates(['sku','post_type']).shape # prouver qu'il y'a aucun doublon pour la clé (sku,post_type)


# In[361]:


recherche_null = web [ web ['sku'].isnull() ] #rechercher les valeurs du sku nulls
print(recherche_null.shape)                   #on a 85 valeurs nulls de sku


# In[363]:


#vérifier si on doit éliminer les valeurs nulls de sku
observation = recherche_null [recherche_null ['post_name'].notnull() ]
observation #pour des valeurs nulls de sku on a quand meme des produits(post_name non null)


# In[14]:


#nettoyage dataframe web
web.dropna(axis = 1 , how = 'all' , inplace = True) # supprimer les colonnes entièrement vide
web.dropna(axis = 0 ,how = 'all' , inplace = True) # supprimer les lignes entièrement vide
web = web.drop_duplicates(['sku'])
web.info()


# # 3) La jointure des dataframes erp et web

# In[15]:


#jointure erp et liaison
erp_liaison = pd.merge(erp, liaison, how = 'inner', on = 'product_id') #jointure entre la table erp et la table liaison 
erp_liaison.head()
erp_liaison.info()


# In[16]:


#jointure web et erp_liaison
DF = pd.merge(web, erp_liaison  , how = 'outer', left_on = 'sku', right_on = 'id_web' )
DF.shape
DF.info()
DF.loc[:,['sku','product_id','onsale_web','price','id_web']]


# # 4) Le CA par produit et total

# In[17]:


DF['product_id']
A = DF.loc[:,['product_id','total_sales','price']] #dataframe ne contient que product_id,total_sales et price
A["CA"] = DF['total_sales'] * DF['price'] #le CA pour un produit est égale à nombre de vente multiplié par le prix
CA_total = A['CA'].sum() #le CA total est la somme 
DF['price'].astype(float) #convertir 'price' en un float
DF.shape
#il faut avoir 714 lignes
print("le chiffre d'affaire par produit:\n",A.head(20)) #affichage de CA total
print("le chiffre d'affaire totale:",CA_total,"euros") #affichage de CA total
A


# # 5) Analyses sur la variable prix (valeurs atypiques)

# In[19]:


A["zscore"] = ((A.price - A.price.mean()) / A.price.std()).abs() #calcul du Z score
valeurs_aberrantes = A [ A ["zscore"] >2 ] #le nombre des outliers du prix
valeurs_aberrantes.index = np.arange(1, len(valeurs_aberrantes) + 1) #commencer l'indexation de 1 au lieu de 0
valeurs_aberrantes.price.hist(bins = 30) #graphique qui présente les valeurs abberantes avec 30 bars
plt.title('Distribution des outliers du prix') #titre de la figure
plt.xlabel("prix produit ") #axe des abscisses
plt.ylabel('nombre') #axe des ordonnées
plt.savefig('variation du prix en fonction du zscore.png' , dpi = 200,bbox_inches = 'tight') #enregistrement de figure dans le répertoire de travail et augmentation de la résolution
print("Le nombre des valeurs abérrantes est de",valeurs_aberrantes.shape)
valeurs_aberrantes


# In[391]:


#on se crée 2 dataframe pour séparer les couleurs
valeurs_normales = A[(A['zscore'] < 2 )]
valeurs_atypique = A[(A['zscore'] > 2 )]
#graphique
plt.scatter (valeurs_normales['price'].index , valeurs_normales['price'].values)
plt.scatter (valeurs_atypique['price'].index , valeurs_atypique['price'].values , c = 'red')
plt.title('Les valeurs atypique du prix en rouge') #titre de la figure
plt.xlabel("indice") #axe des abscisses
plt.ylabel('prix') #axe des ordonnées
plt.savefig('Les valeurs atypiques.png' , dpi = 200,bbox_inches = 'tight') #enregistrement de figure dans le répertoire de travail et augmentation de la résolution


# In[389]:


A.boxplot(column = ['price'] , grid = False)
plt.title('Boîte à moustache pour la variable prix') #titre de la figure
plt.savefig('Boîte à moustache pour la variable prix.png' , dpi = 200,bbox_inches = 'tight') #enregistrement de figure dans le répertoire de travail et augmentation de la résolution

