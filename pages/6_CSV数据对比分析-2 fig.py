import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def get_ylabel(y_cloumns):
    if len(y_cloumns) == 1:
        y_label = y_cloumns[0]
    else:
        y_label = ' / '.join(y_cloumns)
    return y_label


def get_y_column():
    print('y changed!')
    pass


def plot_data(df, plot_type, x_column, y1_columns, y2_columns, show_markers):
    fig = go.Figure()
    mode = 'lines+markers' if show_markers else 'lines'

    for y1_column in y1_columns:
        if plot_type == 'scatter':
            fig.add_trace(go.Scatter(x=df[x_column], y=df[y1_column], mode='markers', name=y1_column, yaxis='y1'))
        elif plot_type == 'line':
            fig.add_trace(go.Scatter(x=df[x_column], y=df[y1_column], mode=mode, name=y1_column, yaxis='y1'))

    for y2_column in y2_columns:
        if plot_type == 'scatter':
            fig.add_trace(
                go.Scatter(x=df[x_column], y=df[y2_column], mode='markers', name=y2_column, xaxis='x2', yaxis='y2'))
        elif plot_type == 'line':
            fig.add_trace(
                go.Scatter(x=df[x_column], y=df[y2_column], mode=mode, name=y2_column, xaxis='x2', yaxis='y2'))

    fig.update_layout(
        template='none',
        title=f'({get_ylabel(y1_columns)} / {get_ylabel(y2_columns)}) ~ {x_column}',
        xaxis=dict(title=x_column, tickmode='auto', nticks=10, showgrid=True, showline=True, linewidth=1.5,
                   linecolor='black'),
        xaxis2=dict(showticklabels=False, tickmode='auto', nticks=10, showgrid=True, showline=True, linewidth=1.5,
                    anchor='y2', overlaying='x', side='top'),
        yaxis=dict(title=get_ylabel(y1_columns), showgrid=True, showline=True, linewidth=1.5, linecolor='black'),
        yaxis2=dict(title=get_ylabel(y2_columns), overlaying="y", side="right", showgrid=True, showline=True,
                    linewidth=1.5, linecolor='black'),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )

    return fig


def data_plotly():
    st.header("数据变化趋势对比分析")

    header_1, header_2 = st.columns(2)
    with header_1:
        st.subheader("上传CSV文件 1")
        uploaded_file_1 = st.file_uploader("上传CSV文件 1", type=["csv"], label_visibility='collapsed')
    with header_2:
        st.subheader("上传CSV文件 2")
        uploaded_file_2 = st.file_uploader("上传CSV文件 2", type=["csv"], label_visibility='collapsed')

    if uploaded_file_1 is not None and uploaded_file_2 is not None:
        df1 = pd.read_csv(uploaded_file_1)
        df2 = pd.read_csv(uploaded_file_2)

        plot_type = st.selectbox('选择画图类型', options=['scatter', 'line'], index=1)

        if 'y1_columns_1' not in st.session_state:
            st.session_state['y1_columns_1'] = df1.columns[[1]].tolist()
        if 'y2_columns_1' not in st.session_state:
            st.session_state['y2_columns_1'] = df1.columns[[-2, -3]].tolist()

        if 'y1_columns_2' not in st.session_state:
            st.session_state['y1_columns_2'] = df2.columns[[1]].tolist()
        if 'y2_columns_2' not in st.session_state:
            st.session_state['y2_columns_2'] = df2.columns[[-2, -3]].tolist()

        title_column_1, title_column_2 = st.columns(2)

        with title_column_1:
            st.write("CSV 文件 1 配置")
            x_column_1 = st.selectbox("选择 X 列", df1.columns, key='x_column_1')
            y1_columns_1 = st.multiselect("选择 Y1 列", df1.columns,
                                          on_change=get_y_column,
                                          # default=st.session_state['y1_columns_1'],
                                          key='y1_columns_1')
            y2_columns_1 = st.multiselect("选择 Y2 列", df1.columns,
                                          on_change=get_y_column,
                                          # default=st.session_state['y2_columns_1'],
                                          key='y2_columns_1')
        with title_column_2:
            st.write("CSV 文件 2 配置")
            x_column_2 = st.selectbox("选择 X 列", df2.columns, key='x_column_2')
            y1_columns_2 = st.multiselect("选择 Y1 列", df2.columns,
                                          on_change=get_y_column,
                                          # default=st.session_state['y1_columns_2'],
                                          key='y1_columns_2')
            y2_columns_2 = st.multiselect("选择 Y2 列", df2.columns,
                                          on_change=get_y_column,
                                          # default=st.session_state['y2_columns_2'],
                                          key='y2_columns_2')

        col_31, col_32, col_33 = st.columns(3)
        with col_31:
            del_zero_rows = st.checkbox('删除数据中包含0的行', value=False)
            if del_zero_rows:
                del_name_1 = st.multiselect('删除数据的列名 1', df1.columns, key='del_name_1',
                                            label_visibility='collapsed')
                for c in del_name_1:
                    df1 = df1[df1[c] != 0]
                del_name_2 = st.multiselect('删除数据的列名 2', df2.columns, key='del_name_2',
                                            label_visibility='collapsed')
                for c in del_name_2:
                    df2 = df2[df2[c] != 0]

        if y1_columns_1 and y2_columns_1 and y1_columns_2 and y2_columns_2:
            with col_33:
                show_markers = st.checkbox("显示数据点", value=False)

            fig1 = plot_data(df1, plot_type, x_column_1, y1_columns_1, y2_columns_1, show_markers)
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = plot_data(df2, plot_type, x_column_2, y1_columns_2, y2_columns_2, show_markers)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("请选择至少两列作为 Y1 和 Y2 列进行图表绘制。")


if __name__ == "__main__":
    st.set_page_config(page_title="折线图分析-数据处理分析工具", layout="wide")
    data_plotly()
