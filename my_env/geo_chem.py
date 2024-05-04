import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import spacy
import plotly.graph_objects as go
from pykrige.ok import OrdinaryKriging
from scipy.interpolate import griddata
import base64
import os


# Get the directory of the current Python file
script_dir = os.path.dirname(__file__)

# Construct the relative path to the CSV file (assuming it's in the same directory)
csv_file_path = os.path.join(script_dir, 'NGDR_Nagpur.csv')
Nagpur_gdf = pd.read_csv(csv_file_path)
# Nagpur_gdf.fillna(0.0, inplace=True)

import textdistance
word_list = ["kriging","concentration","toposheet","interpolation","inverse distance weighted","idw","maximum","minimum","longitude","latitude","aluminum"]
def correct_typos(text, threshold=0.5):
    corrected_text = []
    words = text.split()
    for word in words:
        # Check if the word is misspelled
        suggestions = [w for w in word_list if textdistance.jaccard.normalized_similarity(w, word) >= threshold]
        if suggestions:
            corrected_word = max(suggestions, key=lambda x: textdistance.jaccard.normalized_similarity(x, word))
        else:
            corrected_word = word
        corrected_text.append(corrected_word)
    return ' '.join(corrected_text)


# In[5]:


import re

# Dictionary of chemical names and their formulas
chemicals = {
   'silicon dioxide': 'sio2',
    'aluminum oxide': 'al2o3',
    'iron(III) oxide': 'fe2o3',
    'titanium dioxide': 'tio2',
    'calcium oxide': 'cao',
    'magnesium oxide': 'mgo',
    'manganese(II) oxide': 'mno',
    'sodium oxide': 'na2o',
    'potassium oxide': 'k2o',
    'phosphorus pentoxide': 'p2o5',
    'loss on ignition': 'loi',
    'barium': 'ba',
    'gallium': 'ga',
    'scandium': 'sc',
    'vanadium': 'v',
    'thorium': 'th',
    'lead': 'pb',
    'nickel': 'ni',
    'cobalt': 'co',
    'rubidium': 'rb',
    'strontium': 'sr',
    'yttrium': 'y',
    'zirconium': 'zr',
    'niobium': 'nb',
    'chromium': 'cr',
    'copper': 'cu',
    'zinc': 'zn',
    'gold': 'au',
    'lithium': 'li',
    'cesium': 'cs',
    'arsenic': 'as_',
    'antimony': 'sb',
    'bismuth': 'bi',
    'selenium': 'se',
    'silver': 'ag',
    'beryllium': 'be',
    'germanium': 'ge',
    'molybdenum': 'mo',
    'tin': 'sn',
    'lanthanum': 'la',
    'cerium': 'ce',
    'praseodymium': 'pr',
    'neodymium': 'nd',
    'samarium': 'sm',
    'europium': 'eu',
    'terbium': 'tb',
    'gadolinium': 'gd',
    'dysprosium': 'dy',
    'holmium': 'ho',
    'erbium': 'er',
    'thulium': 'tm',
    'ytterbium': 'yb',
    'lutetium': 'lu',
    'hafnium': 'hf',
    'tantalum': 'ta',
    'tungsten': 'w',
    'uranium': 'u',
    'platinum': 'pt',
    'palladium': 'pd',
    'indium': 'in_',
    'fluorine': 'f',
    'tellurium': 'te',
    'thallium': 'tl',
    'mercury': 'hg',
    'cadmium': 'cd'
    # Add more chemicals as needed
}

# Function to extract chemical names and formulas from a sentence
def extract_chemicals(query):
    # Initialize an empty list to store the extracted elements
    elements = []

    # Convert the sentence to lowercase
    lower_sentence = query.lower()

    # Extract words from the sentence
    words = re.findall(r'\b\w+\b', lower_sentence)

    # Check if any chemical name or formula is present in the sentence
    for chemical, formula in chemicals.items():
        if chemical.lower() in lower_sentence or formula.lower() in words:
            elements.append(formula)

    # Return the list of extracted elements
    return elements


def extract_topo_no(str1):
    toposheet_numbers = []
    toposheet_pattern = r'\b\d+[a-zA-Z]+\d+\b'
    toposheet_numbers = re.findall(toposheet_pattern,str1)
    return toposheet_numbers



