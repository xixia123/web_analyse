import os
from datetime import datetime, timedelta
import streamlit as st
import numpy as np
import pandas as pd


def pretreatment(df):
    df.drop(df.columns[-1], axis=1, inplace=True)
    drop_columns = ['Ch1Ampl', 'Ch2Ampl', 'Ch3Ampl', 'Ch4Ampl', 'Ch5Ampl',
                    'Ch1rAmpl', 'Ch2rAmpl', 'Ch3rAmpl', 'Ch4rAmpl', 'Ch5rAmpl',
                    'Ch1FSpd', 'Ch2FSpd', 'Ch3FSpd', 'Ch4FSpd', 'Ch5FSpd', ]
    df.drop(labels=drop_columns, axis=1, inplace=True)
    ch_zero = df.query('Ch3Dt==0')
    df = df.drop(ch_zero.index)
    df['MKTAvg'] = df[['MKTCh1', 'MKTCh2']].mean(axis=1)
    df['Spd'] = (1402.39 + 1478.5625 * df['MKTAvg'] / 100) / (
            1 + 0.69494542 * df['MKTAvg'] / 100 + 0.16618854 * (df['MKTAvg'] / 100) * (
            df['MKTAvg'] / 100) - 0.0160586 * (df['MKTAvg'] / 100) * (df['MKTAvg'] / 100) * (
                    df['MKTAvg'] / 100) + 0.02192692 * (df['MKTAvg'] / 100) * (df['MKTAvg'] / 100) * (
                    df['MKTAvg'] / 100) * (df['MKTAvg'] / 100))
    df['Ch1Distance'] = df['Spd'] * df['Ch1Dt'] / 2 * 0.000001
    df['Ch2Distance'] = df['Spd'] * df['Ch2Dt'] / 2 * 0.000001
    df['Ch3Distance'] = df['Spd'] * df['Ch3Dt'] / 2 * 0.000001
    df['Ch4Distance'] = df['Spd'] * df['Ch4Dt'] / 2 * 0.000001
    df['Ch5Distance'] = df['Spd'] * df['Ch5Dt'] / 2 * 0.000001
    df = df.set_index('DateTime')
    return df


def sigma_principle(df0, name, n):
    """
    对数据指定列按照3-sigma原则进行处理，返回值为超出可信范围的索引
    :param df0: pandas.Dataframe数据
    :param name: 数据列名字
    :param n: 自定义设置按照几倍原则进行处理
    :return: 返回删除异常数据行后的数据
    """
    min_mask = df0[name] < (df0[name].mean() - n * df0[name].std())
    max_mask = df0[name] > (df0[name].mean() + n * df0[name].std())
    mask = min_mask | max_mask
    delete_index = mask[mask[:] == 1].index
    df = df0.drop(index=delete_index)
    return df


def create_date_named_folder(base_path):
    # 获取当前日期和时间并格式化为字符串
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # 构造新文件夹路径
    new_folder_path = os.path.join(base_path, date_str)

    try:
        # 创建新文件夹
        os.makedirs(new_folder_path, exist_ok=True)
        return f"已在路径 {base_path} 下创建文件夹 {new_folder_path}", new_folder_path
    except Exception as e:
        return f"创建文件夹失败: {e}", None


def check_and_create_folder(path):
    if os.path.isfile(path):
        # 如果是文件，获取其所在的文件夹路径
        base_path = os.path.dirname(path)
        message, folder_path = create_date_named_folder(base_path)
        return message, folder_path
    elif os.path.isdir(path):
        # 如果是文件夹，直接在该文件夹下创建子文件夹
        message, folder_path = create_date_named_folder(path)
        return message, folder_path
    else:
        return "这既不是一个文件，也不是一个文件夹", None


def remove_constant_rows(df, column):
    # 检查指定的列是否存在于 DataFrame 中
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")

    # 初始化一个布尔列表，长度与 DataFrame 行数相同，用于标记需要保留的行
    to_keep = [True] * len(df)
    prev_value = None
    count = 0
    count_n = 10  # 设置连续出现的阈值

    # 遍历指定列中的每个元素
    for i, value in enumerate(df[column]):
        if value == prev_value:
            count += 1
        else:
            if count > count_n:
                # 如果前一个值连续出现超过 count_n 次，将这些行标记为不保留
                for j in range(i - count, i):
                    to_keep[j] = False
            prev_value = value
            count = 1

    # 处理列结束后的最后一个值
    if count > count_n:
        for j in range(len(df) - count + 1, len(df)):
            to_keep[j] = False

    # 返回保留的行组成的新 DataFrame
    return df[to_keep]


