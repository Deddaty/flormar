import requests
from bs4 import BeautifulSoup
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from data import product
from decimal import Decimal
import simplejson
#from retry import retry
from requests.exceptions import ConnectionError, Timeout
import math


def copy_rename(img,name):
    response = requests.get(img, stream=True)
    response.raw.decode_content = True
    image = Image.open(response.raw)
    image.save("img/{}.jpeg".format(name))
    
    
def getName(page):
    nom = page.find_all("h1")
    nom = nom[0].getText().strip()
    return nom

def getPrice(page):
    prix = page.select("#ctl00_u18_ascUrunDetay_dtUrunDetay_ctl00_lblSatisFiyat")
    prix = prix[0].getText().replace("TL","").strip()
    prix = prix.replace('.','')
    prix = prix.replace(',','.')
    prix = Decimal(prix)
    prix = math.ceil(prix)
    return prix

def getMarque(page):
    marque = page.select("#detail-container > div > span > a")
    marque = marque[0].getText().strip()
    return marque

def getPromo(page):
    prix_promo = page.find_all("span","ems-prd-price-first")
    prix_promo = prix_promo[0].getText().replace("TL","").strip()
    prix_promo = prix_promo.replace('.','')
    prix_promo = prix_promo.replace(',','.')
    if prix_promo == '':
        return 0
    else :
        prix_promo = Decimal(prix_promo)
        prix_promo = math.ceil(prix_promo)
        return prix_promo


def getRef(page):
    ref  = page.find_all("div","ems-prd-code ems-none")
    ref = ref[0].getText().strip()
    a,b,c = ref.split("-")
    ref = a+"-"+b
    return ref

def getImg1(page):
    images  = page.find_all("a","cloud-zoom")
    images = images[0].find_all("img")
    img1 = images[0]['src']
    return img1


def getImg2(page):
    images  = page.find_all("a","cloud-zoom")
    if len(images) > 1:
        images = images[1].find_all("img")
        img2 = images[0]['src']
        return img2
    else :
        return ''

def getDesc(page):
    desc = page.find_all("div","ems-prd-mini-description")
    desc = desc[0].getText().strip()
    return desc
def load_data(url):
    req  = requests.get(url,timeout=20)
    page = BeautifulSoup(req.content,"html.parser")
    
    nom = getName(page)
    prix =getPrice(page)
    prix_promo = getPromo(page)
    if prix_promo == 0:
        prix_promo = prix
    #marque = getMarque(page)
    ref = getRef(page)
    img1 = getImg1(page)
    copy_rename(img1,str(ref))
    img2 = getImg2(page)
    if img2 != '':
        copy_rename(img2,str(ref+'_1'))
    desc = getDesc(page)

    return {
        "nom":nom,
        "prix": prix,
        "Prix MRU": simplejson.dumps(Decimal(prix)*10),
        "Promo MRU": simplejson.dumps(Decimal(prix_promo)*10),
        "Prix_de_vente":math.ceil((prix_promo*10)*Decimal(0.5)+prix_promo*10),
        "Marque": 'Flormar',
        "Id_Marque":"",
        'Categorie':"" 	,
        "Id_Categorie":"",
        "Fournisseur": "H&M",	
        "Id_Fournissseur":58,
        "Référence": ref,
        "Image1":img1,
        "Image2":img2,
        "Image":"",
        "Quantite":100, 	
        "Marge":"",	
        "Resume":"",	
        "Description":desc, 	
        "lien":url,
}


def retrive_all(urls):
    prods = []
    for url in urls:
        data = load_data(url)
        prods.append(list(data.values()))
    return prods


def fetch_sheet_data(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json',scope)
    client = gspread.authorize(creds)
    wks = client.open(sheet_name)



def select_sheet(work_sheet,work_sheet_index=0):
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json',scope)
    client = gspread.authorize(creds)
    sh = client.open(work_sheet)
    sh = sh.get_worksheet(work_sheet_index)
    return sh

def insert_into_sheet(data,work_sheet):
    for item in data:
        work_sheet.append_row(list(item))

def getFile(name):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if file1['title'] == name:
            return  file1
    return "introuvable !!"

