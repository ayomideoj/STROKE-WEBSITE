from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv
import joblib


load_dotenv()
app = Flask(__name__)
CORS(app)

# Secret key needed to use session (store prediction between requests)
app.secret_key = os.getenv("SECRET_KEY", "stroke-prediction-secret-key")

client = MongoClient(os.getenv("MONGO_URI"))
db = client["stroke_db"]
collection = db["users"]

model = joblib.load("trained_model.pkl")
scaler = joblib.load("scaler.pkl")

mappings = {
    'gender': {'Female': 0, 'Male': 1, 'Other': 2},
    'ever_married': {'No': 0, 'Yes': 1},
    'work_type': {'Govt_job': 0, 'Never_worked': 1, 'Private': 2, 'Self_employed': 3, 'children': 4},
    'Residence_type': {'Rural': 0, 'Urban': 1},
    'smoking_status': {'Unknown': 0, 'formerly smoked': 1, 'never smoked': 2, 'smokes': 3}
}


@app.route('/')
@app.route('/index2.html')
def home():
    return render_template('index2.html')


@app.route('/test2.html')
def test_page():
    return render_template('test2.html')


@app.route('/submit', methods=['POST'])
def predict():
    # Get raw form data (keep original values for display on result page)
    raw_data = request.form.to_dict()

    # Make a copy to encode for the model
    encoded_data = raw_data.copy()
    for key in mappings:
        if key in encoded_data:
            encoded_data[key] = mappings[key][encoded_data[key]]

    # Build the input array in the correct feature order
    input_values = [float(encoded_data[key]) for key in [
        'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
        'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status'
    ]]

    # Scale and predict
    input_array = scaler.transform([input_values])
    prediction = model.predict(input_array)[0]
    result = "Stroke" if prediction == 1 else "No Stroke"

    # Save record to MongoDB
    record = {**raw_data, "prediction": result}
    collection.insert_one(record)

    # Store prediction + original form data in session so result page can read it
    session['prediction'] = result
    session['form_data'] = raw_data

    # Redirect to the result page
    return redirect(url_for('result_page'))


@app.route('/result')
def result_page():
    # Retrieve prediction and form data from session
    prediction = session.get('prediction')
    form_data = session.get('form_data', {})

    # If someone visits /result directly with no session data, send them back to the test
    if prediction is None:
        return redirect(url_for('test_page'))

    return render_template('result.html', prediction=prediction, form_data=form_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
