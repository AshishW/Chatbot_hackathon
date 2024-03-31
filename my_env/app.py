from flask import Flask, render_template, request
from flask import jsonify
# import model  # Import your trained model

app = Flask(__name__)

def generate_response(user_query):
  """
  This function will be replaced with your actual model logic in the future.
  For now, it returns a dummy response.
  """
  if(user_query == "hello"):
     return "Hello! How can I help you today?"
  return "Thanks for your query! I'm still under development and learning to communicate effectively. Stay tuned for future updates!"


@app.route("/")
def home():
  return render_template("index.html")

# @app.route("/get_response", methods=["POST"])
# def get_response():
#   user_query = request.form["query"]
#   # response = model.generate_response(user_query)  # Call your model function
#   response = generate_response(user_query)  # Call your model function

#   return jsonify({"response": response})
@app.route("/get_response", methods=["POST"])
def get_response():
    user_query = request.json["query"]
    response = generate_response(user_query)
    return jsonify({"response": response})

if __name__ == "__main__":
  app.run(debug=True)
