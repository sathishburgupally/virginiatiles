from openai import OpenAI

import pandas as pd
import fitz
import requests
from flask import Flask, jsonify, request
import flask
import json
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app) 
df =  pd.read_csv("final3.csv")
df1 = df.copy()
api_key = '2e6c47ed-886e-4293-849c-ebbd192da1da' #zerogpt
key  = os.environ.get('OPENAI_API_KEY')

template  = '''
    You are Virginia Tile Assistant, an AI trained to generate helpful FAQs and product description for Virginia Tile products. Your task is to create a concise set of FAQs for a given product deatils based on its unique specifications, installation instructions, maintenance recommendations, and intended applications.

    Example FAQs for a Tile Product
    Q1: What are the recommended applications for this tile?
    A1: This tile can be used in various settings, including [bathrooms, kitchens, floors, walls, pools, outdoor spaces, or high-traffic areas], depending on its slip resistance, durability, and finish.

    Q2: Is this tile suitable for wet or high-moisture areas?
    A2: Yes, tiles with a low water absorption rate and high DCOF (Dynamic Coefficient of Friction) are suitable for wet areas like bathrooms, showers, and kitchens. For polished tiles, sealing may be recommended.

    Q3: Does this tile require sealing?
    A3: Sealing requirements depend on the tile’s finish. Polished or crackle-glazed tiles typically benefit from sealing to protect against stains, especially in high-moisture areas.

    Q4: Can this tile be installed over existing surfaces?
    A4: Yes, if the existing surface is clean, stable, and free of cracks or damage. Proper preparation and consultation with a professional installer are recommended.

    Q5: How should I clean and maintain this tile?
    A5: Most tiles can be maintained with a pH-neutral cleaner and a soft cloth or mop. Avoid harsh chemicals or abrasive tools that could damage the surface.

    Q6: What adhesive and grout types are recommended for installation?
    A6: A high-quality thin-set mortar is generally recommended for installation, with epoxy or color-matched grout depending on the tile's color and intended use.

    Q7: Is this tile available with matching trims or mosaics?
    A7: Many tiles have coordinating trims, borders, or mosaics to achieve a cohesive look, especially for installations requiring edge finishing.

    Q8: What is the PEI rating, and why is it important?
    A8: The PEI (Porcelain Enamel Institute) rating measures the tile’s durability. Tiles with a PEI rating of 3 or higher are suitable for floors and high-traffic areas, while lower ratings are better suited for walls.

    Q9: Can this tile be used with underfloor heating systems?
    A9: Yes, many tiles are compatible with radiant heating systems, but check specific product guidelines to ensure optimal performance.

    Q10: Is this tile eco-friendly?
    A10: Some tiles are manufactured using sustainable practices and materials, meeting certifications like Greenguard for low chemical emissions, making them an environmentally friendly choice.

    for generating FAQ's follow the structure
    product name : <take from data>

    product description (Description should be lessthan 160 characters):
    --Description here--
    
    
    as follow as FAQ's

    Instructions for Virginia Tile Assistant:

    Focus on the single product’s specific details (such as finish, PEI rating, DCOF, water absorption, eco-certifications, and recommended applications).
    Generate 6-10 concise FAQs that address common customer concerns about this product’s features, maintenance, and installation.
    Ensure each FAQ provides clear, relevant information that helps customers understand the product’s unique benefits and limitations.
    Keep the responses short and practical, tailored specifically to the tile’s individual specifications for easy customer reference.
    
     *Things to remember:*
    generate the FAQs by extracting theme from the sample FAQs
    Don't haloginate apart from the given data
    Give me the data in json formate of productDescrption:<from data>, FAQs :<from data>
    '''
