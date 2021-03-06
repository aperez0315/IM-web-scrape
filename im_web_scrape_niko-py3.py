# import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import csv
import argparse

#MANUALLY edit these variables before running
##url is the results page, limited by males, age 30-34, go to page 2 and then copy the link, and replace the p=2 with p={page_nr}
url = "http://www.ironman.com/triathlon/events/americas/ironman/wisconsin/results.aspx?p={page_nr}&race=wisconsin&rd=20170910&agegroup=30-34&sex=M&y=2017&ps=20#axzz5G53hv48M"
##max_pg_nr is the maximum number of pages in the results
max_pg_nr = 14
race_nm = "wisconsin"



def get_table(url):
    page = urlopen(url)
    soup = BeautifulSoup(page, 'lxml')          #parse html
    table = soup.find_all('table')[0]           #Grab the first table
    return table

def set_columns(table):

    n_columns = 0
    n_rows=0
    column_names = []

    # Find the number of rows and columns
    for row in table.find_all('tr'):
        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows+=1
            if n_columns == 0:
                # Set the number of columns for our table
                n_columns = len(td_tags)

        # Handle column names if we find them
        th_tags = row.find_all('th')
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())

    # Error checking for Column Names
    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("The column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0,n_columns)
    df = pd.DataFrame(columns=columns, index= range(0,n_rows))

    return df,columns

def get_row_count(table):
    n_rows=0
    # Find the number of rows and columns
    for row in table.find_all('tr'):
        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows+=1
    return n_rows

def get_results(df,table):
    row_marker = 0
    for row in table.find_all('tr'):
        #print(row)
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1
    return df

def merge_df(df1, df2):
    df_new = pd.concat([df1, df2], ignore_index=True)
    return df_new



if __name__ == '__main__':


    file_nm = "results/{}.csv".format(race_nm)
    #set initial table to get columns
    web_page = url.format(page_nr="1")
    table = get_table(web_page)
    #set initial columns names
    im_orig_df,col_names = set_columns(table)

    #rowcount = get_row_count(table)
    im_orig_df = get_results(im_orig_df,table)


    for i in range(2,max_pg_nr):
        page_nr = i
        web_page = url.format(page_nr=page_nr)       #get the webpage url with page number
        #print(web_page)                                     #print page for debug
        table = get_table(web_page)                         #get the first table on the webpage
        rowcount = get_row_count(table)
        #(re)initialize dataframe
        im_results_df = pd.DataFrame(index= range(0,rowcount), columns=col_names)
        im_results_df = get_results(im_results_df,table)

        im_orig_df = merge_df(im_results_df,im_orig_df)


    #print(im_orig_df)
    #df = im_orig_df.sort_values("Div Rank")
    #df['Race Name'] = race_nm
    #df.to_csv(file_nm)
    race_results = im_orig_df.sort_values(by=['Finish'],ascending = True)
    sorted_race_results = pd.DataFrame(race_results)
    sorted_race_results.to_csv('results.csv', index = False, header = True)
print('csv is created')
