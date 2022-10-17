import streamlit as st
import pymysql
import numpy as np
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

bdcmps_sql = 'select USER_ID, MSRE_DTM, WT, TALL, BDFAT_RATE, BDWT_QTY, MUSL_WT, BDFAT_QTY, ' \
             'BASAL_MTBLS_QTY, SKLTN_WT, BMI, SKLTN_WT_RATE, DVIC_TP from GB_BYDT_BDCMPS'

st.set_page_config(
    page_title="Body Composition",
    page_icon="✅",
    layout="wide",
)

st.header('Body Composition')

df_bdcmps = get_data(conn_info, bdcmps_sql)

df_bdcmps['MSRE_DT'] = pd.to_datetime(df_bdcmps['MSRE_DTM']).dt.date
df_bdcmps['MSRE_year_month'] = pd.to_datetime(df_bdcmps['MSRE_DTM']).dt.to_period('M')

st.write(f"last update : ```{pd.to_datetime(df_bdcmps['MSRE_DTM']).dt.date.max()}```")
st.markdown(' ')


df_bdcmps_prev = df_bdcmps[df_bdcmps['MSRE_year_month'] < df_bdcmps['MSRE_year_month'].max()]

df_bdcmps_fix = df_bdcmps[df_bdcmps['DVIC_TP']==990002]
df_bdcmps_fix_prev = df_bdcmps_fix[df_bdcmps_fix['MSRE_year_month'] < df_bdcmps_fix['MSRE_year_month'].max()]

df_bdcmps_watch4 = df_bdcmps[df_bdcmps['DVIC_TP']==990001]
df_bdcmps_watch4_prev = df_bdcmps_watch4[df_bdcmps_watch4['MSRE_year_month'] < df_bdcmps_watch4['MSRE_year_month'].max()]

df_bdcmps_watch = df_bdcmps[df_bdcmps['DVIC_TP']==360003]
df_bdcmps_watch_prev = df_bdcmps_watch[df_bdcmps_watch['MSRE_year_month'] < df_bdcmps_watch['MSRE_year_month'].max()]

df_bdcmps_external = df_bdcmps[df_bdcmps['DVIC_TP']==360002]
df_bdcmps_external_prev = df_bdcmps_external[df_bdcmps_external['MSRE_year_month'] < \
                                             df_bdcmps_external['MSRE_year_month'].max()]

df_bdcmps_mobile = df_bdcmps[df_bdcmps['DVIC_TP']==360001]
df_bdcmps_mobile_prev = df_bdcmps_mobile[df_bdcmps_mobile['MSRE_year_month'] < \
                                             df_bdcmps_mobile['MSRE_year_month'].max()]

df_bdcmps_unknown = df_bdcmps[df_bdcmps['DVIC_TP']==0]
df_bdcmps_unknown_prev = df_bdcmps_unknown[df_bdcmps_unknown['MSRE_year_month'] < \
                                             df_bdcmps_unknown['MSRE_year_month'].max()]

st.markdown(' ')
placeholder1 = st.empty()
with placeholder1.container():
    st.markdown('**Cumulative Stats**')
    e11, e12, kpi11, e13, e14 = st.columns([1, 1, 1, 1, 1])
    kpi11.metric(label='Total Measured Data', value=millify(df_bdcmps.shape[0], precision=2),
                delta=df_bdcmps.shape[0] - df_bdcmps_prev.shape[0])

    kpi21, kpi22, kpi23, kpi24 = st.columns([1, 1, 1, 1])

    kpi21.metric(label=f'Smart Scale (90002)', value=millify(df_bdcmps_fix.shape[0], precision=2),
                delta=df_bdcmps_fix.shape[0] - df_bdcmps_fix_prev.shape[0])

    kpi22.metric(label=f'Galaxy Watch4 (90001)', value=millify(df_bdcmps_watch4.shape[0], precision=2),
                delta=df_bdcmps_watch4.shape[0] - df_bdcmps_watch4_prev.shape[0])

    kpi23.metric(label=f'Galaxy Watch (360003)', value=millify(df_bdcmps_watch.shape[0], precision=2),
                delta=df_bdcmps_watch.shape[0] - df_bdcmps_watch_prev.shape[0])

    kpi24.metric(label='External Device (360002)', value=millify(df_bdcmps_external.shape[0], precision=2),
                delta=df_bdcmps_external.shape[0] - df_bdcmps_external_prev.shape[0])

    e31, kpi31, kpi32, e32 = st.columns([1, 1, 1, 1])
    kpi31.metric(label=f'Samsung Health (360001)', value=millify(df_bdcmps_external.shape[0], precision=2),
                delta=df_bdcmps_external.shape[0] - df_bdcmps_external_prev.shape[0])

    kpi32.metric(label='Samsung Health Device (0)', value=millify(df_bdcmps_external.shape[0], precision=2),
                delta=df_bdcmps_unknown.shape[0] - df_bdcmps_unknown_prev.shape[0])