def create_kriging_map_from_query(query,df):
    t1 = extract_topo_no(query)
    e1 = extract_chemicals(query)
    
    for toposheet_no in t1:
        for element in e1:
            max_value = df[element].max()
            max_location = df[df[element] == max_value][['latitude', 'longitude']].iloc[0]
            max_lat, max_lon = max_location['latitude'], max_location['longitude']
            # Minimum value aur uske corresponding latitude, longitude find kar rahe hain
            min_value = df[element].min()
            min_location = df[df[element] == min_value][['latitude', 'longitude']].iloc[0]
            min_lat, min_lon = min_location['latitude'], min_location['longitude']
            return generate_kriging_map(df,element,max_value,max_location,max_lat,max_lon,min_value,min_location,min_lat,min_lon, toposheet_no,)



def generate_kriging_map(df, element, max_value, max_location, max_lat, max_lon, min_value, min_location, min_lat, min_lon, toposheet_number=None, variogram_model='spherical'):
    # Function body goes here
     # Filter the DataFrame by the specified toposheet number if provided
    if toposheet_number is not None:
        df = df[df['toposheet'] == toposheet_number]
    
    # Define grid resolution
    gridx = np.linspace(df['longitude'].min(), df['longitude'].max(), 100)
    gridy = np.linspace(df['latitude'].min(), df['latitude'].max(), 100)
    
    # Perform Ordinary Kriging
    OK = OrdinaryKriging(df['longitude'], df['latitude'], df[element], variogram_model=variogram_model)
    z_interp, ss = OK.execute('grid', gridx, gridy)
    
    
    # Create the contour plot
    contour = go.Contour(
        z=z_interp.data,  # 2D array of the heatmap values
        x=gridx,  # X coordinates corresponding to 'z_interp'
        y=gridy,  # Y coordinates corresponding to 'z_interp'
        colorscale='YlOrRd',  # Match the colormap
        showscale=True  # Show the color scale bar
    )
    
    # Create the scatter plot with hover annotations
    scatter = go.Scatter(
        x=df['longitude'],
        y=df['latitude'],
        mode='markers',
        marker=dict(
            color=df[element],
            colorscale='YlOrRd',  # Match the colormap
            showscale=False,  # We already have a color scale from the contour
            line=dict(color='black', width=1)  # Black border around the scatter points
        ),
        text=df[element],  # Text for hover annotations
        hoverinfo='text'  # Show only the text on hover
    )
    
    # Create a figure and add the contour plot
    fig = go.Figure(data=[contour])
    
    # Add the scatter plot on top of the contour plot
    fig.add_trace(scatter)
    
    fig.add_annotation(
    text=f"<i>Maximum value (in ppm): <b>{max_value}</b> at longitude <b>{max_lon}</b> and latitude <b>{max_lat}</b></i>",
    xref="paper", yref="paper",
    x=0.5, y=1.2, showarrow=False,
    font=dict(size=14),
    align="center"
    )

    fig.add_annotation(
    text=f"<i>Minimum value (in ppm): <b>{min_value}</b> at longitude <b>{min_lon}</b> and latitude <b>{min_lat}</b></i>",
    xref="paper", yref="paper",
    x=0.5, y=1.1, showarrow=False,
    font=dict(size=14),
    align="center"
    )

    # Add a title to the map
    fig.update_layout(
    title=f"<b>Stream Sediment samples showing {element} Values(ppm)</b>",
    title_x=0.5,  # Center the title
    title_y=0.95,  # Add some space from the top
    margin=dict(t=120)  # Adjust margin to accommodate the annotations and title
    )
#     fig.show()
    data = fig.to_dict()
    layout = fig.to_dict()
    return (data,layout, 'kriging_map')


# In[103]:


def create_idw_map_from_query(query,df):
    t2 = extract_topo_no(query)
    e2 = extract_chemicals(query)
    threshold_percentile = 100   
    for toposheet_number in t2:
        for element in e2:
            max_value = df[element].max()
            max_location = df[df[element] == max_value][['latitude', 'longitude']].iloc[0]
            max_lat, max_lon = max_location['latitude'], max_location['longitude']
            # Minimum value aur uske corresponding latitude, longitude find kar rahe hain
            min_value = df[element].min()
            min_location = df[df[element] == min_value][['latitude', 'longitude']].iloc[0]
            min_lat, min_lon = min_location['latitude'], min_location['longitude']
            return generate_idw_map(df, element,max_value, max_location, max_lat, max_lon, min_value, min_location, min_lat, min_lon, toposheet_number, threshold_percentile) 


