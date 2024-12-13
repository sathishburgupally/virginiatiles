from openai import OpenAI
import pandas as pd
import fitz
import requests
from flask import Flask, jsonify, request
import flask
import os
import json
from flask_cors import CORS
df =  pd.read_csv("final3.csv")
df1 = df.copy()
app = Flask(__name__)
CORS(app) 
key  =os.environ.get("OPENAI_API_KEY")

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
    Give me the data in json format of productDescrption:<from data>, FAQs :<from data>
    '''
client =  OpenAI(api_key=key)

@app.route('/generate', methods=['GET'])
def generator(line =None):
    try :
        line = flask.request.args.get('line')
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
if __name__ == "__main__":
    app.run(debug=True)