fig_col11, fig_col12 = st.columns(2)

with fig_col11:
    df_bdcmps_measured = df_bdcmps.groupby('MSRE_DT')['WT'].count().reset_index()
    #df_bdcmps_measured['cumsum'] = df_bdcmps_measured['WT'].cumsum()
    fig = px.line(df_bdcmps_measured, x = 'MSRE_DT', y = 'WT')
    fig.update_traces(line=dict(color=colors[2], width=0.9), opacity=0.8)
    fig.update_layout(title={'text': 'Daily measurement', 'y': 0.91, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                      xaxis_title='count', yaxis_title='date',
                      margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig)

with fig_col12:
    #df_bdcmps_measured_by_dvice = df_bdcmps.groupby(['MSRE_DT', 'DVIC_TP'])['WT'].count().reset_index()
    df_bdcmps_measured_by_device = df_bdcmps['DVIC_TP'].value_counts().reset_index()
    fig = px.pie(df_bdcmps_measured_by_device, values = 'DVIC_TP', names='index')
    fig.update_traces(textposition = 'inside', textinfo = 'percent+label')
    fig.update_layout(title={'text': 'Measurement by Device', 'y': 0.92, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                      showlegend = False,
                      margin=dict(l=10, r=10, t=60, b=50))
    st.plotly_chart(fig)

st.markdown('---')

placeholder2 = st.empty()
with placeholder2.container():
    st.markdown(' ')
    st.markdown('**Monthly Stats**')
    e41, e42, kpi41, e43, e44 = st.columns([1, 1, 1, 1, 1])
    df_bdcmps_month = df_bdcmps[df_bdcmps['MSRE_year_month']==df_bdcmps['MSRE_year_month'].max()]
    df_bdcmps_month_prev = df_bdcmps[df_bdcmps['MSRE_year_month']==(df_bdcmps['MSRE_year_month'].max()-1)]
    kpi41.metric(label='Measured Data', value=millify(df_bdcmps_month.shape[0], precision=2),
                delta=millify(df_bdcmps_month.shape[0] - df_bdcmps_month_prev.shape[0], precision=2))

    kpi51, kpi52, kpi53, kpi54 = st.columns([1, 1, 1, 1])
    df_bdcmps_month_fix = df_bdcmps_month[df_bdcmps_month['DVIC_TP']==990002]
    df_bdcmps_month_prev_fix = df_bdcmps_month_prev[df_bdcmps_month_prev['DVIC_TP']==990002]
    kpi51.metric(label = 'Smart Scale (90002)', value = millify(df_bdcmps_month_fix.shape[0], precision=2),
                 delta = df_bdcmps_month_fix.shape[0] - df_bdcmps_month_prev_fix.shape[0])

    df_bdcmps_month_watch4 = df_bdcmps_month[df_bdcmps_month['DVIC_TP'] == 990001]
    df_bdcmps_month_prev_watch4 = df_bdcmps_month_prev[df_bdcmps_month_prev['DVIC_TP'] == 990001]
    kpi52.metric(label='Galaxy Watch4 (90001)', value=millify(df_bdcmps_month_watch4.shape[0], precision=2),
                 delta=df_bdcmps_month_watch4.shape[0] - df_bdcmps_month_prev_watch4.shape[0])

    df_bdcmps_month_watch = df_bdcmps_month[df_bdcmps_month['DVIC_TP'] == 360003]
    df_bdcmps_month_prev_watch = df_bdcmps_month_prev[df_bdcmps_month_prev['DVIC_TP'] == 360003]
    kpi53.metric(label='Galaxy Watch (360003)', value=millify(df_bdcmps_month_watch.shape[0], precision=2),
                 delta=df_bdcmps_month_watch.shape[0] - df_bdcmps_month_prev_watch.shape[0])

    df_bdcmps_month_external = df_bdcmps_month[df_bdcmps_month['DVIC_TP'] == 360002]
    df_bdcmps_month_prev_external = df_bdcmps_month_prev[df_bdcmps_month_prev['DVIC_TP'] == 360002]
    kpi54.metric(label='External Device (360002)', value=millify(df_bdcmps_month_external.shape[0], precision=2),
                 delta=df_bdcmps_month_external.shape[0] - df_bdcmps_month_prev_external.shape[0])

    e61, kpi61, kpi62, e62 = st.columns([1, 1, 1, 1])
    df_bdcmps_month_mobile = df_bdcmps_month[df_bdcmps_month['DVIC_TP'] == 360001]
    df_bdcmps_month_prev_mobile = df_bdcmps_month_prev[df_bdcmps_month_prev['DVIC_TP'] == 360001]
    kpi61.metric(label='Samsung Health (360001)', value=millify(df_bdcmps_month_mobile.shape[0], precision=2),
                 delta=df_bdcmps_month_mobile.shape[0] - df_bdcmps_month_prev_mobile.shape[0])

    df_bdcmps_month_unknown = df_bdcmps_month[df_bdcmps_month['DVIC_TP'] == 0]
    df_bdcmps_month_prev_unknown = df_bdcmps_month_prev[df_bdcmps_month_prev['DVIC_TP'] == 0]
    kpi62.metric(label='Samsung Health Device (0)', value=millify(df_bdcmps_month_unknown.shape[0], precision=2),
                 delta=df_bdcmps_month_unknown.shape[0] - df_bdcmps_month_prev_unknown.shape[0])

    st.markdown(' ')
    st.markdown(' ')
    e71, e72, kpi71, e73, e74 = st.columns([1, 1, 1, 1, 1])
    df_bdcmps_daily = df_bdcmps_month.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    df_bdcmps_daily_prev = df_bdcmps_month_prev.groupby('MSRE_DT')['WT'].count().mean()
    kpi71.metric(label='Measured Data per Day', value=millify(df_bdcmps_daily, precision=2),
                 delta=millify(df_bdcmps_daily - df_bdcmps_daily_prev, precision=2))

    kpi81, kpi82, kpi83, kpi84 = st.columns([1, 1, 1, 1])
    df_bdcmps_daily_fix = df_bdcmps_month_fix.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    df_bdcmps_daily_prev_fix = df_bdcmps_month_prev_fix.groupby('MSRE_DT')['WT'].count().mean()
    kpi81.metric(label='Smart Scale (90002) per Day', value=millify(df_bdcmps_daily_fix, precision=2),
                 delta=np.round(df_bdcmps_daily_fix - df_bdcmps_daily_prev_fix, 2))

    df_bdcmps_daily_watch4 = df_bdcmps_month_watch4.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    df_bdcmps_daily_prev_watch4 = df_bdcmps_month_prev_watch4.groupby('MSRE_DT')['WT'].count().mean()
    kpi82.metric(label='Galaxy Watch4 (90001) per Day', value=millify(0, precision=2),
                 delta=0)

    df_bdcmps_daily_watch = df_bdcmps_month_watch.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    df_bdcmps_daily_prev_watch = df_bdcmps_month_prev_watch.groupby('MSRE_DT')['WT'].count().mean()
    kpi83.metric(label='Galaxy Watch (360003) per Day', value=millify(df_bdcmps_daily_watch, precision=2),
                 delta=np.round(df_bdcmps_daily_watch - df_bdcmps_daily_prev_watch, 2))

    df_bdcmps_daily_external = df_bdcmps_month_external.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    df_bdcmps_daily_prev_external = df_bdcmps_month_prev_external.groupby('MSRE_DT')['WT'].count().mean()
    kpi84.metric(label='External Device (360002) per Day', value=millify(df_bdcmps_daily_external, precision=2),
                 delta=np.round(df_bdcmps_daily_external - df_bdcmps_daily_prev_external, 2))

    e91, kpi91, kpi92, e92 = st.columns([1, 1, 1, 1])
    df_bdcmps_daily_mobile = df_bdcmps_month_mobile.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    df_bdcmps_daily_prev_mobile = df_bdcmps_month_prev_mobile.groupby('MSRE_DT')['WT'].count().mean()
    kpi91.metric(label='Samsung Health (360001) per Day', value=millify(df_bdcmps_daily_mobile, precision=2),
                 delta=np.round(df_bdcmps_daily_mobile - df_bdcmps_daily_prev_mobile, 2))

    if np.isnan(df_bdcmps_month_unknown.groupby('MSRE_DT')['WT'].count()[:-1].mean()):
        df_bdcmps_daily_unknown = 0
    else:
        df_bdcmps_daily_unknown = df_bdcmps_month_unknown.groupby('MSRE_DT')['WT'].count()[:-1].mean()
    #print(df_bdcmps_daily_unknown)

    if np.isnan(df_bdcmps_month_prev_unknown.groupby('MSRE_DT')['WT'].count().mean()):
        df_bdcmps_daily_prev_unknown = 0
    else:
        df_bdcmps_daily_prev_unknown = df_bdcmps_month_prev_unknown.groupby('MSRE_DT')['WT'].count().mean()
    #print(df_bdcmps_daily_prev_unknown)

    kpi92.metric(label='Samsung Health Device (0) per Day', value=millify(df_bdcmps_daily_unknown, precision=2),
                 delta=np.round(df_bdcmps_daily_unknown - df_bdcmps_daily_prev_unknown, 2))

st.markdown(' ')
expander = st.expander('See all user information')
with expander:
    status_list = pd.unique(df_bdcmps['DVIC_TP']).tolist()
    status_list.append('전체')
    status = st.selectbox('Device type', status_list)

    if status == '전체':
        st.success(f'Data size : {df_bdcmps.shape}')
        st.dataframe(df_bdcmps)

    else:
        st.success(f"Data size : {df_bdcmps[df_bdcmps['DVIC_TP'] == status].shape}")
        st.dataframe(df_bdcmps[df_bdcmps['DVIC_TP'] == status])