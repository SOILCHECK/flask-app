from flask import Flask, render_template, request, session
import pickle
import pandas as pd 
from config import Config
from flask_mysqldb import MySQL

app=Flask(__name__,template_folder='./template')

app.config.from_object(Config)
mysql = MySQL(app)

plants = ['rice','maize','chickpea','kidneybeans','pigeonpeas','corn','mothbeans','mungbean','blackgram','lentil','pomegranate',
'banana','mango','grapes','tomato','watermelon','muskmelon','apple','orange','papaya','coconut','cotton','jute','weed','coffee']

input = []

@app.route("/login", methods=['GET'])
def loginPage() :
    return render_template('login.html')

@app.route("/login", methods=['POST'])
def login() : 
    username = request.form['username']
    password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute("select * from accounts where username = %s and password = %s", [username, password])
    if cursor.rowcount != 0 :
        [id,username,password] = cursor.fetchone()
        session['loggedin'] = True
        session['id'] = id
        session['username'] = username
        cursor.close()
        return render_template('home.html', session=session)
    else : 
        message = "Nom d'utilisateur ou mot de passe incorrect"
        return render_template('login.html', message=message)

@app.route("/signup", methods=['GET'])
def signupPage() : 
    return render_template('signup.html')

@app.route("/signup", methods=['POST'])
def signup() :
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']

    cursor = mysql.connection.cursor()
    cursor.execute("select * from accounts where username = %s ", [username])
    if cursor.rowcount != 0 : 
        message = "Un utilisateur avec ce nom d'utilisateur existe déjà"
        return render_template('signup.html', message=message)
    if password != password2 :
        message = "Veuillez confirmer votre mot de passe correctement !"
        return render_template('signup.html', message=message)
    
    cursor.execute("insert into accounts(username, password) values (%s, %s)", [username, password])
    mysql.connection.commit()
    cursor.close()
    return render_template('login.html')

@app.route("/", methods=['GET'])
def home() :
    return render_template('home.html')

@app.route("/plant_rec", methods=['GET'])
def form() :
    return render_template('form.html')

@app.route("/plant_rec", methods=['POST'])
def result() : 
    temperature = request.form['temperature']
    ph = request.form['ph']
    potassium = request.form['potassium']
    phosphorous = request.form['phosphorous']
    nitrogen = request.form['nitrogen']
    rainfall = request.form['rainfall']
    humidity = request.form['humidity']

    file = request.files['file']

    plants.sort()
    model = pickle.load(open('./machine-learning/model.pkl','rb'))

    if temperature != '' and ph != '' and potassium != '' and phosphorous != '' and nitrogen != '' and rainfall != '' and humidity != '' : 
        predicted = model.predict(([[nitrogen, phosphorous, potassium, temperature, humidity, ph, rainfall]]))
    if file.filename != '' :
        csv = pd.read_csv(file, skiprows=1, delimiter=',')
        for row in csv : 
            input.append(row)
        predicted = model.predict(([[input[0], input[1], input[2], input[3], input[4], input[5], input[6]]]))
                
    plant_predicted = plants[predicted[0]].capitalize()

    cur = mysql.connection.cursor()
    image = ""
    description = ""
    cur.execute("select * from plants where name = %s", [plant_predicted])
    if cur.rowcount != 0 :
        [name,image,description] = cur.fetchone()
    cur.close()
    return render_template('PlantDescription.html', plant=plant_predicted, desc=description, image=image)


if __name__ == "__main__":
    app.secret_key = 'secret'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
