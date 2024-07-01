import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def get_ylabel(y_cloumns):
    if len(y_cloumns) == 1:
        y_label = y_cloumns[0]
    else:
        y_label = ' / '.join(y_cloumns)
    return y_label


def get_y1_column():
    print('y1 changed!')
    pass


def get_y2_column():
    print('y2 changed!')
    pass


if __name__ == "__main__":
    st.set_page_config(page_title="数据处理分析工具", layout="wide")
    st.header("恒温槽温度监测")
    # 上传CSV文件
    st.subheader("读取CSV文件")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], label_visibility='collapsed')
    if uploaded_file is not None:
        init_file = f"D:\\Tool\\TemperatureControl\\TestData\\{uploaded_file.name}"
        data_file = st.text_input('输入数据文件的路径：', value=init_file, )
        if data_file is not None:
            # 读取CSV文件
            # df = pd.read_csv(uploaded_file)
            df = pd.read_csv(data_file)
            if 'y1_columns' not in st.session_state:
                st.session_state['y1_columns'] = df.columns[[1]].tolist()

            if 'y2_columns' not in st.session_state:
                st.session_state['y2_columns'] = df.columns[[-3, -2]].tolist()

            # 列名选择
            choose_col_1, choose_col_2, choose_col_3 = st.columns(3)
            with choose_col_1:
                x_column = st.selectbox("选择 X 列", df.columns)
            with choose_col_2:
                y1_columns = st.multiselect("选择 Y1 列", df.columns,
                                            # default=st.session_state['y1_columns'],
                                            on_change=get_y1_column, key='y1_columns')

            with choose_col_3:
                y2_columns = st.multiselect("选择 Y2 列", df.columns,
                                            # default=st.session_state['y2_columns'],
                                            on_change=get_y2_column, key='y2_columns')

            show_markers = st.checkbox("显示数据点", value=True)
            max_size = df.index.size
            if max_size <= 120:
                pass
            else:
                df = df.iloc[max_size - 121::]

        if y1_columns and y2_columns:
            # 创建一个新的图形对象
            fig = go.Figure()

            # 添加第一个 Y 轴
            for y1_column in y1_columns:
                if show_markers:
                    fig.add_trace(
                        go.Scatter(x=df[x_column], y=df[y1_column], mode='lines+markers', name=y1_column, yaxis='y1',
                                   line_shape='linear', line_width=1, marker_size=4))
                else:
                    fig.add_trace(go.Scatter(x=df[x_column], y=df[y1_column], mode='lines', name=y1_column, yaxis='y1',
                                             line_shape='linear', line_width=1))

            # 添加第二个 Y 轴
            for y2_column in y2_columns:
                if show_markers:
                    fig.add_trace(
                        go.Scatter(x=df[x_column], y=df[y2_column], mode='lines+markers', name=y2_column, xaxis='x2',
                                   yaxis='y2', line_shape='linear', line_width=1, marker_size=4,
                                   marker_symbol='diamond'))
                else:
                    fig.add_trace(go.Scatter(x=df[x_column], y=df[y2_column], mode='lines', name=y2_column, xaxis='x2',
                                             yaxis='y2', line_shape='linear', line_width=1))

            df_min = df.min()
            df_max = df.max()
            all_min = df_min[y1_columns + y2_columns].min()
            all_max = df_max[y1_columns + y2_columns].max()

            # 设置图形布局
            fig.update_layout(
                template='none',
                title=f'({get_ylabel(y1_columns)} / {get_ylabel(y2_columns)}) ~ {x_column}',
                xaxis=dict(title=x_column, tickmode='auto', nticks=10, showgrid=True, showline=True, linewidth=1.5,
                           linecolor='black', ),
                xaxis2=dict(title='', showticklabels=False, tickmode='auto', nticks=10, showgrid=True,
                            showline=True, linewidth=1.5,
                            anchor='y2', overlaying='x', side='top'),
                yaxis=dict(title=get_ylabel(y1_columns), showgrid=True, showline=True, linewidth=1.5, linecolor='black',
                           # range=[all_min, all_max]
                           ),
                yaxis2=dict(title=get_ylabel(y2_columns), overlaying="y", side="right", showgrid=True, showline=True,
                            linewidth=1.5, linecolor='black',
                            # range=[all_min, all_max], scaleanchor='y1'
                            ),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, ),
                autosize=True,
                # autosize=False, width=1400, height=500,
            )

            # 显示图形
            plotly_figure = st.plotly_chart(fig, use_container_width=True)

            y_all_columns = y1_columns + y2_columns
            count = 1
            print(x_column)
            while True:
                df = pd.read_csv(data_file)
                # print(df.index.size)
                max_size = df.index.size
                if max_size <= 120:
                    for i in range(len(y_all_columns)):
                        fig.data[i].x = df[x_column]
                        fig.data[i].y = df[y_all_columns[i]]
                else:
                    data_index = list(range(max_size - 121, max_size))
                    # print(data_index)
                    for i in range(len(y_all_columns)):
                        fig.data[i].x = df[x_column][data_index]
                        fig.data[i].y = df[y_all_columns[i]][data_index]
                fig.update_layout(autosize=False, width=1250, height=500, )
                plotly_figure.write(fig)
                count += 1
                print(count)
                time.sleep(1)
        else:
            st.warning("请选择至少两列作为 Y1 和 Y2 列进行图表绘制。")
