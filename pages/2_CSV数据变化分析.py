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


def data_plotly():
    st.header("数据变化趋势分析")

    # 上传CSV文件
    st.subheader("上传CSV文件")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], label_visibility='collapsed')

    if uploaded_file is not None:
        # 读取CSV文件
        df = pd.read_csv(uploaded_file)

        plot_type = st.selectbox('选择画图类型', options=['bar', 'scatter', 'line'], index=2)

        if 'y1_columns' not in st.session_state:
            st.session_state['y1_columns'] = df.columns[[1]].tolist()

        if 'y2_columns' not in st.session_state:
            st.session_state['y2_columns'] = df.columns[[-2, -3]].tolist()
        # 列名选择
        choose_col_1, choose_col_2, choose_col_3 = st.columns(3)
        with choose_col_1:
            x_column = st.selectbox("选择 X 列", df.columns)
        with choose_col_2:
            y1_columns = st.multiselect("选择 Y1 列", df.columns,
                                        on_change=get_y1_column, key='y1_columns')
        with choose_col_3:
            y2_columns = st.multiselect("选择 Y2 列", df.columns,
                                        on_change=get_y2_column, key='y2_columns')
        col_11, col_12, col_13 = st.columns(3)
        with col_11:
            del_zero_rows = st.checkbox('删除数据中包含0的行', value=False)
            if del_zero_rows:
                del_name = st.multiselect('删除数据的列名', df.columns, on_change=get_y1_column(), key='del_name',
                                        label_visibility='collapsed')

                for c in del_name:
                    df = df[df[c] != 0]

        if plot_type == 'bar':
            pass
        elif plot_type == 'scatter':
            if y1_columns and y2_columns:
                # 创建一个新的图形对象
                fig = go.Figure()

                # 添加第一个 Y 轴
                for y1_column in y1_columns:
                    fig.add_trace(
                        go.Scatter(x=df[x_column], y=df[y1_column], mode='markers', name=y1_column, yaxis='y1',
                                   line_shape='linear', line_width=1, marker_size=4))
                for y2_column in y2_columns:
                    fig.add_trace(
                        go.Scatter(x=df[x_column], y=df[y2_column], mode='markers', name=y2_column, xaxis='x2',
                                   yaxis='y2', line_shape='linear', line_width=1, marker_size=4,
                                   marker_symbol='diamond'))
                df_min = df.min()
                df_max = df.max()
                # print(df_max)
                all_min = df_min[y1_columns + y2_columns].min()
                all_max = df_max[y1_columns + y2_columns].max()
                # print('1  ',all_min,all_max,)

                # 设置图形布局
                fig.update_layout(
                    template='none',
                    title=f'({get_ylabel(y1_columns)} / {get_ylabel(y2_columns)}) ~ {x_column}',
                    xaxis=dict(title=x_column, tickmode='auto', nticks=10, showgrid=True, showline=True, linewidth=1.5,
                               linecolor='black', ),
                    xaxis2=dict(title='', showticklabels=False, tickmode='auto', nticks=10, showgrid=True,
                                showline=True, linewidth=1.5,
                                anchor='y2', overlaying='x', side='top'),
                    yaxis=dict(title=get_ylabel(y1_columns), showgrid=True, showline=True, linewidth=1.5,
                               linecolor='black',
                               # range=[all_min, all_max],
                               ),
                    yaxis2=dict(title=get_ylabel(y2_columns), overlaying="y", side="right", showgrid=True,
                                showline=True,
                                linewidth=1.5, linecolor='black',
                                # range=[all_min, all_max], scaleanchor='y1',
                                ),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, ),
                    # autosize=False, width=1000, height=500,
                )

                # 显示图形
                st.plotly_chart(fig, use_container_width=True)
                # st.subheader("数据查看")
                # st.write(df)
            else:
                st.warning("请选择至少两列作为 Y1 和 Y2 列进行图表绘制。")
        elif plot_type == 'line':
            with col_13:
                show_markers = st.checkbox("显示数据点", value=False)
            # show_markers = 0
            if y1_columns and y2_columns:
                # 创建一个新的图形对象
                fig = go.Figure()

                # 添加第一个 Y 轴
                for y1_column in y1_columns:
                    if show_markers:
                        fig.add_trace(
                            go.Scatter(x=df[x_column], y=df[y1_column], mode='lines+markers', name=y1_column,
                                       yaxis='y1',
                                       line_shape='linear', line_width=1, marker_size=4))
                    else:
                        fig.add_trace(
                            go.Scatter(x=df[x_column], y=df[y1_column], mode='lines', name=y1_column, yaxis='y1',
                                       line_shape='linear', line_width=1))

                # 添加第二个 Y 轴
                for y2_column in y2_columns:
                    if show_markers:
                        fig.add_trace(
                            go.Scatter(x=df[x_column], y=df[y2_column], mode='lines+markers', name=y2_column,
                                       xaxis='x2',
                                       yaxis='y2', line_shape='linear', line_width=1, marker_size=4,
                                       marker_symbol='diamond'))
                    else:
                        fig.add_trace(
                            go.Scatter(x=df[x_column], y=df[y2_column], mode='lines', name=y2_column, xaxis='x2',
                                       yaxis='y2', line_shape='linear', line_width=1))

                df_min = df.min()
                df_max = df.max()
                # print(df_max)
                all_min = df_min[y1_columns + y2_columns].min()
                all_max = df_max[y1_columns + y2_columns].max()
                # print('1  ',all_min,all_max,)

                # 设置图形布局
                fig.update_layout(
                    template='none',
                    title=f'({get_ylabel(y1_columns)} / {get_ylabel(y2_columns)}) ~ {x_column}',
                    xaxis=dict(title=x_column, tickmode='auto', nticks=10, showgrid=True, showline=True, linewidth=1.5,
                               linecolor='black', ),
                    xaxis2=dict(title='', showticklabels=False, tickmode='auto', nticks=10, showgrid=True,
                                showline=True, linewidth=1.5,
                                anchor='y2', overlaying='x', side='top'),
                    yaxis=dict(title=get_ylabel(y1_columns), showgrid=True, showline=True, linewidth=1.5,
                               linecolor='black',
                               # range=[all_min, all_max],
                               ),
                    yaxis2=dict(title=get_ylabel(y2_columns), overlaying="y", side="right", showgrid=True,
                                showline=True,
                                linewidth=1.5, linecolor='black',
                                # range=[all_min, all_max], scaleanchor='y1',
                                ),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, ),
                    # autosize=False, width=1000, height=500,
                )

                # 显示图形
                st.plotly_chart(fig, use_container_width=True)
                # st.subheader("数据查看")
                # st.write(df)
            else:
                st.warning("请选择至少两列作为 Y1 和 Y2 列进行图表绘制。")


if __name__ == "__main__":
    st.set_page_config(page_title="折线图分析-数据处理分析工具", layout="wide")
    data_plotly()
