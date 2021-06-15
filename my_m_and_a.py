import pandas as pd
import re
import numpy as np
import sqlite3

# FUNCTIONS FOR CLEANING CSV FILES
def clean_gender(df):
    df['gender'] = df['gender'].str.replace('0', 'male')
    df['gender'] = df['gender'].str.replace('1', 'female')
    df['gender'] = df['gender'].str.replace(r'\bF\b','female',regex = True)
    df['gender'] = df['gender'].str.replace(r'\bM\b','male',regex = True)

def clean_firstname(df):
    df['firstname'] = df['firstname'].str.replace(r'\\','',regex = True)
    df['firstname'] = df['firstname'].str.replace(r'"','',regex = True)

def split_name(df):
    df[['firstname','lastname']] = df.firstname.str.split(" ",expand=True)

def clean_lastname(df):
    df['lastname'] = df['lastname'].str.replace(r'\\','',regex = True)
    df['lastname'] = df['lastname'].str.replace(r'"','',regex = True)

def clean_email(df):
    df["email"] = df["email"].fillna('none')

def clean_city(df):
    df["city"] = df["city"].str.replace(r' ','_', regex = True)
    df["city"] = df["city"].str.replace(r'-','_', regex = True)

def add_country(df):
    df['country'] = 'usa'

def clean_prefix(df):
    for column_name in df.columns:
        df[column_name] = df[column_name].str.replace(r'string_','',regex = True)
        df[column_name] = df[column_name].str.replace(r'integer_','',regex = True)
        df[column_name] = df[column_name].str.replace(r'boolean_','',regex = True)
        df[column_name] = df[column_name].str.replace(r'character_','',regex = True)
    
def clean_convert_to_int_age(df):
    df['age'] = df['age'].str.replace(r'[a-zA-Z]+','',regex = True)
    df["age"] = pd.to_numeric(df["age"])

def df_all_lowercase(df):
    for column in df.columns:
        try:
            df[column]=df[column].str.lower()
        except:
            continue

# APPEND 3 files
def append_csv_files(file1, file2, file3):

    #creating dataframe with correct colums names
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2, sep=';', names = ["age","city","gender","firstname","email"])
    df3 = pd.read_csv(file3, sep='\t', skiprows=[0], names = ["gender","firstname","email","age","city","country"])

    #small letter for columns name
    df1 = df1.rename(str.lower,axis='columns')

    #cleaning first file
    df1['created_at'] = 'None'
    df1['referral'] = 'None'
    del df1['username']
    clean_gender(df1)
    clean_firstname(df1)
    clean_lastname(df1)
    clean_city(df1)
    add_country(df1)
    df_all_lowercase(df1)

    #cleaning second file
    df2['created_at'] = 'None'
    df2['referral'] = 'None'
    clean_gender(df2)
    split_name(df2)
    clean_firstname(df2)
    clean_lastname(df2)
    clean_email(df2)
    clean_city(df2)
    clean_convert_to_int_age(df2)
    add_country(df2)
    df_all_lowercase(df2)
    df2 = df2[["gender", "firstname", "lastname", "email", "age", "city", "country", "created_at", "referral"]]

    #cleaning third file
    clean_prefix(df3)
    df3['created_at'] = 'None'
    df3['referral'] = 'None'
    clean_gender(df3)
    split_name(df3)
    clean_firstname(df3)
    clean_lastname(df3)
    clean_email(df3)
    clean_city(df3)
    clean_convert_to_int_age(df3)
    add_country(df3)
    df_all_lowercase(df3)
    df3 = df3[["gender", "firstname", "lastname", "email", "age", "city", "country", "created_at", "referral"]]

    # append 3 csv files
    df1 = df1.append(df2, ignore_index = True)
    df1 = df1.append(df3, ignore_index = True)

    return df1

def csv_to_db(df,db,table):
    column_list = list(df.columns)
    connection = sqlite3.connect(db) #connection to database
    cursor = connection.cursor() #cursor in database
    cursor.execute('DROP TABLE IF EXISTS '+table)
    query_1 = "CREATE TABLE " + table + "({0});" #creating table
    query_1 = query_1.format(','.join(column_list)) #formatting query in the style like (col1,col2,col3)
    cursor.execute(query_1) #executing query
    query_2 = "INSERT INTO " + table + "({0}) VALUES ({1})" #importing data in the table
    query_2 = query_2.format(','.join(column_list),','.join('?'*len(column_list))) #formatting query in the style like VALUES (?,?,?,?,?,?)
    for index, row in df.iterrows():
        cursor.execute(query_2,row) #execure every lines of data
    connection.commit()
    connection.close()

def db_to_sql(db_file,sql_file):
    con = sqlite3.connect(db_file)
    with open(sql_file, 'w') as f:
        for line in con.iterdump():
            f.write('%s\n' % line)
    con.close()

def m_and_a(file1,file2,file3,sql_name):
    df = append_csv_files(file1,file2,file3)   
    db_name = 'empty.db'
    table_name = 'customers'
    csv_to_db(df,db_name,table_name)
    db_to_sql(db_name,sql_name)

# Main part
file1 = 'only_wood_customer_us_1.csv'
file2 = 'only_wood_customer_us_2.csv'
file3 = 'only_wood_customer_us_3.csv'
sql = 'plastic_free_boutique.sql'
m_and_a(file1,file2,file3,sql)