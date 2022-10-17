import numpy as np
import streamlit as st
import pymysql
import pandas as pd

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

daily_step_sql = 'select USER_ID, MSRE_DTM, STEP_CNT, MOVE_DIST, CNPT_CALR, MOVE_SPEED from GB_BYDT_STEP'

st.set_page_config(
    page_title="Rothy dashboard",
    page_icon="✅",
    layout="wide",
)

st.header('Daily steps')

df_step = get_data(conn_info, daily_step_sql)
df_step = df_step[df_step['STEP_CNT']>0]
df_step['MSRE_DT'] = pd.to_datetime(df_step['MSRE_DTM']).dt.date
df_step['MSRE_year_month'] = pd.to_datetime(df_step['MSRE_DTM']).dt.to_period('M')

st.write(f"last update : ```{pd.to_datetime(df_step['MSRE_DTM']).dt.date.max()}```")

df_step_prev = df_step[df_step['MSRE_year_month'] < df_step['MSRE_year_month'].max()]

#print(pd.to_datetime(pd.to_datetime(df_step['MSRE_DTM']).dt.date).max())
#print(df_step['MSRE_year_month'].max())
#print(df_step['MSRE_year_month'].max()-1)

#print(df_step.loc[df_step['MSRE_year_month'] ==df_step['MSRE_year_month'].max(), 'USER_ID'].nunique())

st.markdown(' ')
placeholder = st.empty()
with placeholder.container():
    st.markdown('**Cumulative Stats**')
    e1, kpi11, kpi12, kpi13, e2 = st.columns([0.2, 1, 1, 1, 0.2])

    kpi11.metric(label='Total Measured Data', value=millify(df_step.shape[0], precision=2),
                 delta=millify(df_step.shape[0] - df_step_prev.shape[0], precision=2))

    e21, kpi21, kpi22, kpi23, e22 = st.columns([0.2, 1, 1, 1, 0.2])
    act_users_month = df_step.loc[df_step['MSRE_year_month'] ==df_step['MSRE_year_month'].max(), 'USER_ID'].nunique()
    act_users_prev_month = df_step.loc[df_step['MSRE_year_month'] == (df_step['MSRE_year_month'].max()-1),
                                        'USER_ID'].nunique()

    kpi21.metric(label=f'Active Users of the Month', value=millify(act_users_month, precision=2),
                 delta=act_users_month - act_users_prev_month)

    act_users_daily = df_step[df_step['MSRE_year_month'] == df_step['MSRE_year_month'].max()].groupby('MSRE_DTM')\
                         ['USER_ID'].count().mean()
    act_users_daily_prev = df_step[df_step['MSRE_year_month'] == (df_step['MSRE_year_month'].max()-1)].groupby('MSRE_DTM') \
         ['USER_ID'].count().mean()

    kpi22.metric(label=f'Average Daily Active Users', value=millify(act_users_daily, precision=2),
                 delta=np.round(act_users_daily - act_users_daily_prev))

st.markdown(' ')
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    df_daily_step = df_step.groupby('MSRE_DT')['STEP_CNT'].sum().reset_index()
    df_daily_step = df_daily_step[df_daily_step['MSRE_DT']<df_daily_step['MSRE_DT'].max()]
    # print(df_daily_step)
    fig = px.line(df_daily_step, x ='MSRE_DT', y = 'STEP_CNT')
    fig.update_traces(line=dict(color=colors[5], width=0.9), opacity=0.8)
    fig.update_layout(title={'text': 'Daily step counts', 'y': 0.91, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                      xaxis_title='date', yaxis_title='step counts',
                      margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig)

with fig_col2:
    df_active_users = df_step.groupby('MSRE_DT')['USER_ID'].count().reset_index()
    df_active_users = df_active_users[df_active_users['MSRE_DT'] < df_active_users['MSRE_DT'].max()]
    fig = px.line(df_active_users, x='MSRE_DT', y='USER_ID')
    fig.update_traces(line=dict(color=colors[15], width=1.0), opacity=0.8)
    fig.update_layout(title={'text': 'Active users', 'y': 0.91, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                      xaxis_title='date', yaxis_title='Active users',
                      margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig)