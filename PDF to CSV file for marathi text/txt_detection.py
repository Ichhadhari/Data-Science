import os
import io
import re
import glob
import shutil
import logging
import tempfile
import pandas as pd
import numpy as np
from tkinter import Tcl
from wand.image import Image
from wand.color import Color
import cv2
import pytesseract

logger = logging.getLogger()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

parents_words=['पतीचे','वडीलांचे','इतरांचे','आईचे']
header_lst=['घर','वय','वडीलांचे','पतीचे','नाव','इतरांचे','आईचे']
dataframe_list=[]

#Create input and output folders if they dont exist
def create_folders(output_path):
    '''if not(os.path.isdir(os.getcwd()+"/"+ input_path)):
        os.mkdir(os.getcwd()+"/"+ input_path)'''
    if not(os.path.isdir(os.getcwd()+"/"+output_path)):
        os.mkdir(os.getcwd()+"/"+ output_path)

#Remove image files after the process is completed
def remove_files(extension):
    files = os.listdir(document_dir)
    for item in files:
        if item.endswith(extension):
            os.remove(os.path.join(document_dir, item))

def print_logging(msg):
    print(msg)
    logger.info(msg)

#Retrieve list of pdf files from given directory
def get_pdf_file_list():
    pdf_list=[]
    for file in glob.glob(document_dir + "*.pdf"):
        file=os.path.split(file)[1]
        pdf_list.append(file)
    return pdf_list

#Convert Pdfs to image files
def convert_pdf_to_images(filename,folder_path):
    print_logging("\n Converting pdf to images.... \n")
    if filename.endswith(".pdf"):
        print(filename)
        with Image(filename=folder_path + "/" + filename,resolution=300) as img:
            img.background_color = Color("white")
            img.alpha_channel = False
            output_image = filename.replace('.pdf','.png')
            print(output_image)
            img.save(filename=folder_path + "/" + output_image)
            print(folder_path)
    print_logging("Pdf conversion completed!!! \n ")

#Retrieve list of png files from given directory
def get_img_file_list(folder_path):
    png_file_list=[]
    for file in glob.glob(folder_path +"/"+ "*.png"):
        file=os.path.split(file)[1]
        png_file_list.append(file)
    return png_file_list



#Get the list of parents names
def get_ParentsName(text):
    Parents_Name_lst=[]
    Parents_Name_lst = re.findall("Parents.*$", text, re.MULTILINE)
    Parents_Name_lst = [sub.replace("Parents", "").replace(":", "").lstrip() for sub in Parents_Name_lst]
    for x in Parents_Name_lst:
        print(x)
    return Parents_Name_lst

def get_Name_list(text):
    Name_lst=[]
    Name_lst = re.findall("Name.*$", text, re.MULTILINE)
    Name_lst = [sub.replace("Name", "").replace(":", "").lstrip() for sub in Name_lst]
    for x in Name_lst:
        print(x)
    return Name_lst
def get_gender_lst(text):
    gender_lst = []
    gender_lst = re.findall("gender.*$", text, re.MULTILINE)
    gender_lst = [sub.replace("gender", "").replace(":", "").lstrip() for sub in gender_lst]
    for x in gender_lst:
        print(x)
    return gender_lst
def get_pageHeader(text,M):
    pageHeader=[]
    pageHeaders=[]
    pageHeader = re.findall("PageHeader.*$", text, re.MULTILINE)
    pageHeader = [sub.replace("PageHeader", "").replace(":", "").lstrip() for sub in pageHeader]
    pageHeaders = pageHeader * M
    return pageHeaders
def get_file_address(text, M):
    file_address = re.findall("File_Address.*$", text, re.MULTILINE)
    file_address = [sub.replace("File_Address", "").replace(":", "").lstrip() for sub in file_address]
    files_address = file_address * M
    return files_address

def get_page_address(text, M):
    page_address = re.findall("Page_Address.*$", text, re.MULTILINE)
    page_address = [sub.replace("Page_Address", "").replace(":", "").lstrip() for sub in page_address]
    pages_address = page_address * M
    return pages_address

def get_number_list(text):
    number_list =[]
    words_pattern = "[A-Z0]{3}\d{7}"
    number_list = re.findall(words_pattern, text, flags=re.IGNORECASE)
    return number_list

def get_age_list(text):
    age_list=[]
    pattern = "[A-Z]{1}[a-z]{2}\s\d{2}.\d{2}.\d{4}"
    age_list = re.findall("Age.*$", text, re.MULTILINE)
    age_list.pop(-1)
    age_list = [sub.replace("gender", "").replace(":", "").lstrip() for sub in age_list]
    for x in age_list:
        print(x)
    return age_list



