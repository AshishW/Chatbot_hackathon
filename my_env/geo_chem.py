import pandas as pd
import numpy as np
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

# Example usage
# sentence = "Can you generate a map for the element aluminum oxide, copper,silicon dioxide."
# extracted_elements = extract_chemicals(response)
# print(extracted_elements)
# # Print message if elements are present in the sentence
# if extracted_elements:
#     print(f"The following elements are present in the sentence: {', '.join(extracted_elements)}")
# else:
#     print("No elements from the dictionary are present in the sentence.")

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
            generate_kriging_map(df,element, toposheet_no)
            
def generate_kriging_map(df, element, toposheet_number=None, variogram_model='spherical'):
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
    
    # Update layout with title and labels
    fig.update_layout(
        title=f'Geochemical Kriging Map for {element}' + (f' (Toposheet {toposheet_number})' if toposheet_number else ''),
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        coloraxis_colorbar=dict(title=f'{element} Concentration')
    )
    print("Figure",fig)
    # Show the plot
    fig.show()
    

def create_idw_map_from_query(query,df,threshold=100):
    t2 = extract_topo_no(query)
    e2 = extract_chemicals(query)
       
    for toposheet_no in t2:
        for element in e2:
            generate_idw_map(df,element,toposheet_no,threshold) 
    
def generate_idw_map(df, element, toposheet_number, threshold_percentile):
    # Filter the DataFrame by the specified toposheet number
    gdf = df[df['toposheet'] == toposheet_number]

    # Step 1: Determine Baseline
    baseline = np.median(gdf[element])  # Using median as the baseline

    # Step 2: Calculate Deviation
    deviation = gdf[element] - baseline

    # Step 3: Statistical Analysis
    std_dev = np.std(deviation)
    percentile_value = np.percentile(deviation, threshold_percentile)

    # Step 4: Define Anomaly Threshold
    anomaly_threshold = percentile_value  # Setting the specified percentile as the threshold

    # Step 5: Identify Anomalies
    anomalies = gdf[deviation > anomaly_threshold]

    # Step 6: Anomaly Map
    # Create grid coordinates for interpolation
    grid_x, grid_y = np.mgrid[min(gdf['longitude']):max(gdf['longitude']):100j, min(gdf['latitude']):max(gdf['latitude']):100j]

    # Interpolate using IDW
    grid_z = griddata((gdf['longitude'], gdf['latitude']), deviation, (grid_x, grid_y), method='cubic')

    # Plotting the IDW map
    plt.figure(figsize=(10, 8))
    plt.imshow(grid_z.T, extent=(min(gdf['longitude']), max(gdf['longitude']), min(gdf['latitude']), max(gdf['latitude'])), origin='lower')
    plt.scatter(anomalies['longitude'], anomalies['latitude'], c='red')  # Anomalies marked in red
    plt.colorbar(label='Deviation from Baseline')
    plt.title(f'Geochemical IDW Map for {element} (Toposheet {toposheet_number})')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

def find_max_values(query,df):
    toposheet_numbers = extract_topo_no(query)
    elements = extract_chemicals(query)
    max_value_results = []
    for toposheet_number in toposheet_numbers:
        for element in elements:
            max_value = df[element].max()
            max_location = df[df[element] == max_value][['latitude', 'longitude']].iloc[0]
            max_lat, max_lon = max_location['latitude'], max_location['longitude']
            max_value_result = f"For the toposheet {toposheet_number}, the element {element} has maximum PPM value {max_value} at latitude {max_lat} and longitude {max_lon}."
            max_value_results.append(max_value_result)
    return max_value_results

def find_min_values(query,df):
    toposheet_numbers = extract_topo_no(query)
    elements = extract_chemicals(query)
    min_value_results = []
    for toposheet_number in toposheet_numbers:
        for element in elements:
            min_value = df[element].min()
            min_location = df[df[element] == min_value][['latitude', 'longitude']].iloc[0]
            min_lat, min_lon = min_location['latitude'], min_location['longitude']
    
            # Results ko sentence mein display kar rahe hain
            min_value_result = f"For the toposheet {toposheet_number}, the element {element} has minimum PPM value {min_value} at latitude {min_lat} and longitude {min_lon}."
            min_value_results.append(min_value_result)
    return min_value_results

def find_both_min_max(query,df):
    toposheet_numbers = extract_topo_no(query)
    elements = extract_chemicals(query)
    min_max_value_results = []
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
            min_max_value_results.append(min_max_value_result)
    return min_max_value_results

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
    combined_output = []  # Initialize a list to store combined output
    
    for subquery in subqueries:
        print(f"Processing subquery: {subquery}")
        output = "Apologies, but I'm only able to provide information related to Nagpur data. Please enter a valid query about Nagpur. Thank you for your understanding and patience"        
        # Check conditions and call functions accordingly
        if 'maximum' in subquery.lower() and 'minimum' in subquery.lower():
            print("Calling the function for min and max")
            output = find_both_min_max(subquery, df=Nagpur_gdf)
            
        # Check if the subquery mentions both latitude and longitude
        elif all(word in subquery.lower() for word in ['maximum', 'minimum', 'latitude', 'longitude']):
            print('Only Max function is called')
            # Call the function to handle maximum latitude and longitude values
            output = handle_max_latitude_longitude(subquery)
            
        # Check if the subquery mentions 'idw interpolation map'
        elif 'idw' in subquery.lower() and 'inverse distance weighted map' in subquery.lower():
            print("Calling the IDW function")
            output = create_idw_map_from_query(subquery, df=Nagpur_gdf)
            
        elif 'idw' in subquery.lower() and "kriging" in subquery.lower():
            print("Calling both kriging and IDW function")
            output_idw = create_idw_map_from_query(subquery, df=Nagpur_gdf)
            output_kriging = create_kriging_map_from_query(subquery, df=Nagpur_gdf)
            output = (output_idw, output_kriging)  # Store both outputs in a tuple
            
        elif 'kriging' in subquery.lower():
            print("Calling the kriging function")
            output = create_kriging_map_from_query(subquery, df=Nagpur_gdf)
#         elif:
#             print("None")
            
        elif 'idw' in subquery.lower():
            print("Invoking the IDW mage...")
            output = create_idw_map_from_query(subquery, df=Nagpur_gdf)
            
        # ... (Continue with the rest of your conditions)
        
        # Add the output to the combined_output list
        combined_output.append(output)
    if not combined_output:
        apology_message = "Apologies, but I'm only able to provide information related to Nagpur data. Please enter a valid query about Nagpur. Thank you for your understanding and patience."
        combined_output.append(apology_message)
    return combined_output

def generate_geochemistry_response(query):
    corrected_sentence = correct_typos(query)
    Subqueries = split_query_smartly(corrected_sentence)
    response = process_subqueries(Subqueries)
    return response

# generate_geochem_response('Create a kriging map for copper and gold for the toposheet number 55K14')

if __name__ == "__main__":
    generate_geochemistry_response(query="Create a kriging map for copper for the toposheet number 55K14")