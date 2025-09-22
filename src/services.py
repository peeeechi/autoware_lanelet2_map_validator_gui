import streamlit as st
import os
import pandas as pd
import plotly.graph_objs as go
from run_script import run_validator
from models.validation_results import ValidationResults
from load_lanelet import get_lane_polygon

# --- 定数 ---
CHART_SIZE = 1200

# --- ロジック関数 ---
def load_and_merge_data(validation_results: ValidationResults):
    """
    検証結果とCSVファイルを結合し、DataFrameを返します。
    """
    df_data = []
    for req in validation_results.requirements:
        for validator in req.validators:
            if not validator.passed:
                for issue in validator.issues:
                    df_data.append({
                        'status': '❌',
                        'requirement_id': req.id,
                        'validator_name': validator.name,
                        'issue_code': issue.issue_code,
                        'message': issue.message,
                        'primitive': issue.primitive,
                        'lane_id': str(issue.id)
                    })
            else:
                df_data.append({
                    'status': '✅',
                    'requirement_id': req.id,
                    'validator_name': validator.name,
                    'issue_code': '',
                    'message': '',
                    'primitive': '',
                    'lane_id': ''
                })
    
    df = pd.DataFrame(df_data)
    
    # === CSVファイルを読み込み、DataFrameを結合 ===
    try:
        csv_file_path = os.path.join(os.path.dirname(__file__), "table.csv")
        df_table = pd.read_csv(csv_file_path)

        merged_df = pd.merge(df, df_table, left_on='requirement_id', right_on='ID', how='left')
        merged_df.drop(columns=['ID'], inplace=True)

        return merged_df

    except FileNotFoundError:
        st.warning("`table.csv`ファイルが見つかりません。")
        return df

def create_plotly_figure(file_path: str, selected_lane_id: str | None, chart_size: int = CHART_SIZE):
    """
    Plotlyグラフオブジェクトを生成し、ハイライトを適用します。
    """
    lanelet_polygon_list = get_lane_polygon(file_path)
    fig = go.Figure()
    
    all_x = []
    all_y = []
    for polygon in lanelet_polygon_list.root:
        all_x.extend(polygon.x)
        all_y.extend(polygon.y)

    if all_x and all_y:
        x_range = [min(all_x), max(all_x)]
        y_range = [min(all_y), max(all_y)]
        fig.update_xaxes(range=x_range)
        fig.update_yaxes(range=y_range)
        fig.update_layout(
            width=chart_size,
            height=chart_size,
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1
            )
        )
    
    for polygon in lanelet_polygon_list.root:
        if (selected_lane_id and
            (str(selected_lane_id) == str(polygon.lane_id) or
             str(selected_lane_id) == str(polygon.left_bound_id) or
             str(selected_lane_id) == str(polygon.right_bound_id))):
            line_color = "red"
        else:
            line_color = "blue"

        fig.add_trace(
            go.Scattergl(
                x=polygon.x,
                y=polygon.y,
                name=f'id: {polygon.lane_id}',
                fill="toself",
                fillcolor="rgba(135, 206, 235, 0.5)",
                line=dict(color=line_color, width=1),
                showlegend=False,
                mode='lines'
            )
        )
        
    return fig

def handle_dataframe_selection(df, selection):
    """
    DataFrameの選択状態を処理し、セッションステートを更新します。
    """
    if selection["selection"]["rows"]:
        selected_index = selection["selection"]["rows"][0]
        selected_row = df.iloc[selected_index]
        st.session_state.selected_lane_id = selected_row['lane_id']
    else:
        st.session_state.selected_lane_id = None
