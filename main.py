from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

conn = "mysql+pymysql://root:with0816@127.0.0.1:3306/glpi"

app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

##CONFIGURE TABLES
class User(db.Model):
    __tablename__ = "glpi_users"
    id = db.Column(db.Integer, primary_key=True)
    
    locations_id = db.Column(db.Integer, db.ForeignKey("glpi_locations"))
    
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40))
    realname = db.Column(db.String(255))

class Group(db.Model):
    __tablename__ = "glpi_groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Peripheral(db.Model):
    __tablename__ = "glpi_peripherals"
    id = db.Column(db.Integer, primary_key=True)
    
    users_id = db.Column(db.Integer, db.ForeignKey("glpi_users"))
    states_id = db.Column(db.Integer, db.ForeignKey("glpi_states"))
    entities_id = db.Column(db.Integer, db.ForeignKey("glpi_entities"))
    locations_id = db.Column(db.Integer, db.ForeignKey("glpi_locations"))
    peripheraltypes_id = db.Column(db.Integer, db.ForeignKey("glpi_peripheraltypes"))
    peripheralmodels_id = db.Column(db.Integer, db.ForeignKey("glpi_peripheralmodels"))
    manufacturers_id = db.Column(db.Integer, db.ForeignKey("glpi_manufacturers"))
    
    name = db.Column(db.String(255), nullable=False)
    date_mod = db.Column(db.String(250))
    date_creation = db.Column(db.String(250))
    contact = db.Column(db.String(250))
    comment = db.Column(db.Text)
    serial = db.Column(db.String(255), nullable=False)
    otherserial = db.Column(db.String(255))
    is_deleted = db.Column(db.Integer, nullable=False)

class Manufacturer(db.Model):
    __tablename__ = "glpi_manufacturers"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)
    date_mod = db.Column(db.String(250))
    date_creation = db.Column(db.String(250), nullable=False)       
    
class State(db.Model):
    __tablename__ = "glpi_states"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Entitie(db.Model):
    __tablename__ = "glpi_entities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    
class Location(db.Model):
    __tablename__ = "glpi_locations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    completename = db.Column(db.String(255), nullable=False)

class PeripheralModel(db.Model):
    __tablename__ = "glpi_peripheralmodels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class PeripheralType(db.Model):
    __tablename__ = "glpi_peripheraltypes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

# db.create_all()

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/")
def home():
    peripherals = Peripheral.query.all()
    def get_manufacturer(id):
        return Manufacturer.query.get(int(id))
    def get_state(id):
        return State.query.get(int(id))
        
    return render_template("index.html", peripherals=peripherals, manufacturer=get_manufacturer, state=get_state)





if __name__ == "__main__":
    app.run(debug=True)