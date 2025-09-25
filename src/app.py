import streamlit as st
import os
import shutil
import re
import pandas as pd
import subprocess
from run_script import run_validator
from models.validation_results import ValidationResults
from services import load_and_merge_data, create_plotly_figure

# --- ディレクトリ設定 (変更なし) ---
base = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(base, "uploaded_files")
SCRIPT_OUTPUT_BASE_DIR = os.path.join(base, "script_temp_output")
CHART_SIZE = 1800

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(SCRIPT_OUTPUT_BASE_DIR):
    os.makedirs(SCRIPT_OUTPUT_BASE_DIR)

st.set_page_config(layout="wide")
st.title("OSMファイル検証アプリ")
st.markdown("`.osm` ファイルをアップロードして、**Autoware.Universeのlanelet2_map_validator** を実行し、結果を表示します。")

# --- セッションステートの初期化 ---
if 'selected_lane_id' not in st.session_state:
    st.session_state.selected_lane_id = None
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None


def run_app_logic():
    """
    ファイルがアップロードされた後の全てのロジックを処理
    """
    file_path_on_server = st.session_state.uploaded_file_path
    
    # 既存の出力ディレクトリを削除
    if os.path.exists(SCRIPT_OUTPUT_BASE_DIR):
        shutil.rmtree(SCRIPT_OUTPUT_BASE_DIR)
    os.makedirs(SCRIPT_OUTPUT_BASE_DIR)
    
    st.markdown("---")
    st.header("2. 検証スクリプトの実行")
    st.markdown(f'file: {file_path_on_server}')
    
    with st.spinner("検証スクリプトを実行中...しばらくお待ちください。"):
        try:
            validation_results: ValidationResults = run_validator(
                file_path_on_server, SCRIPT_OUTPUT_BASE_DIR
            )
            st.success("検証スクリプトが正常に実行され、結果が取得されました。")
            
            st.markdown("---")
            st.header("3. 検証結果")
            
            # === ロジック層を呼び出してDataFrameを生成 ===
            st.session_state.df = load_and_merge_data(validation_results)
            
            st.subheader("検証結果詳細")
            
            column_order = [
                "status", "Category", "requirement_id", "Requirement", "URL",
                "validator_name", "issue_code", "message", "primitive", "lane_id"
            ]
            
            column_config = {
                "URL": st.column_config.LinkColumn(
                    "URL",
                    help="リンクされた要件ページに移動",
                    display_text="🔗 Link",
                ),
            }

            selected = st.dataframe(
                st.session_state.df,
                on_select='rerun',
                selection_mode="single-row",
                hide_index=True,
                column_order=column_order,
                column_config=column_config
            )
            
            st.session_state.selected_lane_id = None
            if selected["selection"]["rows"]:
                selected_index = selected["selection"]["rows"][0]
                selected_row = st.session_state.df.iloc[selected_index]
                result = re.search((r' +(\d+) +'), str(selected_row['message']))
                st.session_state.selected_lane_id = result.group(1) if result else None
                if st.session_state.selected_lane_id is None and selected_row['lane_id'] is not None:
                    st.session_state.selected_lane_id = str(selected_row['lane_id'])
            # === ロジック層を呼び出してPlotlyグラフを生成 ===
            id_str = st.session_state.selected_lane_id if st.session_state.selected_lane_id else "なし"
            st.write( f"選択された lane_id: {id_str}" )
            st.subheader("Lanelet2 Map")
            fig = create_plotly_figure(
                file_path_on_server, st.session_state.selected_lane_id, CHART_SIZE
            )
            st.plotly_chart(fig)
            
        except subprocess.CalledProcessError as e:
            st.error("検証スクリプトの実行中にエラーが発生しました。")
            st.error(f"終了コード: {e.returncode}")
            if e.stdout:
                st.code(f"スクリプトの標準出力:\n{e.stdout}", language='text')
            if e.stderr:
                st.code(f"スクリプトの標準エラー出力:\n{e.stderr}", language='text')
        except FileNotFoundError:
            st.error("エラー: 必要なファイルが見つかりません。パスを確認してください。")
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {e}")

    st.markdown("---")
    if st.button("アップロードファイルを削除", key="delete_uploaded_file"):
        try:
            # UPLOAD_DIR内のファイルを再帰的に削除
            if os.path.exists(UPLOAD_DIR):
                shutil.rmtree(UPLOAD_DIR)
            os.makedirs(UPLOAD_DIR)
            
            st.success(f"アップロードされたファイルを全て削除しました。")
            st.session_state.uploaded_file_path = None
            st.rerun()
        except OSError as e:
            st.error(f"ファイルの削除に失敗しました: {e}")

# --- メインロジック ---
uploaded_file = st.file_uploader(
    "検証したい `.osm` ファイルを選択してください",
    type=["osm"],
    accept_multiple_files=False
)

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_path_on_server = os.path.join(UPLOAD_DIR, file_name)

    if st.session_state.uploaded_file_path != file_path_on_server:
        # 既存のファイルを再帰的に削除
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR)
        
        with open(file_path_on_server, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"ファイル '{file_name}' をアップロードしました。")
        st.session_state.uploaded_file_path = file_path_on_server
        st.rerun()

if st.session_state.uploaded_file_path:
    run_app_logic()
