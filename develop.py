import streamlit as st
import pandas as pd
import sqlalchemy as sa # Support connect to SQL server
import urllib # Support connect to SQL server
import time




page_title = "Input Web Demo "
page_icon = "👦🏻"
layout = "wide"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
# st.title(page_title + " " + page_icon)

server = 'SGPSQC01CLU002.apac.bosch.com,56482'
database = 'DB_SOVH_BI_MS_SQL'
tb_name = 'TEST_DIM_LOCATION_SUPPLEMENT'
schema = 'dbo'
if_exist = 'replace'


class PandasToSQL:

    def __init__(self, server = '' , database = '', schema = '', if_exist = ''):
        self.server = server
        self.database = database
        self.schema = schema
        self.if_exist = if_exist
        
    def chunker(self,seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def insert_with_progress(self,dataframe,dbTable):
        conn= urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database)+';Trusted_Connection=yes'
        engine = sa.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(conn),fast_executemany=True)
        dataframe = dataframe.convert_dtypes() # auto convert data type of dataframe
        chunksize = int(len(dataframe) / 1) 

        my_bar = st.progress(0, text='progress bar')
        for i, cdf in enumerate(self.chunker(dataframe, chunksize)):
            replace = self.if_exist if i == 0 else "append"
            cdf.to_sql(dbTable, schema=self.schema, con = engine, index=False, if_exists=replace)
            time.sleep(0.1)
            my_bar.progress((i + 1)/ chunksize, text='progress bar')
        my_bar.progress(100)
    

# Streamlit UI
def main():
    st.title('Excel to Database Uploader 😸')
    uploaded_file = st.file_uploader('Upload Excel File', type=['xlsx'])
    if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            st.write('Preview of the uploaded data:')
            st.dataframe(df)
            if st.button('Upload to Database'):
                # SQL server metadata
                server = 'SGPSQC01CLU002.apac.bosch.com,56482'
                database = 'DB_SOVH_BI_MS_SQL'
                tb_name = 'TEST_STREAMLIT'
                schema = 'dbo'
                if_exist = 'replace'
              
                PandasToSQL(server,database,schema,if_exist).insert_with_progress(df,tb_name)

                st.write(f'Successfully import :red[{df.shape[0]}] rows to :red[{database}] with table name as :red[{tb_name}]')
if __name__ == '__main__':
    main()


# progress_text = "Operation in progress. Please wait."
# my_bar = st.progress(0, text=progress_text)

# for percent_complete in range(100):
#     time.sleep(0.1)
#     my_bar.progress(percent_complete + 1, text=progress_text)
