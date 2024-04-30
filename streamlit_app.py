import pandas as pd
import streamlit as st
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title="Duplicates Eliminator", layout="wide")
st.title("Duplicates Eliminator")
st.caption("Eliminate duplicates from multiple excel/csv file")
row1 = st.columns([3,7])

dfs = []
with st.sidebar:
    uploaded_files = st.file_uploader("Choose **excel/csv** files", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        try:
            df = pd.read_excel(uploaded_file)
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, low_memory=False)
        df['filename'] = uploaded_file.name
        df['filename'] = df['filename'].str.slice(0, 31)
        dfs.append(df)

def dfs_tabs(df_list, sheet_list, file_name):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')   
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0, index=False)   
    writer.save()
    processed_data = output.getvalue()
    return processed_data

if dfs:
    all_df = pd.concat(dfs)
    with row1[0].container(border=True):
        identifier = st.selectbox("Select identifier",
                          all_df.columns,index=None,
                          placeholder="Select identifier...")
    if identifier!=None:
        with row1[1].container(border=True):
            options = st.radio(
            "How do you want to eliminate the duplicates?",
            ["Determine for each row", "Select from one of the files", "Keep one, eliminate other duplicates"],
            captions = ["Select based on the case", "Best for 2 files upload", "Best for >2 files upload"])
        duplicates = all_df[all_df.duplicated(subset=identifier,keep=False)].sort_values([identifier,'filename'],ascending=True)
        duplicates = duplicates[duplicates[identifier].notna()]
        if len(duplicates)>0 and options=="Determine for each row":
            with st.container(border=True):
                st.write("### Duplicates")
                duplicates['select'] = True
                st.write(len(duplicates[identifier]), " rows, for ", duplicates[identifier].nunique(), " identifier")
                columns_to_move = ['select',identifier,'filename']
                other_columns = [col for col in df.columns if col not in columns_to_move]
                new_columns_order = columns_to_move + other_columns
                duplicates = duplicates[new_columns_order]
                modified_data = st.data_editor(
                    duplicates.reset_index(drop=True)
                    ,column_config={"select": st.column_config.CheckboxColumn("Select Files",help="Select one of the duplicates",default=False)}
                    ,disabled=["widgets"],hide_index=True)

                st.write("### Final Data")
                non_duplicates = all_df[~all_df[identifier].isin(duplicates[identifier].unique())]
                selected_duplicates = modified_data[modified_data['select']==True].drop(columns={'select'})
                final_data = pd.concat([non_duplicates, selected_duplicates])
                if len(final_data[final_data.duplicated(subset=identifier)])>0:
                    st.warning('Duplicates still exist', icon="⚠️")
                st.write(len(final_data[identifier]), " rows, for ", final_data[identifier].nunique(), " identifier")
                st.dataframe(final_data)

                grouped = final_data.groupby('filename')
                final_data_df = {}
                final_data_dfs = []
                sheets = final_data['filename'].unique()
                for group_name, group_df in grouped:
                    final_data_df[group_name] = group_df
                for i in sheets:
                    final_data_dfs.append(final_data_df[i])
                df_xlsx = dfs_tabs(final_data_dfs, sheets, 'multitest.xlsx')
                st.download_button(label='Download Final Data', data=df_xlsx, file_name='final_result.xlsx', type="primary")

        elif len(duplicates)>0 and options=="Select from one of the files":
            with st.container(border=True):
                st.write("### Duplicates")
                st.write(len(duplicates[identifier]), " rows, for ", duplicates[identifier].nunique(), " identifier")
                with st.expander("See duplicated data 👇"):
                    st.dataframe(duplicates.reset_index(drop=True))

                st.write("### Selected data files")
                col1, col2 = st.columns([6,4])
                selected_file = st.selectbox("Which data files you want to keep?", all_df['filename'].unique())
                selected_duplicates = duplicates[duplicates['filename']==selected_file].reset_index(drop=True)
                st.write(len(selected_duplicates[identifier]), " rows, for ", selected_duplicates[identifier].nunique(), " identifier")
                with st.expander("See selected data from duplicates 👇"):
                    st.dataframe(selected_duplicates)

                st.write("### Final Data")
                non_duplicates = all_df[~all_df[identifier].isin(duplicates[identifier].unique())]
                final_data = pd.concat([non_duplicates, selected_duplicates])
                if len(final_data[final_data.duplicated(subset=identifier)])>0:
                    st.warning('Duplicate still exist', icon="⚠️")
                st.write(len(final_data[identifier]), " rows, for ", final_data[identifier].nunique(), " identifier")
                st.dataframe(final_data)

                grouped = final_data.groupby('filename')
                final_data_df = {}
                final_data_dfs = []
                sheets = final_data['filename'].unique()
                for group_name, group_df in grouped:
                    final_data_df[group_name] = group_df
                for i in sheets:
                    final_data_dfs.append(final_data_df[i])
                df_xlsx = dfs_tabs(final_data_dfs, sheets, 'multitest.xlsx')
                st.download_button(label='Download Final Data', data=df_xlsx, file_name='final_result.xlsx', type="primary")

        elif len(duplicates)>0 and options=="Keep one, eliminate other duplicates":
            with st.container(border=True):
                st.write("### Duplicates")
                st.write(len(duplicates[identifier]), " rows, for ", duplicates[identifier].nunique(), " identifier")
                with st.expander("See duplicated data 👇"):
                    st.dataframe(duplicates.reset_index(drop=True))

                st.write("### Final Data")
                final_data = all_df.drop_duplicates(subset=identifier)
                if len(final_data[final_data.duplicated(subset=identifier)])>0:
                    st.warning('Duplicate still exist', icon="⚠️")
                st.write(len(final_data[identifier]), " rows, for ", final_data[identifier].nunique(), " identifier")
                st.dataframe(final_data)

                grouped = final_data.groupby('filename')
                final_data_df = {}
                final_data_dfs = []
                sheets = final_data['filename'].unique()
                for group_name, group_df in grouped:
                    final_data_df[group_name] = group_df
                for i in sheets:
                    final_data_dfs.append(final_data_df[i])
                df_xlsx = dfs_tabs(final_data_dfs, sheets, 'multitest.xlsx')
                st.download_button(label='Download Final Data', data=df_xlsx, file_name='final_result.xlsx', type="primary")               
