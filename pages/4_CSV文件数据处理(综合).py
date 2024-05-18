import datetime
from typing import Union

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html


@st.cache_data
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
    data_split = data.truncate(time1, time2)
    return data_split


@st.cache_data
def utc2utc_8(time_index_name, df):
    time_stamps = pd.to_datetime(df[time_index_name])
    df[time_index_name] = time_stamps + pd.Timedelta(hours=8)
    df= df.set_index(time_index_name)
    return df


def data_analyse():
    st.header("数据处理")
    # 上传CSV文件
    st.subheader("上传CSV文件")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], label_visibility='collapsed')

    if uploaded_file is not None:
        # 读取CSV文件
        df = pd.read_csv(uploaded_file)
        df_index = df.index.values
        t_start = datetime.datetime.strptime(df.loc[0, 'DateTime'], '%Y-%m-%d %H:%M:%S').timestamp()
        t_end = datetime.datetime.strptime(df.loc[df_index[-1], 'DateTime'], '%Y-%m-%d %H:%M:%S').timestamp()
        day_start = df.loc[0, 'DateTime'].split(' ')[0]
        time_start = df.loc[0, 'DateTime'].split(' ')[-1]
        day_end = df.loc[df_index[-1], 'DateTime'].split(' ')[0]
        time_end = df.loc[df_index[-1], 'DateTime'].split(' ')[-1]

        st.subheader("选择时间区间")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            start_date = st.date_input("起始日期", value=datetime.datetime.strptime(day_start, '%Y-%m-%d'))
            start_date = start_date.strftime('%Y-%m-%d')
        with col2:
            start_time = st.text_input('起始时间', value=time_start, placeholder='hh:mm:ss')
        with col3:
            end_date = st.date_input("结束日期", value=datetime.datetime.strptime(day_end, '%Y-%m-%d'))
            end_date = end_date.strftime('%Y-%m-%d')
        with col4:
            end_time = st.text_input('结束时间', value=time_end, placeholder='hh:mm:ss')
        with col5:
            # 列名选择
            time_column = st.selectbox("选择时间列", df.columns)

        start_datetime_str = f"{start_date} {start_time}"
        start_datetime = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
        end_datetime_str = f"{end_date} {end_time}"
        end_datetime = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
        start_stamps = start_datetime.timestamp()
        end_stamps = end_datetime.timestamp()

        display_df = df.set_index(df.columns[0])
        csv_data = pd.DataFrame([]).to_csv()
        file_name = 'example.csv'

        col21, col22, col23, col24, col25 = st.columns(5)
        with col23:
            if st.button('截取数据', use_container_width=True):
                if start_datetime and end_datetime:
                    # 保存分割后的数据到新的CSV文件
                    t1 = datetime.datetime.strftime(start_datetime, '%Y-%m-%d_%H-%M-%S')
                    t2 = datetime.datetime.strftime(end_datetime, '%Y-%m-%d_%H-%M-%S')
                    file_name = f"DataSplit_{t1}_{t2}.csv"
                    if t_start <= start_stamps < end_stamps <= t_end:
                        # 分割数据
                        split_df = split_data_by_datetime(df, time_column, start_datetime_str,
                                                          end_datetime_str)
                        csv_data = split_df.to_csv().encode('utf-8')
                        display_df = split_df
                    else:
                        split_df = pd.DataFrame([]), pd.DataFrame([]).to_csv()
                        csv_data = split_df.to_csv().encode('utf-8')
                        display_df = split_df
                        alert_js = '''
                        alert('超出数据的时间范围!请检查输入的起止日期和终止日期。');
                        '''
                        html(f"<script>{alert_js}</script>")
        with col24:
            if st.button('转换utc8时间', use_container_width=True):
                file_name = uploaded_file.name.replace('.csv', '-utc-8.csv')
                utc_data = utc2utc_8(time_column, df)
                display_df = utc_data
                csv_data = utc_data.to_csv().encode('utf-8')
        with col25:
            st.download_button('保存csv文件', data=csv_data, file_name=file_name, mime='text/csv',
                               use_container_width=True)

        st.subheader(f'csv文件内容:')
        st.dataframe(display_df,width=None,use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(page_title="数据处理分析工具", layout="wide")
    data_analyse()