def analyse_realtime_data(file_path_realtime, file_path_result):
    df_realtime = pd.read_csv(file_path_realtime)
    df_result = pd.read_csv(file_path_result)
    df_realtime = pretreatment(df_realtime)
    start_times = df_result['TestStartTime']
    end_times = df_result['TestEndTime']
    result = []
    columns_name = []
    nxsigma = 3
    csv_data = []
    csv_data_sigma = []
    columns_to_process = [
        'MKTAvg',
        'Ch1Dt',
        'Ch2Dt',
        'Ch3Dt',
        'Ch4Dt',
        'Ch5Dt'
    ]
    for i in range(start_times.size):
        time1 = start_times.loc[i]
        time2 = end_times.loc[i]
        dt = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        # dt_before = dt - timedelta(minutes=1)
        # time1 = dt_before.strftime("%Y-%m-%d %H:%M:%S")
        temp_df = df_realtime.truncate(time1, time2)
        csv_data.append(temp_df)
        for j in range(len(columns_to_process)):
            column = columns_to_process[j]
            if j == 0:
                temp_df_sigma = sigma_principle(temp_df, column, n=nxsigma)
            else:
                temp_df_sigma = sigma_principle(temp_df_sigma, column, n=nxsigma)

        temp_df_remove_constant = remove_constant_rows(temp_df_sigma, 'Ch3Dt')
        csv_data_sigma.append(temp_df_remove_constant)
        des2 = temp_df_remove_constant.describe()
        result.append(des2.loc[['mean'], :])
        columns_name.append(df_result.loc[i, 'TestCondition'])
        pass

    message, folder_path = check_and_create_folder(file_path_realtime)
    res_df = pd.concat(result)
    res_df.insert(0, 'TestCondition', columns_name)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    res_file = os.path.join(folder_path, f"result_{nxsigma}xsigma_{date_str}.csv")
    res_df.to_csv(res_file, index=None)

    csv_df = pd.concat(csv_data)
    csv_file = os.path.join(folder_path, f"realtime_data_extract_{date_str}_ori.csv")
    csv_df.to_csv(csv_file)
    csv_df_sigma = pd.concat(csv_data_sigma)
    sigma_file = os.path.join(folder_path, f"realtime_data_extract_{nxsigma}xsigma_{date_str}.csv")
    csv_df_sigma.to_csv(sigma_file)

    analyse_xlsx_file = os.path.join(folder_path, f"{date_str}_analyse.xlsx")
    xlsx_df = pd.DataFrame()
    with pd.ExcelWriter(analyse_xlsx_file) as f:
        xlsx_df.to_excel(f)
    print('done')
    # return res_df,csv_df,csv_df_sigma,analyse_xlsx_file
    return folder_path


def summary_re(file_path):
    # file_path = r'D:\Tool\TemperatureControl\TestData\测试结果汇总'
    files = os.listdir(file_path,)
    files_list = []
    for i in files:
        if os.path.splitext(i)[-1] == '.xlsx':
            files_list.append(i)

    test_re = []
    for f in files_list:
        data = pd.read_excel(os.path.join(file_path, f), sheet_name=None)

        try:
            df0 = data[list(data.keys())[1]]
            df0.columns.values[0] = 'testdate'
            df0['testdate'] = f.split('_')[-1].split('.')[0]
            # df0.iloc[0, 0] = f.split('_')[-1].split('.')[0]
            temp_v = df0.values
            if len(test_re) == 0:
                test_re = temp_v
            else:
                test_re = np.append(test_re, temp_v, axis=0)
        except:
            print(f'{f}报错！')
    df1 = pd.DataFrame(test_re, columns=['testdate', 'y=ax+b', '1#', '2#', '3#', '4#', '5#'])
    df_a = df1[df1['y=ax+b'] == 'a']
    df_b = df1[df1['y=ax+b'] == 'b']
    df_dppm = df1[df1['y=ax+b'] == r'a/50']
    df_spde_std = df1[df1['y=ax+b'] == '声速偏差标准差']

    message, folder_path = check_and_create_folder(file_path)
    output = os.path.join(folder_path, 'Test_Result_Summary.xlsx')
    if os.path.isfile(output):
        os.remove(output)
    with pd.ExcelWriter(output) as file:
        df1.to_excel(file, index=None, sheet_name='sheet1', startrow=0)
        df_a.to_excel(file, index=None, sheet_name='sheet2', startrow=0)
        df_b.to_excel(file, index=None, sheet_name='sheet2', startrow=(df_a.shape[0] + 1) + 1)
        df_dppm.to_excel(file, index=None, sheet_name='sheet2', startrow=2 * (df_a.shape[0] + 1) + 2)
        df_spde_std.to_excel(file, index=None, sheet_name='sheet2', startrow=3 * (df_a.shape[0] + 1) + 3)
    return output


if __name__ == "__main__":
    st.set_page_config(page_title="数据处理分析工具", layout="wide")
    st.subheader("声速探头数据分析")
    uploaded_file_1 = st.text_input('RealTime数据文件路径：', None,placeholder='测试得到的RealTime数据文件路径')
    uploaded_file_2 = st.text_input('ResultTime数据文件路径：', None,placeholder='测试得到的ResultTime数据文件路径')
    bt1 = st.button('数据分析计算', )
    if uploaded_file_1 is not None and uploaded_file_2 is not None:
        uploaded_file_1 = uploaded_file_1.strip('"')
        uploaded_file_2 = uploaded_file_2.strip('"')
        if bt1:
            folder = analyse_realtime_data(uploaded_file_1,uploaded_file_2)
            st.success(f"分析结果存储在{folder}")
    st.divider()
    st.subheader("声速探头测试结果汇总")
    uploaded_file_3 = st.text_input('RealTime数据文件路径：', None,placeholder='请输入测试结果文件所在的文件夹')
    # st.warning('运行前确保该文件夹下没有汇总后的结果文件')
    bt2 = st.button('测试结果汇总', )
    if uploaded_file_3 is not None:
        uploaded_file_3 = uploaded_file_3.strip('"')
        if bt2:
            output_file = summary_re(uploaded_file_3)
            st.success(f"汇总结果保存在{output_file}")
