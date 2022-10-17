import streamlit as st
import pymysql
import numpy as np
import pandas as pd
import datetime
from utils import get_data
from millify import millify
import plotly.express as px

colors = ["#00798c", "#d1495b", '#edae49', '#66a182', '#4a4a4a',
          '#1a508b', '#e3120b', '#c5a880', '#9F5F80', '#6F9EAF',
          '#0278ae','#F39233', '#A7C5EB', '#54E346', '#ABCE74',
        '#d6b0b1', '#58391c', '#cdd0cb', '#ffb396', '#6930c3']

conn_info = { 'host' : "givita-test.cgfnwkqkz7hj.ap-northeast-2.rds.amazonaws.com",
              'port' : 3306,
              'database' : "GIVITA",
              'user' : "sqluser",
              'password' : "sqluser",
              }

user_sql = 'select USER_ID, NICK_NM, USER_EMAIL, USER_NM, BIRTHDAY, GENDER, TALL, \
            WEIGHT, OS, APP_VER_NO, STATUS, SIGNUP_DT from GB_SVC_USER'


st.set_page_config(
    page_title="User Status",
    page_icon="✅",
    layout="wide",
)

st.header('User Status')

st.sidebar.success('Select a page above')

df_users = get_data(conn_info, user_sql)

df_users['SIGNUP_DT'] = pd.to_datetime(df_users['SIGNUP_DT']).dt.date
df_users['SIGNUP_year_month'] = pd.to_datetime(df_users['SIGNUP_DT']).dt.to_period('M')
birthday = df_users['BIRTHDAY'].astype('str')
#df_users['BIRTHDAY'] = birthday.str[:4] +'-' + birthday.str[4:6]+'-' + birthday.str[6:8]
df_users['BIRTHDAY'] = pd.to_datetime(df_users['BIRTHDAY'])
df_users['AGE'] = datetime.datetime.today().year -df_users['BIRTHDAY'].dt.year
df_users['BIRTHDAY'] = df_users['BIRTHDAY'].dt.date
#df_users['AGE'] = df_users['AGE'].astype(int)


st.write(f"last update : ```{df_users['SIGNUP_DT'].max()}```")
st.markdown(' ')

df_user_prevmonth = df_users[df_users['SIGNUP_year_month']<df_users['SIGNUP_year_month'].max()]

df_users_normal = df_users[df_users['STATUS']=='정상']
df_users_normal_prevmonth = df_users_normal[df_users_normal['SIGNUP_year_month']<df_users_normal['SIGNUP_year_month'].max()]

df_user_withdrawal = df_users[df_users['STATUS']=='탈퇴']
df_user_withdrawal_prevmonth = df_user_withdrawal[df_user_withdrawal['SIGNUP_year_month']<df_user_withdrawal['SIGNUP_year_month'].max()]

st.markdown(' ')
placeholder1 = st.empty()
with placeholder1.container():
    st.markdown('**Cumulative Stats**')
    e1, kpi1, kpi2, kpi3, e2 = st.columns([0.2, 1, 1, 1, 0.2])

    kpi1.metric(label = 'Total Users', value= millify(df_users.shape[0], precision=2),
                delta = df_users.shape[0] - df_user_prevmonth.shape[0])

    kpi2.metric(label = 'Total Reg. Users', value= millify(df_users_normal.shape[0], precision=2),
                delta = df_users_normal.shape[0] - df_users_normal_prevmonth.shape[0])

    kpi3.metric(label='Total Withdrawal Users', value=millify(df_user_withdrawal.shape[0], precision=2),
                delta=df_user_withdrawal.shape[0] - df_user_withdrawal_prevmonth.shape[0])

st.markdown('___')
st.markdown(' ')

st.markdown('Monthly Report')
placeholder2 = st.empty()
with placeholder2.container():
    e1, kpi3, kpi4, kpi5, e2 = st.columns([0.2, 1, 1, 1, 0.2])

    reg_month = df_users_normal[df_users_normal['SIGNUP_year_month'] == df_users_normal['SIGNUP_year_month'].max()]
    reg_month_prev = df_users_normal[df_users_normal['SIGNUP_year_month'] == (df_users_normal['SIGNUP_year_month'].max()-1)]

    kpi3.metric(label = 'Registered Users', value= millify(reg_month.shape[0], precision=2),
                delta = millify(reg_month.shape[0] - reg_month_prev.shape[0]))

    reg_users_daily = df_users_normal[df_users_normal['SIGNUP_year_month'] == df_users_normal['SIGNUP_year_month'].max()].groupby('SIGNUP_DT') \
        ['USER_ID'].count().mean()
    reg_users_daily_prev = \
    df_users_normal[df_users_normal['SIGNUP_year_month'] == (df_users_normal['SIGNUP_year_month'].max() - 1)].groupby('SIGNUP_DT') \
        ['USER_ID'].count().mean()

    kpi4.metric(label = 'Average Reg. per Day', value= millify(reg_users_daily, precision=0),
                delta = np.rint(reg_users_daily - reg_users_daily_prev))

    withdrawal_users_daily = df_user_withdrawal[df_user_withdrawal['SIGNUP_year_month'] == \
                            df_user_withdrawal['SIGNUP_year_month'].max()].groupby('SIGNUP_DT') ['USER_ID'].count().mean()

    withdrawal_users_daily_prev = df_user_withdrawal[df_user_withdrawal['SIGNUP_year_month'] == \
                           df_user_withdrawal['SIGNUP_year_month'].max()-1].groupby('SIGNUP_DT')['USER_ID'].count().mean()

    kpi5.metric(label='Average Withdrawal per Day', value=millify(withdrawal_users_daily, precision=2),
                delta=np.rint(withdrawal_users_daily - withdrawal_users_daily_prev))

st.markdown(' ')

fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    df_daily_reg = df_users[df_users['STATUS']=='정상'].groupby('SIGNUP_DT')['USER_ID'].count().reset_index()
    fig = px.line(df_daily_reg, x = 'SIGNUP_DT', y = 'USER_ID')
    fig.update_traces(line = dict(color = colors[0], width = 0.8), opacity= 0.8)
    fig.update_layout(title = {'text' : 'Daily registration', 'y':0.91, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                      xaxis_title = 'registration', yaxis_title = 'date')
    st.plotly_chart(fig)

with fig_col2:
    df_users_normal = df_users[df_users['STATUS']=='정상']
    df_users_normal['AGE'] = df_users_normal['AGE'].astype(int)
    fig = px.histogram(df_users_normal, x = 'AGE', color = 'GENDER', opacity=0.8,
                       color_discrete_map={'M': colors[5], 'F': colors[1]})
    fig.update_layout(legend = dict(x = 0.88, y=0.95), title = {'text' : 'AGE', 'y':0.91, 'x':0.5,
                                                                'xanchor': 'center', 'yanchor': 'top'})
    st.plotly_chart(fig)




expander = st.expander("See all user information")
with expander:
    status_list = pd.unique(df_users["STATUS"]).tolist()
    status_list.append('전체')
    status = st.selectbox("User status", status_list)

    if status == '전체':
        st.success(f'Data size : {df_users.shape}')
        st.dataframe(df_users.drop('SIGNUP_year_month', axis=1))
    else:
        st.success(f"Data size : {df_users[df_users['STATUS'] == status].shape}")
        st.dataframe(df_users[df_users['STATUS'] == status].drop('SIGNUP_year_month', axis=1))