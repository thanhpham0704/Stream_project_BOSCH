import openai
import configparser
import os

proxy_server = 'http://rb-proxy-de.bosch.com:8080'
os.environ['http_proxy'] = proxy_server
# Set the https_proxy environment variable
os.environ['https_proxy'] = proxy_server
print(os.environ['http_proxy'])
print(os.environ['https_proxy'])

# Load API key from config.ini
config = configparser.ConfigParser()
config.read(r'C:\Users\HPT7HC\Desktop\Sentimental_analysis\config_sentimental.ini')

openai.api_type = "azure"
openai.api_base = "https://openai-sentiment-vietnam.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = config.get('OpenAI', 'api_key')

prompt = f"""

Your are a customer experience employee, specialized in analysis of customer feedback.
Please extract relevant aspects from the input text and format output in JSON. Use the given examples to learn the format and analysis.
In addition to the text, the NPS score of the feedback is given. This is a scale from 0-10, which is used to classify customers. 0 to 6 are detractors, 7 to 8 are passive customers, 9 to 10 are promoters. 
Use this scale as an indicator if the sentiment is not clearly visible. 

Examples:              
NPS: 10, Feedback: Good quality of its components and after-sales service is very well qualified as well as committed to the service and the customer to make the implemented solution work 100%.                             
[                
{{"aspect":"product quality", "segment":"Good quality of its components", "attribute":"good", "sentiment":"positive"}},                
{{"aspect":"customer support", "segment":"after-sales service is very well qualified", "attribute":"qualification", "sentiment":"positive"}}, 
{{"aspect":"customer support", "segment":"after-sales service is very well qualified", "attribute":"knowledge", "sentiment":"positive"}}, 
{{"aspect":"customer support", "segment":"after-sales service is very well qualified as well as committed", "attribute":"commitment", "sentiment":"positive"}}                               
]

NPS: 6, Feedback: unstable product quality, slow feedback, shirk responsibility.
[
{{"aspect":"product quality", "segment":"unstable product quality", "attribute":"unstable", "sentiment":"negative"}},      
{{"aspect":"customer support", "segment":"slow feedback", "attribute":"slow", "sentiment":"negative"}},  
{{"aspect":"attitude", "segment":"shirk responsibility", "attribute":"responsibility", "sentiment":"negative"}}
]

NPS: 8, Feedback: sometimes there is a lot of bureaucracy and the prices are a bit high. excellent quality.
[
{{"aspect":"process", "segment":"sometimes there is a lot of bureaucracy", "attribute":"bureaucratic", "sentiment":"negative"}},      
{{"aspect":"price", "segment":"the prices are a bit high", "attribute":"high", "sentiment":"negative"}},  
{{"aspect":"product quality", "segment":"excellent quality", "attribute":"excellent", "sentiment":"positive"}}
]

NPS: 8, Feedback: great communication, willingness, reliability, professionality
[
{{"aspect":"communication", "segment":"great communication ", "attribute":"great", "sentiment":"positive"}},                
{{"aspect":"willingness", "segment":"great communication, willingness", "attribute":"great", "sentiment":"positive"}}, 
{{"aspect":"reliability", "segment":"great communication, willingness, reliability", "attribute":"great", "sentiment":"positive"}}, 
{{"aspect":"professionality", "segment":"great communication, willingness, reliability, professionality", "attribute":"great", "sentiment":"positive"}}  
]

NPS: 4, Feedback: quality and delivery lead time
[
{{"aspect":"product quality", "segment":"quality ", "attribute":"bad", "sentiment":"negative"}},                
{{"aspect":"delivery", "segment":"delivery lead time", "attribute":"bad", "sentiment":"negative"}}, 
]

Input:
{"NPS: 7, Feedback: I like how fast the delivery is, but hate the person who sale it to me"}
"""

prompt2 = "who is the president of Vietnam"

message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},\
                {"role":"user","content":prompt2}]

completion = openai.ChatCompletion.create(
  engine="gpt-vietnam",
  messages = message_text,
  temperature=0,
  max_tokens=1500,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None
)

# print(completion)

print(completion["choices"][0]["message"]["content"])
