from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv
import joblib




load_dotenv()
app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["stroke_db"]
collection = db["users"]

model = joblib.load("trained_model.pkl")
scaler = joblib.load("scaler.pkl")

mappings = {
  'gender' : {'Female': 0, 'Male': 1, 'Other': 2},
  'ever_married':{'No': 0, 'Yes': 1},
  'work_type': {'Govt_job': 0, 'Never_worked': 1, 'Private': 2, 'Self_employed': 3, 'children': 4},
  'Residence_type': {'Rural': 0, 'Urban': 1},
  'smoking_status':{'Unknown': 0, 'formerly smoked': 1, 'never smoked': 2, 'smokes': 3}
}


@app.route('/index2.html')
def home():
    return render_template('index2.html')


@app.route('/test2.html')
def test_page():
    return render_template('test2.html')


@app.route('/submit', methods=['POST'])
def predict():
    data = request.form.to_dict()

    for key in mappings:
        if key in data:
            data[key] = mappings[key][data[key]]

    input_values = [float(data[key]) for key in[
        'gender', 'age', 'hypertension','heart_disease','ever_married', 'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status'

    ]]

    input_array = scaler.transform([input_values])

    prediction = model.predict(input_array)[0]
    result = "Stroke" if prediction == 1 else "No Stroke"


    record ={
        **data,
        "prediction": result
    }
    collection.insert_one(record)





    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)