# In[181]:


import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import io
import base64

# def generate_idw_map(df, element,max_value, max_location, max_lat, max_lon, min_value, min_location, min_lat, min_lon, toposheet_number, threshold_percentile):
#     # Filter the DataFrame by the specified toposheet number
#     gdf = df[df['toposheet'] == toposheet_number]

#     # Step 1: Determine Baseline
#     baseline = np.median(gdf[element])  # Using median as the baseline

#     # Step 2: Calculate Deviation
#     deviation = gdf[element] - baseline

#     # Step 3: Statistical Analysis
#     std_dev = np.std(deviation)
#     percentile_value = np.percentile(deviation, threshold_percentile)

#     # Step 4: Define Anomaly Threshold
#     anomaly_threshold = percentile_value  # Setting the specified percentile as the threshold

#     # Step 5: Identify Anomalies
#     anomalies = gdf[deviation > anomaly_threshold]

#     # Step 6: Anomaly Map
#     # Create grid coordinates for interpolation
#     grid_x, grid_y = np.mgrid[min(gdf['longitude']):max(gdf['longitude']):100j, min(gdf['latitude']):max(gdf['latitude']):100j]

#     # Interpolate using IDW
#     grid_z = griddata((gdf['longitude'], gdf['latitude']), deviation, (grid_x, grid_y), method='cubic')

#     # Plotting the IDW map
#     plt.figure(figsize=(10, 8))
#     plt.imshow(grid_z.T, extent=(min(gdf['longitude']), max(gdf['longitude']), min(gdf['latitude']), max(gdf['latitude'])), origin='lower')
#     plt.scatter(anomalies['longitude'], anomalies['latitude'], c='red')  # Anomalies marked in red
#     plt.colorbar(label='Deviation from Baseline')
#     plt.title(f'Geochemical IDW Map for {element} (Toposheet {toposheet_number})\n\nMaximum value (in ppm): {max_value} at longitude {max_lat} and latitude {max_lat}\nMinimum value (in ppm): {min_value} at longitude {min_lat} and latitude {min_lat}')

#     plt.xlabel('Longitude')
#     plt.ylabel('Latitude')
    
  
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')  # Save the plot to the buffer in PNG format
#     buffer.seek(0)
#     image_data = base64.b64encode(buffer.read()).decode('utf-8')  # Convert the image buffer to base64 string
#     output = {"image_data": image_data}
#     plt.close()  # Close the plot to prevent it from being displayed or printed
    
#     return output  # Return the base64 encoded image data as a dictionary

def generate_idw_map(df, element, max_value, max_location, max_lat, max_lon, min_value, min_location, min_lat, min_lon, toposheet_number, threshold_percentile):
    # Filter the DataFrame by the specified toposheet number
    gdf = df[df['toposheet'] == toposheet_number]

    # Determine Baseline
    baseline = np.median(gdf[element])

    # Calculate Deviation
    deviation = gdf[element] - baseline

    # Statistical Analysis
    std_dev = np.std(deviation)
    percentile_value = np.percentile(deviation, threshold_percentile)

    # Define Anomaly Threshold
    anomaly_threshold = percentile_value

    # Identify Anomalies
    anomalies = gdf[deviation > anomaly_threshold]

    # Create grid coordinates for interpolation
    grid_x, grid_y = np.mgrid[min(gdf['longitude']):max(gdf['longitude']):100j, min(gdf['latitude']):max(gdf['latitude']):100j]

    # Interpolate using IDW
    grid_z = griddata((gdf['longitude'], gdf['latitude']), deviation, (grid_x, grid_y), method='cubic')

    # Create the contour plot
    contour = go.Contour(
        z=grid_z.T,
        x=np.linspace(min(gdf['longitude']), max(gdf['longitude']), 100),
        y=np.linspace(min(gdf['latitude']), max(gdf['latitude']), 100),
        colorscale='Viridis',
        colorbar=dict(title='Deviation from Baseline')
    )

    # Create the scatter plot for anomalies
    scatter = go.Scatter(
        x=anomalies['longitude'],
        y=anomalies['latitude'],
        mode='markers',
        marker=dict(color='red', size=5),
        name='Anomalies'
    )

    # Define the layout
    layout = go.Layout(
        title=f'Geochemical IDW Map for {element} (Toposheet {toposheet_number})<br>'
              f'Maximum value (in ppm): {max_value} at longitude {max_lon} and latitude {max_lat}<br>'
              f'Minimum value (in ppm): {min_value} at longitude {min_lon} and latitude {min_lat}',
        xaxis=dict(title='Longitude'),
        yaxis=dict(title='Latitude')
    )
    
    # Create the figure and plot it
    fig = go.Figure(data=[contour, scatter], layout=layout)
    data = fig.to_dict()
    layout = fig.to_dict()
    return (data, layout, 'idw_map')