def detect_text(path):
    #votedict,id_dict={},{}
    no_lst=[]
    parent_lst = []
    print("I am here...")
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)#cv2.threshold(path, 128, 255, cv2.THRESH_BINARY_INV)[1]
    # convert img to grey
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # get threshold image
    thr = cv2.threshold(img_grey, 128, 255, cv2.THRESH_BINARY_INV)[1]
    # Find contours w.r.t. the OpenCV version
    cnts = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    text = pytesseract.image_to_string(path, config='--psm 6', lang='Devanagari')
    #text = text.replace('\n', '').replace('\f', '')
    text = text.replace('|', '').replace('Avallable', '').replace('Avalable', '').replace('Available', '').replace('Photo', '').replace('hos', '').replace('is', '').replace('Avallablo', '').replace('कTOK', 'TOK').replace('फTOKo', 'TOK9').replace('फTOKI', 'TOK9').replace('___s°0', '')
    text = text.replace('विधानसभा मतदारसंघाचा क्रमाक व नाव', 'PageHeader').replace('यादी भाग क्रमाक', '\nPage_Address').replace('विभागाचा क्रमांक व नाव', '\nFile_Address').replace('पतीचे नाव', '\n Parents').replace('वडीलांचे नाव', '\n Parents').replace('आईचे नाव', '\n Parents').replace('इतरांचे नाव', '\n Parents').replace('नाव', '\n Name').replace('वय', '\n Age').replace('घर क्रमांक', '\n Address').replace('आईचे नाव', '\n Parents Name').replace('लिंग', '\n gender').replace('\n\n', '\n')
    #re.split(text, maxsplit=0)
    print('text: {}'.format(text))
    no_lst = get_number_list(text)
    print(no_lst)
    Name_lst = get_Name_list(text)
    M=len(Name_lst)
    Page_header = get_pageHeader(text, M)
    file_address = get_file_address(text, M)
    page_address=get_page_address(text,M)
    parent_lst = get_ParentsName(text)
    gender_lst = get_gender_lst(text)
    age_list = get_age_list(text)


    return text , no_lst ,Name_lst, parent_lst, gender_lst, Page_header, file_address, page_address, age_list

def get_combine_data(file_list,folder_path):
    print(file_list)
    print(folder_path)
    text = []
    no_lst =[]
    data = {}
    Pages_header=[]
    Page_header=[]
    pages_address=[]
    Files_Address=[]
    page_address = []
    File_Address = []
    number_lst =[]
    Name_lst=[]
    Names_lst=[]
    parent_lst=[]
    parents =[]
    gender_lsts=[]
    age_list =[]
    ages_list=[]
    raw_data=""
    combined_df = pd.DataFrame()
    page = 0
    for filename in (Tcl().call('lsort', '-dict', file_list)):
        page= page + 1
        print_logging("Processing file {}.".format(filename))
        if page > 2:
            text , no_lst ,Name_lst, parent_lst, gender_lst, Page_headers, File_Address, page_address, age_list = detect_text(folder_path + "/" + filename)

            raw_data = raw_data + text
            Pages_header = Pages_header + Page_headers
            Files_Address = Files_Address + File_Address
            pages_address = pages_address + page_address
            number_lst = number_lst + no_lst
            Names_lst = Names_lst + Name_lst
            parents = parents + parent_lst
            gender_lsts=gender_lsts+gender_lst
            ages_list= ages_list+age_list
    print(" adding all ")
    print(len(Pages_header))
    print(len(Files_Address))
    print(len(pages_address))
    print(len(Names_lst))
    print(len(parents))
    print(len(gender_lsts))
    print(len(ages_list))
    if (len(Pages_header)==len(Files_Address)==len(pages_address)==len(Names_lst)==len(parents)==len(gender_lsts)==len(number_lst)==len(ages_list)):
        data = {
            'Page_header': Pages_header,
            'File_Address':Files_Address,
            'page_address':pages_address,
            'Voter ID':number_lst,
            'Voter Name': Names_lst,
            'Parents Name': parents,
            'Gender': gender_lsts,
            'Age':ages_list
        }
        final_df = pd.DataFrame(data, columns=['Page_header','File_Address','page_address','Voter ID','Voter Name','Parents Name','Gender','Age'])
    elif (len(Pages_header)==len(Files_Address)==len(pages_address)==len(Names_lst)==len(parents)==len(gender_lsts)==len(ages_list)):
        data = {
            'Page_header': Pages_header,
            'File_Address': Files_Address,
            'page_address': pages_address,
            'Name': Names_lst,
            'Parents Name': parents,
            'Gender': gender_lsts,
            'Age': ages_list
        }
        final_df = pd.DataFrame(data, columns=['Page_header', 'File_Address', 'page_address', 'Name', 'Parents Name',
                                               'Gender', 'Age'])
    return final_df





if __name__ == "__main__":
    path=os.getcwd()+ "/"
    output_path="processed"
    input_path= input('enter folder name \n')
    global document_dir
    document_dir = os.getcwd()+ "/" + input_path + "/"
    create_folders(output_path)
    pdf_file_list=get_pdf_file_list()


    for filename in (Tcl().call('lsort', '-dict', pdf_file_list)):
        print_logging("Processing file {}.".format(filename))
        try:
            tempdir = tempfile.TemporaryDirectory(dir=os.getcwd()+"/")
            shutil.move(document_dir+ filename, tempdir.name + "/")
            #os.remove(os.path.join(document_dir + filename ))
            convert_pdf_to_images(filename,tempdir.name)
            print('1')
            png_file_list=get_img_file_list(tempdir.name)
            print(2)
            final_df =get_combine_data(png_file_list,tempdir.name)
            #Convert the dataframe to csv
            final_df.to_csv (path + output_path + "/" + filename.replace(".pdf",".csv"), index = False, header=True)
            #Remove the image files and move the pdf file
            remove_files(".png")
            #if not(os.path.exists(path + output_path + "/" + filename)):
            shutil.move(tempdir.name + "/" + filename, path + output_path + "/")
            tempdir.cleanup()
            print_logging("Successfully completed.")
        except Exception as e:
            logger.error(e, exc_info=True)