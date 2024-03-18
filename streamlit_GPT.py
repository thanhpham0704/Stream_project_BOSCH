import openai
import plotly.express as px
import configparser
import os
import json
import pandas as pd
import streamlit as st
import sqlalchemy as sa  # Support connect to SQL server
import urllib  # Support connect to SQL server
from tqdm import tqdm
import numpy as np
from datetime import date
server = 'SGPSQC01CLU002.apac.bosch.com,56482'
database = 'DB_SOVH_BI_MS_SQL'
tb_name = 'TEST_SENTIMENTAL_ANALYSIS'
schema = 'dbo'
trusted_connection = "yes"
if_exist = 'append'
# Define a function to tranfer data to SQL server
# class PandasToSQL:

#     def __init__(self, server = '' , database = '', schema = '', if_exist = ''):
#         self.server = server
#         self.database = database
#         self.schema = schema
#         self.if_exist = if_exist

#     def chunker(self,seq, size):
#         return (seq[pos:pos + size] for pos in range(0, len(seq), size))

#     def insert_with_progress(self,dataframe,dbTable):
#         conn= urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database)+';Trusted_Connection=yes'
#         engine = sa.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(conn),fast_executemany=True)
#         dataframe = dataframe.convert_dtypes() # auto convert data type of dataframe
#         chunksize = int(len(dataframe) / 1)
#         with tqdm(total=len(dataframe)) as pbar: # load data to SQLserver withprogressing bar
#             for i, cdf in enumerate(self.chunker(dataframe, chunksize)):
#                 replace = self.if_exist if i == 0 else "append"
#                 cdf.to_sql(dbTable, schema=self.schema, con = engine, index=False, if_exists=replace)
#                 pbar.update(chunksize)
#                 tqdm._instances.clear()
# def sql_server_to_df():
#     # Establish a trusted connection to the SQL Server database
#     conn = pyodbc.connect(
#         f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#         f"SERVER={server};"
#         f"DATABASE={database};"
#         f"Trusted_Connection={trusted_connection};"
#     )

#     # Create a cursor for executing SQL queries
#     cursor = conn.cursor()

#     # Define your SQL queries
#     queries = {
#         "query1": f"SELECT * FROM {database}.{schema}.{tb_name}"
#     }

#     # Execute the SQL query
#     query_result = cursor.execute(queries["query1"])

#     # Fetch all rows from the result set
#     rows = query_result.fetchall()

#     # Get column names from the cursor description
#     columns = [column[0] for column in cursor.description]

#     return pd.DataFrame(np.array(rows), columns=columns)


def bar(df, yvalue, xvalue, text, title, y_title, x_title, color=None, discrete_sequence=None, map=None):
    fig = px.bar(df, y=yvalue,
                 x=xvalue, text=text, color=color, color_discrete_sequence=discrete_sequence, color_discrete_map=map)
    fig.update_layout(
        title=title,
        yaxis_title=y_title,
        xaxis_title=x_title)
    fig.update_layout(font=dict(size=17), xaxis={
        'categoryorder': 'total descending'})
    return fig


st.title("What do you think about your company?")
st.subheader("AI-powered sentimental analysis of DSBI team")
st.warning('Developed by Thanh Pham, API key provided by DC_MKT', icon="😉")


score = st.slider('Rate how you feel today from 0 to 10', 0, 10, 0)

