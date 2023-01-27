from flask import Flask, render_template, redirect, request, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import pymysql
from werkzeug.utils import secure_filename
from datetime import datetime
import csv
import os


USER_MYSQL = 'root'
PASSWORD_MYSQL = 'Soueu.0816'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'upload')

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

conn = f"mysql+pymysql://{USER_MYSQL}:{PASSWORD_MYSQL}@127.0.0.1:3306/glpi"

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
    
    users_id = db.Column(db.Integer, db.ForeignKey("glpi_users.id"), default=0, nullable=False)
    states_id = db.Column(db.Integer, db.ForeignKey("glpi_states.id"), default=0, nullable=False)
    groups_id = db.Column(db.Integer, db.ForeignKey("glpi_groups.id"), default=0, nullable=False)
    entities_id = db.Column(db.Integer, db.ForeignKey("glpi_entities.id"), default=0, nullable=False)
    locations_id = db.Column(db.Integer, db.ForeignKey("glpi_locations.id"), default=0, nullable=False)
    peripheraltypes_id = db.Column(db.Integer, db.ForeignKey("glpi_peripheraltypes.id"), default=0, nullable=False)
    peripheralmodels_id = db.Column(db.Integer, db.ForeignKey("glpi_peripheralmodels.id"), default=0, nullable=False)
    manufacturers_id = db.Column(db.Integer, db.ForeignKey("glpi_manufacturers.id"), default=0, nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    date_mod = db.Column(db.String(250))
    date_creation = db.Column(db.String(250))
    contact = db.Column(db.String(250))
    comment = db.Column(db.Text)
    serial = db.Column(db.String(255), nullable=False)
    otherserial = db.Column(db.String(255))
    is_deleted = db.Column(db.Integer, nullable=False)
    is_dynamic = db.Column(db.Integer, default=0, nullable=False)
    is_template = db.Column(db.Integer, default=0, nullable=False)
    is_deleted = db.Column(db.Integer, default=0, nullable=False)
    is_global = db.Column(db.Integer, default=0, nullable=False)
    is_recursive = db.Column(db.Integer, default=0, nullable=False)
    groups_id_tech = db.Column(db.Integer, default=0, nullable=False)
    users_id_tech = db.Column(db.Integer, default=0, nullable=False)
    

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

#funcs
def get_manufacturer(id): return Manufacturer.query.get(int(id))
def get_state(id): return State.query.get(int(id))

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

ROWS_PER_PAGE = 20

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    
    # peripherals = Peripheral.query.all()
    peripherals = Peripheral.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template("index.html", peripherals=peripherals, manufacturer=get_manufacturer, state=get_state)

@app.route("/new-peripheral", methods=['GET', 'POST'])
def add_new_peripheral():
    manufacturers = Manufacturer.query.all()
    states = State.query.all()
    entities = Entitie.query.all()
    if request.method == 'POST':
        new_peripheral = Peripheral(
            name=request.form["name_peripheral"],
            manufacturers_id=request.form["manufacturer"],
            serial=request.form["serial"],
            states_id=request.form["state"],
            entities_id=request.form["entitie"],
            users_id=0,
            date_creation=datetime.now().strftime("%Y-%m-%d %X")
        )
        db.session.add(new_peripheral)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_peripheral.html", manufacturers=manufacturers, states=states, entities=entities)

@app.route("/new-peripherals", methods=['GET', 'POST'])
def add_new_peripherals():
    file_csv = request.files['csv-file']
    savePath = os.path.join(UPLOAD_FOLDER, secure_filename(file_csv.filename))
    file_csv.save(savePath)
    with open(savePath, 'r', encoding="utf-8") as file:
        next(file)
        csvreader = csv.reader(file)
        for row in csvreader:
            new_peripheral = Peripheral(
            name=row[0],
            manufacturers_id=int(row[1]),
            serial=row[2],
            states_id=int(row[3]),
            entities_id=int(row[4]),
            users_id=0,
            comment=(row[5]),
            date_creation=datetime.now().strftime("%Y-%m-%d %X")
        )

            db.session.add(new_peripheral)
            db.session.commit()
    os.remove(savePath)
    return redirect(url_for("home"))



@app.route("/edit/<int:peripheral_id>", methods=['GET', 'POST'])
def edit_peripheral(peripheral_id):
    peripheral = Peripheral.query.get(peripheral_id)
    manufacturers = Manufacturer.query.all()
    states = State.query.all()
    entities = Entitie.query.all()
    
    if request.method == 'POST':
        peripheral.name = request.form["name_peripheral"]
        peripheral.manufacturers_id = request.form["manufacturer"]
        peripheral.serial = request.form["serial"]
        peripheral.states_id = request.form["state"]
        peripheral.entities_id = request.form["entitie"]
        peripheral.date_creation = datetime.now().strftime("%Y-%m-%d %X")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("peripheral_edit.html", peripheral=peripheral, manufacturers=manufacturers, states=states, entities=entities)

@app.route("/delete/<int:peripheral_id>")
def delete_peripheral(peripheral_id):
    peripheral_to_delete = Peripheral.query.get(peripheral_id)
    db.session.delete(peripheral_to_delete)
    db.session.commit()
    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)