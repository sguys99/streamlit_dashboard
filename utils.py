import streamlit as st
import pymysql
import pandas as pd


@st.experimental_memo # get_data를 한번만 실행시킨다. 앱을 rerun하더라도 데이터가 기억되어서 재사용함
def get_data(conn_info, sql) -> pd.DataFrame:
    db = pymysql.connect(host= conn_info['host'], port=conn_info['port'], user= conn_info['user'],
                         passwd=conn_info['password'], db=conn_info['database'],
                         charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    df = pd.DataFrame(result)

    return df