def find_max_values(query, df):
    toposheet_numbers = extract_topo_no(query)
    elements = extract_chemicals(query)
    for toposheet_number in toposheet_numbers:
        for element in elements:
            max_value = df[element].max()
            max_location = df[df[element] == max_value][['latitude', 'longitude']].iloc[0]
            max_lat, max_lon = max_location['latitude'], max_location['longitude']
            max_value_result = f"For the toposheet {toposheet_number}, the element {element} has maximum PPM value {max_value} at latitude {max_lat} and longitude {max_lon}."
            return max_value_result


# In[183]:


def find_min_values(query, df):
#     print("[INFO:] Finding the min values")
    toposheet_numbers = extract_topo_no(query)
    elements = extract_chemicals(query)
    for toposheet_number in toposheet_numbers:
        for element in elements:
            min_value = df[element].min()
            min_location = df[df[element] == min_value][['latitude', 'longitude']].iloc[0]
            min_lat, min_lon = min_location['latitude'], min_location['longitude']
    
            # Results ko sentence mein display kar rahe hain
            min_value_result = f"For the toposheet {toposheet_number}, the element {element} has minimum PPM value {min_value} at latitude {min_lat} and longitude {min_lon}."
            return min_value_result


# In[184]:


def find_both_min_max(query, df):
    toposheet_numbers = extract_topo_no(query)
    elements = extract_chemicals(query)
    for toposheet_number in toposheet_numbers:
        for element in elements:
            max_value = df[element].max()
            max_location = df[df[element] == max_value][['latitude', 'longitude']].iloc[0]
            max_lat, max_lon = max_location['latitude'], max_location['longitude']
            # Minimum value aur uske corresponding latitude, longitude find kar rahe hain
            min_value = df[element].min()
            min_location = df[df[element] == min_value][['latitude', 'longitude']].iloc[0]
            min_lat, min_lon = min_location['latitude'], min_location['longitude']

            # Results ko sentence mein display kar rahe hain
            min_max_value_result = f"For the toposheet {toposheet_number}, the element {element} has maximum PPM value {max_value} at latitude {max_lat} and longitude {max_lon}, and has minimum PPM value {min_value} at latitude {min_lat} and longitude {min_lon}."
            return min_max_value_result


# In[185]:


