# Import necessary modules and libraries
from flask import Flask, render_template, request, redirect
from textblob import TextBlob
from textblob import TextBlob
from googletrans import Translator
from spellchecker import SpellChecker
from twilio.rest import Client
from deep_translator import GoogleTranslator
import facebook
import enchant
import openai

# Initialize Flask
app = Flask(__name__)
translator = Translator()
spell = SpellChecker()

# Set up OpenAI API credentials
openai.api_key = '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'

# Configure WhatsApp API credentials
account_sid = 'AC1903156721faceb9839e694af69b0863'
auth_token = '5d052178039fb5898995704cbff3ca41'
client = Client(account_sid, auth_token)

# Configure Facebook API credentials
#access_token = '668468751285601|joV1vayxOmZCnu8lLGXgASwn7Qk'
print("here")
#graph = facebook.GraphAPI(access_token)

#print(graph)
whatsapp_messages = []
chatgpt_messages = []

@app.route('/')
def home():
    # Fetch WhatsApp and Facebook messages
    whatsapp_messages = fetch_whatsapp_messages()
   # chatgpt_messages = fetch_chatgpt_messages()
    #facebook_messages = fetch_facebook_messages()

    #return render_template('index.html', whatsapp_messages=whatsapp_messages, facebook_messages=facebook_messages)
    return render_template('index.html', whatsapp_messages=whatsapp_messages, chatgpt_messages=chatgpt_messages)

@app.route('/reply', methods=['POST'])
def reply_message():
    recipient_id = request.form['recipient_id']
    message = request.form['message']
    print(message)
    print(recipient_id)
    # Determine if the recipient ID corresponds to WhatsApp or Facebook user
    if recipient_id.startswith('whatsapp:'):
        send_whatsapp_message(recipient_id, message)
    else:
        #send_facebook_message(recipient_id, message)
         print("no hwtas")
    return redirect('/')

def fetch_whatsapp_messages():
    # Use Twilio API to fetch WhatsApp messages
    messages = client.messages.list(limit=100)

    # Process and extract relevant information from the messages
    #whatsapp_messages = []
    for message in messages:
        body = proces_query(message.body)
        whatsapp_messages.append({
            'sender': message.from_,
            'body': body
        })
            
    
    return whatsapp_messages

#def fetch_facebook_messages():
    # Use Facebook Graph API to fetch Facebook messages
#    messages = graph.get_connections('me', 'inbox', fields='id,participants,messages')

    # Process and extract relevant information from the messages
    #facebook_messages = []
    #for message in messages['data']:
    #    participants = message['participants']['data']
    #    sender_name = participants[0]['name']  # Assuming only one participant
    #    sender_id = participants[0]['id']
    #    last_message = message['messages']['data'][0]['message']
        
    #    facebook_messages.append({
    #        'sender': sender_name,
    #        'sender_id': sender_id,
    #        'body': last_message
    #    })

    #return facebook_messages

def send_whatsapp_message(recipient_id, message):
    # Use Twilio API to send a WhatsApp message
    from_whatsapp_number = 'whatsapp:+14155238886'

# The WhatsApp number to send the voice message to
    to_whatsapp_number = 'whatsapp:+919176000532' 
    try:
    # Upload the voice recording file to Twilio Programmable Storage
     media = client \
        .messages \
        .create(
            body=message,
            from_=from_whatsapp_number,            
            to=recipient_id
        )

     print('Voice message sent:', media.sid)

    except TwilioException as e:
           print('Twilio Error:', e)

#def send_facebook_message(recipient_id, message):
    # Use Facebook Graph API to send a Facebook message
    #graph.put_object(parent_object=recipient_id, connection_name='messages', message=message)

@app.route('/process', methods=['POST'])
def process_message():
    message = request.form['message']
    
    # Store the WhatsApp message
    whatsapp_messages.append(message)
    
    print(message)
    # Generate a response using ChatGPT
    response = generate_chatgpt_response(message)
    print(response)
    # Store the ChatGPT response
    chatgpt_messages.append(response)
    
    return response

def proces_query(query):
    #query = request.form['query']
    
    # Translate message to English
    translated_query = translate_to_english(query)
    
    # Correct spelling mistakes
    corrected_query = correct_spelling(translated_query)
    
    return str(corrected_query)
    #return render_template('index.html', query=query, translated_query=translated_query, corrected_query=corrected_query)

def translate_to_english(query):
    translated_text = GoogleTranslator(source='auto', target='en').translate(query)
    return translated_text

def correct_spelling(query):
    words = query.split()
    corrected_words = []
    for word in words:
        corrected_word = spell.correction(word)
        if corrected_word is not None:
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
    corrected_text = ' '.join(corrected_words)
    return corrected_text





def generate_chatgpt_response(message):
    # Make a request to ChatGPT using OpenAI API
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=message,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=None,
       # frequency_penalty=None
    )
    
    return response.choices[0].text.strip()

if __name__ == '__main__':
    app.run()
