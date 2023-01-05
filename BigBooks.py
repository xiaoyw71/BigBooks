# -*- coding: utf-8 -*-
'''
Created on 2022年4月14日

@author: xiaoyw
'''

import time
import pandas as pd
import pymongo
from gridfs import GridFS
from io import StringIO
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

def navigation_bar():
    #st.set_page_config(layout="wide") #设置屏幕展开方式，宽屏模式布局更好
    st.sidebar.write('文档管理导航栏')
    
        
    add_selectbox = st.sidebar.radio(
        "文档管理",
        ("上传文档", "下载文档", "文档查询")
    )
    
    if add_selectbox == '上传文档':
        fileupload()
    elif add_selectbox == '下载文档':
        filedownload()  #filedownload_tmp() #
    elif add_selectbox == '文档查询':
        querybooks()  
                                         
    return add_selectbox

def fileupload():
    
    classic = st.selectbox('文档类别',['政策法规','文学作品','技术资料'])
    filekeyword = st.text_input('文档关键字','AI')
    filedesc = st.text_input('文档概述','简略描述文档')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        filename = uploaded_file.name
        filetype = uploaded_file.type

        db = connectmongo()
        cn = 'books'
        re = filetoGridFS(db, cn, filename, filetype ,classic, filekeyword, filedesc,bytes_data) 

        st.write(re)
        


# 文件下载
def filedownload():
    st.header("文档查询下载")
    st.markdown('查询数据库中的文档，显示文档列表。')
    db = connectmongo()
    df= queryfile(db,'books.files')

    df,selected = aggrid(df)
    
    if (len(selected)>0):
        filenameList = selected[0]
        inputfilename=filenameList['文件名称']
    else:
        inputfilename='请选择文件名'
            
    file_coll = 'books'    
    with st.form(key='filename'):
        filename=st.text_input('输入文件名',inputfilename)
        submit_button = st.form_submit_button(label='确认')            
    
    if submit_button:
        gridfs_col = GridFS(db, collection=file_coll)
        file_data = gridfs_col.get_version(filename=filename, version=-1).read()
        st.download_button('下载文件', file_data,file_name = filename) 


def querybooks():
    pass

def connectmongo():
    database_url = 'mongodb://localhost:27017/bigbooks'
    client = pymongo.MongoClient(database_url)
    db = client['BigBooks']
    
    return db
# 文件写入MongodbGridFS
def filetoGridFS(db, file_coll, file_name,filetype,classic, filekeyword, filedesc, stringdata):
    filter_condition = {"filename": file_name,"filetype":filetype,"classic":classic,"keyword":filekeyword, "descripte":filedesc}
    print('file_name is ',file_name)
    gridfs_col = GridFS(db, collection=file_coll)
    file_ = "0"
    query = {"filename":"","filetype":""}
    query["filename"] = file_name
    query["filetype"] = filetype
            
    if gridfs_col.exists(query):
        return '已经存在该文件'
    else:
        #print(**filter_condition)
        file_ = gridfs_col.put(data=stringdata, **filter_condition)  # 上传到gridfs
   
    return file_ 

# 数据库，集合名称
def queryfile(db,collectionname):
    collection = db[collectionname]
    query_dict = {}
    col_name = {"_id":0 ,"filename":1 ,"length":1,'classic':1,'keyword':1,'descripte':1,'length':1,'uploadDate':1,'filetype':1} 
    df = pd.DataFrame(list(collection.find(query_dict,col_name)))
    rencolnames = {"filename":'文件名称' ,"length":'文件长度','classic':'文件分类','keyword':'关键字','descripte':'文件描述','uploadDate':'上传日期','filetype':'文件类型'}
    colnames = ['文件名称' ,'文件长度','文件分类','关键字','文件描述','上传日期','文件类型']
    
    df = df.rename(columns=rencolnames)
    df = df[colnames]
    
    return df

def filedownload_tmp():
    db = connectmongo()
    #df= queryfile(db,'books.files')
    #st.dataframe(df)
    file_coll = 'books'
    
    with st.form(key='filename'):
        filename=st.text_input('输入文件名')
        submit_button = st.form_submit_button(label='下载文件')            
    
    if submit_button:
        gridfs_col = GridFS(db, collection=file_coll)
        file_data = gridfs_col.get_version(filename=filename, version=-1).read()
        st.download_button('Download file', file_data,file_name = filename)  # Defaults to 'application/octet-stream'

# 定义单行选择表，选中行的数据，可以按字段/关键字读取出来
def aggrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    selection_mode = 'single' # 定义单选模式，多选为'multiple'
    enable_enterprise_modules = True # 设置企业化模型，可以筛选等
    #gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    #gb.configure_default_column(editable=True) #定义允许编辑
    
    return_mode_value = DataReturnMode.FILTERED  #__members__[return_mode]
    gb.configure_selection(selection_mode, use_checkbox=True) # 定义use_checkbox
    
    gb.configure_side_bar()
    gb.configure_grid_options(domLayout='normal')
    gb.configure_pagination(paginationAutoPageSize=True)
    gridOptions = gb.build()
    
    update_mode_value = GridUpdateMode.MODEL_CHANGED
    
    grid_response = AgGrid(
                        df, 
                        gridOptions=gridOptions,
                        data_return_mode=return_mode_value,
                        update_mode=update_mode_value,
                        #allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
                        #enable_enterprise_modules=enable_enterprise_modules,
                        )
    #                    data_return_mode=return_mode_value)
    
    df = grid_response['data']
    selected = grid_response['selected_rows']
    
    return df, selected  


def main():
    navigation_bar()

if __name__ == '__main__':
    main()
    pass