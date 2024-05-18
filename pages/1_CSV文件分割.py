import datetime
from typing import Union

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html


def split_data_by_datetime(df: pd.DataFrame, index_name: str, time1: Union[str, pd.Timestamp],
                           time2: Union[str, pd.Timestamp]) -> pd.DataFrame:
    """
    Split the DataFrame based on the specified time range.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - index_name (str): The name of the index to be set for the DataFrame.
    - time1 (Union[str, pd.Timestamp]): The start time for truncation.
    - time2 (Union[str, pd.Timestamp]): The end time for truncation.

    Returns:
    - pd.DataFrame: The truncated DataFrame.
    """
    data = df.set_index(index_name)
    data_new = data.truncate(time1, time2)
    return data_new


def data_spilt():
    st.header("CSV数据按时间段切片")
    # 上传CSV文件
    st.subheader("上传CSV文件")
    uploaded_file1 = st.file_uploader("上传CSV文件", type=["csv"], label_visibility='collapsed')

    if uploaded_file1 is not None:
        # 读取CSV文件
        df = pd.read_csv(uploaded_file1)
        df_index = df.index.values
        t_start = datetime.datetime.strptime(df.loc[0, 'DateTime'], '%Y-%m-%d %H:%M:%S').timestamp()
        t_end = datetime.datetime.strptime(df.loc[df_index[-1], 'DateTime'], '%Y-%m-%d %H:%M:%S').timestamp()

        data_col1, data_col2 = st.columns(2)
        with data_col1:
            st.subheader("头部数据预览")
            st.write(df.head())
        with data_col2:
            st.subheader("尾部数据预览")
            st.write(df.tail())
    else:
        df = pd.DataFrame([])

    st.subheader("选择时间区间")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        start_date = st.date_input("起始日期")
        start_date = start_date.strftime('%Y-%m-%d')
    with col2:
        start_time = st.text_input('起始时间', value='00:00:00', placeholder='hh:mm:ss')
        # start_time = st.text_input('起始时间',placeholder='hh:mm:ss')

    with col3:
        end_date = st.date_input("结束日期")
        end_date = end_date.strftime('%Y-%m-%d')
    with col4:
        end_time = st.text_input('结束时间', value='00:00:00', placeholder='hh:mm:ss')
    start_datetime_str = f"{start_date} {start_time}"
    start_datetime = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_datetime_str = f"{end_date} {end_time}"
    end_datetime = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    start_stamps = start_datetime.timestamp()
    end_stamps = end_datetime.timestamp()

    with col5:
        # 列名选择
        time_column = st.selectbox("选择时间列", df.columns)

    col21, col22, col23, col24, col25 = st.columns(5)

    filtered_df = pd.DataFrame([])
    filename = 'example.csv'

    with col24:
        if st.button("截取数据", use_container_width=True):
            st.write(start_datetime_str, end_datetime_str)
            if start_datetime and end_datetime:
                if t_start < start_stamps < end_stamps < t_end:
                    # 分割数据
                    filtered_df = split_data_by_datetime(df, time_column, start_datetime_str, end_datetime_str)

                    # 保存分割后的数据到新的CSV文件
                    t1 = datetime.datetime.strftime(start_datetime, '%Y-%m-%d_%H-%M-%S')
                    t2 = datetime.datetime.strftime(end_datetime, '%Y-%m-%d_%H-%M-%S')
                    filename = f"Data_{t1}_{t2}.csv"
                    # print(filename)

                    with col23:
                        st.success("数据已成功截取！")
                else:
                    alert_js = '''
                    alert('超出数据的时间范围!请检查输入的起止日期和终止日期。');
                    '''
                    html(f"<script>{alert_js}</script>")
    with col25:
        if not filtered_df.empty:
            # 如果数据框非空，则显示下载按钮
            st.download_button(label="点击保存数据文件", data=filtered_df.to_csv(index=True),
                               file_name=filename,
                               use_container_width=True)
        else:
            # 如果数据框为空，则禁用下载按钮
            st.download_button(label="点击保存数据文件", data=filtered_df.to_csv(index=True), disabled=True,
                               use_container_width=True)


st.set_page_config(page_title="数据分割-数据处理分析工具", layout="wide")
data_spilt()
