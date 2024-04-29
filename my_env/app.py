from flask import Flask, render_template, request
from flask import jsonify
import requests
from dotenv import load_dotenv
import os
import re
# import model  # Import your trained model

app = Flask(__name__)

def generate_response(user_query, topic):
  """
  This function will be replaced with your actual model logic in the future.
  For now, it returns a dummy response.
  """
  # send post request to the rag model flask server with user_query and topic
  # get the response from the rag model server and return it
  load_dotenv()
  rag_server_url = os.getenv('SERVER_URL')  # Get the server URL from the environment variables

  response = requests.post(rag_server_url + '/chatbot', json={"query": user_query, "topic": topic})
  if response:
      response_json = response.json()
      if 'answer' in response_json:
          answer = response_json['answer']
          answer = re.sub(r'\*\*+', "", answer)
          answer = re.sub(r'\*', "🔸", answer)
          answer = re.sub(r'-(?=\s)', "🔸", answer)
          # context_items = response_json.get('context_items', [])
          if ('so I cannot answer this question from the provided context.' in answer) or (('The context does not mention any information' or 'The context items do not provide' or 'The context does not') in answer):
             answer += '\n\n 📔 Note: Sometimes I am unable to answer the question as I am still learning and improving. Please provide more context or rephrase the question.'
          return answer
      else:
          default_answer = "Sorry, I am unable to generate a response at this moment."
          return default_answer
  else:
      error_message = "There was an error connecting to the chatbot. Please try again later."
      return error_message
  # if(user_query == "hello"):
  #    return "Hello! How can I help you today?"
  # elif(user_query.lower() == "what is ngdr?"):
  #    return "National Geoscience Data Repository (NGDR) is a flagship initiative conceptualised by Ministry of Mines as a part of National Mineral Exploration Policy (NMEP), 2016 for hosting all exploration related geoscientific data for dissemination to all the stakeholders so as to expedite, enhance and facilitate the exploration coverage of the country. Geological Survey of India is selected as the nodal agency for the implementation of NGDR. All legacy data of all stakeholders will be brought in to the system through digitization and all the exploration related data has been standardized through MERT (Mineral Exploration Reporting Template) and converted into GIS compatible formats for application of emerging technologies like AI and ML."
  # return "Thanks for your query! I'm still under development and learning to communicate effectively. Stay tuned for future updates!"


@app.route("/")
def home():
  return render_template("index.html")
import plotly.graph_objects as go

def generate_ngdr_map():
  # Create a map figure
  fig = go.Figure(data=go.Scattergeo())

  # Set the layout of the map
  fig.update_layout(
    title_text="My Map",
    showlegend=False,
    geo=dict(
      resolution=50,
      showland=True,
      showlakes=True,
      landcolor="rgb(204, 204, 204)",
      countrycolor="rgb(204, 204, 204)",
      lakecolor="rgb(255, 255, 255)",
      projection_type="equirectangular",
      coastlinewidth=1,
      lataxis=dict(range=[-90, 90]),
      lonaxis=dict(range=[-180, 180])
    )
  )

  # Convert the map figure to HTML
  # map_html = fig.to_html(full_html=False)
  print(fig)
  data = fig.to_dict() 
  layout = fig.to_dict()
  return data, layout


@app.route("/get_response_ngdr", methods=["POST"])
def ngdr_geochem_response():
    user_query = request.json["query"]
    # send this user_query to the ngdr main function then get the response and return it by jsonify after making it to a dictionary
    
    # response = generate_geochemistry_response(user_query) # the response should already be jsonified
    # return response
    data, layout = generate_ngdr_map()
    return jsonify(data=data, layout=layout)


# @app.route("/get_response", methods=["POST"])
# def get_response():
#   user_query = request.form["query"]
#   # response = model.generate_response(user_query)  # Call your model function
#   response = generate_response(user_query)  # Call your model function

#   return jsonify({"response": response})
@app.route("/get_response_rag", methods=["POST"])
def get_response():
    user_query = request.json["query"]
    topic = request.json["topic"]
    response = generate_response(user_query, topic)
    return jsonify({"response": response})

if __name__ == "__main__":
  app.run(debug=True)