client =  OpenAI(api_key=key)
actul_token = "vamsiswaroopadvaitlabschanakya"
@app.route('/generate', methods=['POST'])
def generator(line =None,token=None):
    try :
        data = flask.request.get_json()
        line  = data.get('line')
        token = data.get('token')
        if token ==None:
            return jsonify({
                'response' : 'No token found' })
        if token!=actul_token :
            return jsonify({'response':'Please provide valid token'})
        
        if line in df1["product-lines"].to_list():
            link  = df1["product_line_literature"][df1["product-lines"]==line]
        else :
            return jsonify({
                'response' :"Sorry No product line found"
            })

        text = ''
        response  =requests.get(link.values[0]).content
        pdf =  fitz.open(stream=response, filetype="pdf")
        for i in pdf:
            text+=i.get_text()
        model = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": template},
            {"role": "assistant", "content": '\n\nproduct detail'+"\n\n\n"+text}
        ],
        temperature=0,
        presence_penalty=0,
        frequency_penalty=0,
    
        )   
        res  = model.choices[0].message.content
        # print(res)
        return jsonify(json.loads(res))
    except :
        jsonify({

            'response' : 'An error occured please try again later'
        })

@app.route("/aiscore",methods=["POST"])    
def Aiscore(text =None):
    data =  flask.request.get_json()
    # print(data)
    text = data.get('faqs')
    # print(text)
    if not text:
        return jsonify({'response':'No FAQs found'})
    else :
         # zerGPT
        try :
            url = "https://api.zerogpt.com/api/detect/detectText"
            headers = {
            "ApiKey": api_key,
            "Content-Type": "application/json"
        }
            data = { "input_text": text}

            response = requests.post(url, headers=headers, json=data)
            return jsonify({'Fake percentage':response.json()})
        except :
            return jsonify({"response":"An error occured please contact developer"})

@app.route('/grammarCheck', methods=['POST'])
def grammar_check():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Ensure 'string' is provided in the request body
        text = data.get('string')
        if not text:
            return jsonify({'response': 'No text provided for grammar check'}), 400

        # Define API URL and headers
        url = "https://api.zerogpt.com/api/transform/grammarCheck"
        headers = {
            "Content-Type": "application/json",
            "ApiKey": api_key,
        }

        # Define the payload with only the 'string' field
        payload = {
            "string": text
        }

        # Make the POST request to ZeroGPT API
        response = requests.post(url, headers=headers, json=payload)

        # Check if the response is successful
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'response': f'Error from ZeroGPT API: {response.status_code}'}), 500

    except Exception as e:
        # Log the error and return a message
        print(f"Error: {e}")
        return jsonify({'response': 'An error occurred. Please try again later.'}), 500

@app.route('/plagarisim',methods=["POST"])
def plagarisim():
    data =  flask.request.get_json()
    text  = data.get('data')
    url = "https://api.zerogpt.com/api/detect/textPlagiarism"
    headers = {
    "ApiKey": api_key,
    "Content-Type": "application/json"}
    data = { "input_text": text}
    response = requests.post(url, headers=headers, json=data)
    return jsonify(response.json())

@app.route('/humanize',methods = ["POST"])
def humanize():
    data  = flask.request.get_json()
    text = data.get('data')
    # print(request.headers)
    prompt ='''
As a human assistant named Swaroop, your main task is to thoroughly review and rephrase the provided sentences. Make essential adjustments to ensure they are written in a way that bypasses detection by ZEROGPT or any similar tools designed to identify machine-generated content. When rewriting FAQs, focus on maintaining low perplexity and high burstiness to improve readability and engagement.
'''
    if not text:
        return jsonify({"response" : 'No FAQs found to humanize'})
    else :
        try :
            response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": prompt
        }
      ]
    },{
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": text
        }
      ]
    }

  ],
    response_format={
    "type": "text"
    },
    temperature=0.1,
    max_completion_tokens=989,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
            return jsonify({'FAQS':response.choices[0].message.content})
        except Exception as e:
            # Log the error and return a message
            print(f"Error: {e}")
            return jsonify({'response': 'An error occurred. Please try again later.'}), 500
                
    

@app.errorhandler(404)
def errorhandle(e):

    return jsonify({
        'Response ':'NO webpage found on this path please contact developer'
    })



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8000)