text = st.text_input('Please write your feedback')
if st.button('Submit'):
    # Add your logic for handling the submission here
    st.success('Unleashing the power of AI. Get ready for the result!')

    # Load API key from config.ini
    config = configparser.ConfigParser()
    config.read('config_sentimental.ini')

    openai.api_type = "azure"
    openai.api_base = "https://openai-sentiment-vietnam.openai.azure.com/"
    openai.api_version = "2023-07-01-preview"
    openai.api_key = config.get('OpenAI', 'api_key')
    prompt = f"""
    You are an experience HR manager who has high EQ and care for the employee's wellbeing. You specialized in analyzing employees' feedback.
    Please extract relevant aspects from the input text and format output in JSON. Use the given examples to learn the format and analysis.
    In addition to the text, the sentimental score (STM) of the feedback is given. This STM is a scale from 0-10, which is used to classify employees. 0 to 6 are detractors, 7 to 8 are passive employees, 9 to 10 are promoters. 
    Use this STM scale as an indicator if the sentiment is not clearly visible. After analyzing the text, please infer the new sentimental score (NSTM) for the feedback.

    Examples:              
    STM: 3, Feedback: There has been a consistent lack of attention to project deadlines, impacting team deliverables. It's crucial to prioritize tasks and manage time effectively to meet project milestones                            
    [                
    {{"aspect":"Project Management", "segment":"Lack of attention to project deadlines", "attribute":"Lack of attention", "sentiment":"Negative", "NSTM":"2"}},                
    {{"aspect":"Team Collaboration", "segment":"Impacting team deliverables", "attribute":"Impacting", "sentiment":"Negative", "NSTM":"1"}}, 
    {{"aspect":"Time Management", "segment":"Crucial to prioritize tasks and manage time effectively", "attribute":"Crucial", "sentiment":"Suggestive", "NSTM":"5"}},                            
    ]

    STM: 7, Feedback: The technical skills are solid, but there's room for improvement in communication within the team. Consider being more proactive in sharing updates and collaborating with colleagues to enhance overall project efficiency.
    [
    {{"aspect":"Technical Skills", "segment":"Technical skills are solid", "attribute":"Solid", "sentiment":"Positive", "NSTM":"9"}},      
    {{"aspect":"Communication", "segment":"Room for improvement in communication within the team", "attribute":"Improvement needed", "sentiment":"Suggestive", "NSTM":"5"}},  
    {{"aspect":"Collaboration", "segment":"Consider being more proactive in sharing updates and collaborating", "attribute":"Proactive", "sentiment":"Suggestive", "NSTM":"5"}}
    ]
    STM: 10, Feedback: Your commitment to quality in code development has significantly contributed to the success of recent software releases. The attention to detail and thorough testing have been instrumental in delivering robust solutions to our clients.
    [
    {{"aspect":"Code Development", "segment":"Commitment to quality in code development", "attribute":"Commitment", "sentiment":"Positive", "NSTM":"8"}},      
    {{"aspect":"Attention to Detail", "segment":"Attention to detail", "attribute":"Detail-oriented", "sentiment":"Positive", "NSTM":"8"}},  
    {{"aspect":"Testing", "segment":"Thorough testing", "attribute":"Thorough", "sentiment":"Positive", "NSTM":"8"}},
    {{"aspect":"Project Success", "segment":"Contributed to the success of recent software releases", "attribute":"Contributed", "sentiment":"Positive", "NSTM":"8"}},
    {{"aspect":"Client Satisfaction", "segment":"Delivering robust solutions to clients", "attribute":"Robust", "sentiment":"Positive", "NSTM":"8"}}
    ]

    STM: 2, Feedback: There's been a noticeable decline in participation during team meetings. Active engagement is crucial for the exchange of ideas and information sharing. Please make an effort to contribute more actively and stay involved in discussions
    [
    {{"aspect":"Team Participation", "segment":"Noticeable decline in participation during team meetings", "attribute":"Decline", "sentiment":"Negative", "NSTM":"1"}},                
    {{"aspect":"Active Engagement", "segment":"Active engagement is crucial for the exchange of ideas and information sharing", "attribute":"Crucial", "sentiment":"Suggestive", "NSTM":"5"}}, 
    {{"aspect":"Contribution", "segment":"Make an effort to contribute more actively", "attribute":"Effort needed", "sentiment":"Suggestive", "NSTM":"5"}},
    {{"aspect":"Involvement", "segment":"Stay involved in discussions", "attribute":"Stay involved", "sentiment":"Suggestvive", "NSTM":"8"}}
    ]
    STM: 7, Feedback: The team is doing great, everyone is willing to help each other. However, there are a few members who are toxic and talk behind people'back. Technical skills of team members are enough for the tasks. There should be more team engagement activities
    [
    {{"aspect":"Team Collaboration", "segment":"Everyone is willing to help each other", "attribute":"Willing to help", "sentiment":"Positive", "NSTM":10"}},
    {{"aspect":"Toxicity", "segment":"Few members who are toxic and talk behind people's back", "attribute":"Toxic behavior", "sentiment":"Negative", "NSTM":"0"}},
    {{"aspect":"Technical Skills", "segment":"Technical skills of team members are enough for the tasks", "attribute":"Enough skills", "sentiment":"Neutral", "NSTM":"6"}},
    {{"aspect":"Team Engagement", "segment":"More team engagement activities needed", "attribute":"More activities needed", "sentiment":"Suggestive", "NSTM":"5"}},
    ]
    STM: 5, Feedback: Generally, Working at BOSCH has pros and cons. The company offers great incentives for self-learning. People are willing to share and grow together.The working space is nothing special. The monitors are a bit outdated. The monitors are a bit outdated. I recommend replacing old ones with IMac monitors
    [
    {{"aspect":"Company Culture", "segment":"Working at BOSCH has pros and cons", "attribute":"Mixed experience", "sentiment":"Neutral", "NSTM":"5"}},
    {{"aspect":"Self-Learning", "segment":"Great incentives for self-learning", "attribute":"Great incentives", "sentiment":"Positive", "NSTM":"9"}},
    {{"aspect":"Team Collaboration", "segment":"People are willing to share and grow together", "attribute":"Willing to share", "sentiment":"Positive", "NSTM":"9"}},
    {{"aspect":"Working Space", "segment":"Working space is nothing special", "attribute":"Nothing special", "sentiment":"Neutral", "NSTM":"4"}},
    {{"aspect":"Equipment", "segment":"Monitors are a bit outdated", "attribute":"Outdated monitors", "sentiment":"Negative", "NSTM":"2"}},
    {{"aspect":"Equipment", "segment":"Recommend replacing old ones with IMac monitors", "attribute":"Recommendation", "sentiment":"Suggestive", "NSTM":"5"}}
    ]


    Input:
    {{"STM: {score}, Feedback: {text}"}}

    """

    prompt2 = "who is the president of Vietnam"

    message_text = [{"role": "system", "content": "You are an AI assistant that helps people find information."},
                    {"role": "user", "content": prompt}]

    completion = openai.ChatCompletion.create(
        engine="gpt-vietnam",
        messages=message_text,
        temperature=0,
        max_tokens=2000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    # print(completion["choices"][0]["message"]["content"])

    df = pd.DataFrame(json.loads(
        completion["choices"][0]["message"]["content"]))
    # Specify the file path
    file_path = "sentimental_data.csv"
    # Append new values to the csv file
    df.to_csv(file_path, mode = 'a', header=False, index=False)

    st.write("Your feedback")
    st.dataframe(df, use_container_width=True)

    try:
        df_csv = pd.read_csv(file_path, sep= ',', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df_csv = pd.read_csv(file_path, sep= ',', encoding='utf-8-sig')
        except UnicodeDecodeError:
            try:
                df_csv = pd.read_csv(file_path, sep= ',', encoding='latin-1')
            except UnicodeDecodeError:
                df_csv = pd.read_csv(file_path, sep= ',', encoding='ISO-8859-1')
    # # df_csv['date_created'] = pd.Timestamp(date.today()).date()
    st.write("Accumulative feedback")
    st.dataframe(df_csv, use_container_width=True)



    df_csv_group_sentiment = df_csv.groupby("sentiment", as_index = False).size()
    df_csv_group_aspect = df_csv.groupby("aspect", as_index = False).size()
    df_csv_group_attribute = df_csv.groupby("attribute", as_index = False).size()




    fig1 = bar(df_csv_group_sentiment, yvalue='size',
               xvalue='sentiment', text=df_csv_group_sentiment["size"], title='Total count by Sentiment', x_title='Sentiment', y_title='Total Count')
    fig1.update_traces(
        hovertemplate="Total count: %{y:,.0f}<extra></extra>")
    fig2 = bar(df_csv_group_aspect, yvalue='aspect',
               xvalue='size', text=df_csv_group_aspect["size"], title='Total count by Aspect', x_title='Total Count', y_title='Aspect')
    fig2.update_traces(
        hovertemplate="Total count: %{x:,.0f}<extra></extra>")
    fig3 = bar(df_csv_group_attribute, yvalue='attribute',
               xvalue='size', text=df_csv_group_attribute["size"], title='Total count by Attribute', x_title='Total Count', y_title='Attribute')
    fig3.update_traces(
        hovertemplate="Total count: %{x:,.0f}<extra></extra>")
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)
