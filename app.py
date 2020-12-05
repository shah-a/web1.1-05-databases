# Bismillah al-Rahmaan al-Raheem
# Ali Shah | Dec. 04, 2020

"""WEB1.1 Assignment 5: Databases."""

from bson.objectid import ObjectId
from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantdb"
mongo = PyMongo(app)

plants = mongo.db.plants
harvests = mongo.db.harvests

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    return render_template('plants_list.html', plants=plants.find())

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""

    if request.method == 'GET':
        return render_template('create.html')
    # else:  # if request.method == 'POST':
    new_plant = {
        'name': request.form.get('plant_name'),
        'variety': request.form.get('variety'),
        'photo_url': request.form.get('photo'),
        'date_planted': request.form.get('date_planted')
    }

    plant_id = plants.insert_one(new_plant).inserted_id

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """Accepts a POST request with data for 1 harvest and inserts into database."""

    new_harvest = {
        'quantity': request.form.get('harvested_amount'),
        'date': request.form.get('date_planted'),
        'plant_id': plant_id
    }

    harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    if not ObjectId.is_valid(plant_id) or not plants.find_one({'_id': ObjectId(plant_id)}):
        return render_template('error.html')

    plant_to_show = plants.find_one({'_id': ObjectId(plant_id)})
    harvest_list = harvests.find({'plant_id': plant_id})
    context = {
        'plant' : plant_to_show,
        'harvests': harvest_list
    }
    return render_template('detail.html', **context)

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""

    if request.method == 'GET':
        plant_to_show = plants.find_one({'_id': ObjectId(plant_id)})
        return render_template('edit.html', plant=plant_to_show)
    # else:  # if request.method == 'POST':
    plant_filter = {
        '_id': ObjectId(plant_id)
    }

    plant_update = {
        '$set': {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
    }

    plants.update_one(plant_filter, plant_update)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """Delete plants."""
    plants.delete_one({'_id': ObjectId(plant_id)})
    harvests.delete_many({'plant_id': plant_id})
    return redirect(url_for('plants_list'))

@app.errorhandler(404)
def error(e):
    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)
