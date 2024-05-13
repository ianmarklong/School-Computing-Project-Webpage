import sqlite3
import flask
import os
from flask import render_template, request, Flask
from flask import send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__) #create a flask object
###################################DISCOVER###################################################
@app.route('/') #root path
def discover():
     # Retrieve all recipes from the database
    all_recipes = get_all_recipes()

    # Check if a search query is present
    search_query = request.args.get('recipe', '')

    # Filter recipes based on the search query
    filtered_recipes = filter_recipes(all_recipes, search_query)

    return render_template('Hdiscover.html', foods=filtered_recipes, search_query=search_query)

@app.route('/food_details/<dishName>')
def food_details(dishName):
    details = getDetails(dishName)
    reviews = getReviews(dishName)
    if details:
        return render_template('HfoodDetails.html', food=details, reviews=reviews)
    else:
        # Handle case where food item with specified ID is not found
        return "Food not found", 404
    
@app.route('/photos/<filename>')
def get_file(filename):
    return send_from_directory('uploads', filename)
    
####################################SHARE############################################

@app.route('/share/') #share form 
def share():
    return render_template('Hshare.html')

@app.route('/submitted/', methods=['POST']) #route to share form path using POST method
def submitted():
    if 'dishName' in request.form:
        insertDetails(request.form,request.files['image'])
        return render_template('Hsubmitted.html')
    return 'No form data found'

####################################REVIEW############################################
@app.route('/review/') #review path
def review():
    all_recipes = get_all_recipes()

    # Check if a search query is present
    search_query = request.args.get('recipe', '')

    # Filter recipes based on the search query
    filtered_recipes = filter_recipes(all_recipes, search_query)

    return render_template('Hreview.html', foods=filtered_recipes, search_query=search_query)

@app.route('/reviewform/<dishName>')
def reviewform(dishName):
    return render_template('Hreviewform.html',dishName = dishName)

@app.route('/submittedReview/', methods=['POST']) #route to share review form path using POST method
def submittedReview():
    if 'dishName' in request.form: 
        insertReviews(request.form)
        return render_template('Hsubmitted.html')
    return 'No form data found'

####################################ABOUT############################################
@app.route('/about/') 
def about():
    return render_template('Habout.html')

#####################################functions#####################################################

def insertDetails(data,imageFile):
    #from notes
    photo = imageFile
    filename = secure_filename(photo.filename)
    path = os.path.join('uploads', filename)
    photo.save(path)
    #
    conn = sqlite3.connect('hawker.db')
    print(data)
    tobeInserted = (data['dishName'],data['stallName'],data['location'],float(data['price']),int(data['protein']),data['cuisine'],filename)
    #print(tobeInserted)
    conn.execute('INSERT INTO Details(DishName, StallName, Location, Price, Protein, Cuisine, Image) VALUES (?,?,?,?,?,?,?)',tobeInserted)

    conn.commit()
    conn.close()

def get_all_recipes():
    # Connect to the database
    conn = sqlite3.connect('hawker.db')
    c = conn.cursor()
    
    # Retrieve all recipes from the database
    c.execute('SELECT * FROM Details')
    all_recipes = c.fetchall()
    
    # Close the connection
    conn.close()
    
    return all_recipes

def filter_recipes(all_recipes, search_query):
    # If search query is empty, return all recipes
    if not search_query:
        return all_recipes

    # Filter recipes based on the search query
    filtered_recipes = [recipe for recipe in all_recipes if search_query.lower() in recipe[1].lower()]
    
    return filtered_recipes

def getDetails(DishName):
    conn = sqlite3.connect('hawker.db')
    cursor = conn.execute('''SELECT Details.DishName, Details.StallName, Details.Location, 
                                    Details.Price, Details.Protein, Details.Cuisine, 
                                    Details.Image
                             FROM Details
                             WHERE Details.DishName=?''', (DishName,))
    
    data = cursor.fetchone()  # Fetch the single record
    
    conn.close()
    return data

def getReviews(DishName):
    conn = sqlite3.connect('hawker.db')
    cursor = conn.execute('''SELECT Rating, Comments
                             FROM Review
                             WHERE DishName=?''', (DishName,))
    
    reviews = cursor.fetchall()  # Fetch all the review records
    
    conn.close()
    return reviews

def insertReviews(data):
    conn = sqlite3.connect('hawker.db')
    tobeInserted = (data['dishName'],data['rating'],data['comments'])
    #print(tobeInserted)
    conn.execute('INSERT INTO Review(DishName, Rating, Comments) VALUES (?,?,?)',tobeInserted)

    conn.commit()
    conn.close()



if __name__ == '__main__':
    app.run()
