import pandas as pd
import streamlit as st


@st.cache_data
def utc2utc_8(time_index_name, df):
    time_stamps = pd.to_datetime(df[time_index_name])
    df[time_index_name] = time_stamps + pd.Timedelta(hours=8)
    return df.to_csv(index=None).encode("utf-8")


def time2beijing():
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], label_visibility='collapsed')

    if uploaded_file is not None:
        st.subheader(f'预览文件：{uploaded_file.name}')
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
        # time_index_name = st.text_input('时间列名', value='DateTime', placeholder='DateTime')
        time_index_name = st.selectbox('选择时间列',df.columns)
        filename = uploaded_file.name.replace('.csv', '-utc-8.csv')
        utc_data = utc2utc_8(time_index_name, df)
        st.download_button('转换时间并下载为csv', data=utc_data, file_name=filename, mime='text/csv')


if __name__ == "__main__":
    st.set_page_config(page_title="csv时间处理工具", layout="wide")
    st.header('UTC时间转UTC-8时间')
    time2beijing()