def split_query_smartly(query):
    element_names = ['silicon dioxide', 'aluminum oxide', 'iron(III) oxide', 'titanium dioxide', 'calcium oxide', 'magnesium oxide', 'manganese(II) oxide', 'sodium oxide', 'potassium oxide', 'phosphorus pentoxide', 'loss on ignition', 'barium', 'gallium', 'scandium', 'vanadium', 'thorium', 'lead', 'nickel', 'cobalt', 'rubidium', 'strontium', 'yttrium', 'zirconium', 'niobium', 'chromium', 'copper', 'zinc', 'gold', 'lithium', 'cesium', 'arsenic', 'antimony', 'bismuth', 'selenium', 'silver', 'beryllium', 'germanium', 'molybdenum', 'tin', 'lanthanum', 'cerium', 'praseodymium', 'neodymium', 'samarium', 'europium', 'terbium', 'gadolinium', 'dysprosium', 'holmium', 'erbium', 'thulium', 'ytterbium', 'lutetium', 'hafnium', 'tantalum', 'tungsten', 'uranium', 'platinum', 'palladium', 'indium', 'fluorine', 'tellurium', 'thallium', 'mercury', 'cadmium']
    # Load spaCy English model
    nlp = spacy.load("en_core_web_sm")
    
    # Define split words and phrases
    split_words = ["maximum and minimum", "longitude and latitude"]
    additional_split_words = ["also", "display", "create", "produce", "tell", "describe","show"]
    
    # Process the query using spaCy
    doc = nlp(query)
    
    # Initialize variables
    subqueries = []
    subquery = ""
    split_flag = False  # Flag to determine if splitting is allowed
    
    # Iterate over tokens in the query
    for token in doc:
        # Check if token is a split word or phrase
        if any(split_word in token.text.lower() for split_word in split_words):
            split_flag = False
        elif token.text.strip() == "." or token.text.strip() == ". ":
            # Split when encountering a full stop or full stop followed by a space
            if subquery.strip():
                subqueries.append(subquery.strip())
            subquery = ""
            split_flag = False
        elif token.text.strip() in additional_split_words:
            # Split when encountering additional split words
            if subquery.strip():
                subqueries.append(subquery.strip())
            subquery = ""
            split_flag = False
        elif token.text.strip() == "and" and split_flag:
            # Do not split when "and" is encountered between elements
            subquery += token.text_with_ws
        elif token.text.strip() == "and" and subquery.lower().strip() in element_names:
            # Do not split when "and" is encountered after an element name
            subquery += token.text_with_ws
        elif token.text.strip().lower() not in additional_split_words:
            # Append token to subquery if it's not in the additional split words list
            subquery += token.text_with_ws
            split_flag = True  # Set flag to allow splitting after this token
    
    # Append the final subquery if it's not empty and contains more than one word
    if subquery.strip() and len(subquery.split()) > 1:
        subqueries.append(subquery.strip())
    
    return subqueries



def process_subqueries(subqueries):
#     combined_output = []  # Initialize a list to store combined output
    df = Nagpur_gdf
    try: 
        for subquery in subqueries:
            print(f"Processing subquery: {subquery}")
            if ('maximum' in subquery.lower() and 'minimum' in subquery.lower()) or ('max' in subquery.lower() and 'min' in subquery.lower()):
                print("Calling the function for min and max")
                output = find_both_min_max(subquery, df=Nagpur_gdf) 
            elif ('maximum' in subquery.lower()) or ('max' in subquery.lower()):
                print('Calling Max Fun')
                output = find_max_values(subquery,df)
            elif ('minimum' in subquery.lower()) or ('min' in subquery.lower()):
                print('Calling Min Fun')
                output = find_min_values(subquery,df)      
                
            # Check if the subquery mentions 'idw interpolation map'
            elif 'idw' in subquery.lower() or 'inverse distance weighted map' in subquery.lower():
                print("Calling the IDW function")
                output = create_idw_map_from_query(subquery, df)           
                
            elif 'idw' in subquery.lower() and "kriging" in subquery.lower():
                print("Calling both kriging and IDW function")
                output_idw = create_idw_map_from_query(subquery, df)
                output_kriging = create_kriging_map_from_query(subquery, df)
                output = (output_idw, output_kriging)  # Store both outputs in a tuple
                
            elif 'kriging' in subquery.lower():
                print("Calling the kriging function")
                output = create_kriging_map_from_query(subquery, df)
            else:
                apology_message = "I'm only able to provide information related to Nagpur data. Please enter a valid query about Nagpur toposheet data. Thank you for your understanding and patience."
                print(apology_message)
        return output 
    except Exception as e:
        print("Error:", e)
        return "There was problem processing your query, please try again and make sure the query is valid on Nagpur toposheet data. Thank you for your understanding and patience."
# Example usage:
# SubQueries = [
#     'the maximum and minimum longitude and latitude values for 55K14 for gold',
#     'a kriging map for the gold for 55K14'
# ]

# combined_output = process_subqueries(SubQueries)
# print("Combined Output:", combined_output)


# In[200]:


def generate_geochemistry_response(query):
    corrected_sentence = correct_typos(query)
    Subqueries = split_query_smartly(corrected_sentence)
    response = process_subqueries(Subqueries)
    if response == None:
        response = "Sorry, I am unable to respond to this query. I am currently equipped to provide information on Nagpur Geochemistry Toposheet data and can handle one query at a time. Thank you for your understanding."
    data_type = "text"
    if type(response) == tuple and response[2]=='idw_map':
        data_type = "idw_map"
    elif type(response) == tuple and response[2]=='kriging_map':
        data_type = "kriging_map"
    return response, data_type


if __name__ == "__main__":
    generate_geochemistry_response(query="Create a kriging map for copper for the toposheet number 55K14")
