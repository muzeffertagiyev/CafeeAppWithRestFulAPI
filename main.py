from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

import random
import json

app = Flask(__name__)

with open("config.json") as config_file:
    data = json.load(config_file)
    API_KEY_FOR_DELETING_CAFE = data['api_key']

#Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    

@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route('/random/')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)

    # return jsonify(cafe=random_cafe.to_dict())
    return jsonify(cafe=
    {
        "id":random_cafe.id,
        "name":random_cafe.name,
        "map_url":random_cafe.map_url,
        "img_url":random_cafe.img_url,
        "location":random_cafe.location,
        "seats":random_cafe.seats,
        "has_toilet":random_cafe.has_toilet,
        "has_wifi":random_cafe.has_wifi,
        "has_sockets":random_cafe.has_sockets,
        "can_take_calls":random_cafe.can_take_calls,
        "coffee_price":random_cafe.coffee_price
    })

@app.route('/all/')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()

    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search/")
def search_cafe():
    cafe_location = request.args.get('loc')
    cafe = Cafe.query.filter_by(location=cafe_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={
            "Not Found":"Sorry, we do not have a cafe at that location"
        })

## HTTP POST - Create Record
@app.route('/add/', methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('location'),
        has_sockets=bool(request.form.get('has_sockets')),
        # we use bool function because we will ad 0 and 1 for this variables and it will return us True and False 
        has_toilet=bool(request.form.get('has_toilet')),
        has_wifi=bool(request.form.get('has_wifi')),
        can_take_calls=bool(request.form.get('can_tke_calls')),
        seats=request.form.get('seats'),
        coffee_price=request.form.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"Success":"New cafe was added to our database successfully"})

## HTTP PUT/PATCH - Update Record
# we use PATCH method if we want to change some data from our database,if we need to change our data entirely then we should use PUT method
@app.route('/update-price/<int:cafe_id>', methods=["PATCH"])
def update_coffee_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_price = request.args.get('new_price')
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success":f"The coffee price for cafe {cafe.name} was updated successfully"})
    else:
        return jsonify(error={"Not Found":"Sorry, a cafe with that id was not found in the database"})

## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    asked_api_key = request.args.get('api_key')
    if asked_api_key == API_KEY_FOR_DELETING_CAFE:
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success":f'Cafe "{cafe.name}" was deleted successfully'})
        else:
            return jsonify(error={"Not Found":"Sorry the cafe with that ID was not in the database "})
            
    else:
        return jsonify(error={"Forbidden":"Sorry that is not allowed. Make sure you have the correct API_KEY"})
        

if __name__ == '__main__':
    app.run(debug=True)
