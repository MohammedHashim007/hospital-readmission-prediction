import sqlite3
from contextlib import closing



from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
import re   # For email validation


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random string


# 1️⃣ Load the trained model
model = pickle.load(open("model.pkl", "rb"))

# 2️⃣ Define your feature columns (order must match training)
columns = [
    'gender', 'age', 'admission_type_id', 'discharge_disposition_id', 'admission_source_id',
    'time_in_hospital', 'num_lab_procedures', 'num_procedures', 'num_medications',
    'diag_1', 'diag_2', 'diag_3', 'number_diagnoses', 'max_glu_serum', 'A1Cresult',
    'metformin', 'glipizide', 'glyburide', 'insulin', 'change', 'diabetesMed',
    'service_utilization', 'Asian', 'Caucasian', 'Hispanic', 'Other'
]

# 3️⃣ Category → numeric mappings (must match your training encoding)
gender_map = {
    "Female": 0,
    "Male":   1
}


admission_type_map = {
    "Emergency":      0,
    "Elective":       1,
    "Not Available":  2
}

discharge_disposition_map = {
    "Discharged to home":                       0,
    "Transferred to another facility":          1,
    "Not Available":                            2,
    "Left AMA":                                 3,
    "Still patient/referred to this institution":4
}


admission_source_map = {
    "Emergency":                   0,
    "Referral":                    1,
    "Not Available":               2,
    "Transferred from hospital":   3
}


max_glu_serum_map = {
    "None":  0,
    "Norm":  1, 
    ">200":  2,
    ">300":  2
}


A1Cresult_map = {
    "None":0,
    "Norm":1,
    ">7":  2,
    ">8":  2
}


diabetesMed_map= {
    'Yes': 1, 
    'No':  0
}

# (Add additional maps for other categorical features: discharge_disposition_id, admission_source_id,
#  max_glu_serum, A1Cresult, change, diabetesMed, etc.)

CATEGORY_MAPS = {
    "gender": gender_map,
    "admission_type_id": admission_type_map,
    "discharge_disposition_id": discharge_disposition_map,
    "admission_source_id": admission_source_map,
    "max_glu_serum": max_glu_serum_map,
    "A1Cresult": A1Cresult_map,
    "diabetesMed": diabetesMed_map,

}




def save_prediction(raw_inputs, prediction):
    try:
        with closing(sqlite3.connect('predictions.db')) as conn:
            c = conn.cursor()
            
            columns_str = ', '.join(raw_inputs.keys())
            placeholders = ', '.join(['?'] * (len(raw_inputs) + 1))  # +1 for prediction
            values = list(raw_inputs.values()) + [prediction]
            
            c.execute(f'''
                INSERT INTO predictions 
                ({columns_str}, prediction)
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
    except Exception as e:
        print("Error saving to database:", e)







# 🌐 Routes

@app.route('/')
def home():
    """Render form with friendly dropdowns for categorical inputs."""
    return render_template('index.html', columns=columns)

@app.route('/predict', methods=['POST'])
def predict():
    """Process form submission, map categories to numbers, predict and display result."""
    try:
        # Collect raw form inputs
        raw_inputs = {col: request.form.get(col) for col in columns}

        # Build numerical feature vector
        input_data = []
        for col in columns:
            if col in CATEGORY_MAPS:
                # Map category → numeric code
                mapped = CATEGORY_MAPS[col].get(raw_inputs[col])
                if mapped is None:
                    raise ValueError(f"Invalid option for {col}: {raw_inputs[col]}")
                input_data.append(mapped)
            else:
                # Numeric input (floats/integers)
                input_data.append(float(raw_inputs[col]))

        # Prediction
        final_input = np.array([input_data])
        prediction = model.predict(final_input)[0]



                # Save to database
        save_prediction(raw_inputs, int(prediction))



        return render_template('result.html', prediction=prediction)

    except Exception as e:
        print("Error during prediction:", e)
        return render_template('result.html', prediction="Error occurred during prediction.")
    




# 🔐 Admin login & register handler
@app.route('/admin_auth', methods=['POST'])
def admin_auth():
    action = request.form.get('action')  # signup or signin
    username = request.form.get('name').strip()
    password = request.form.get('password')


        # Validation

    with closing(sqlite3.connect('predictions.db')) as conn:
        c = conn.cursor()

        if action == 'signup':
            hashed_pw = generate_password_hash(password)
            try:
                c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
                flash('Admin registered successfully! Please login.', 'success')
                
            except sqlite3.IntegrityError:
                
                flash('Username already exists', 'danger')
                return redirect('/login')


        elif action == 'signin':
            c.execute("SELECT password FROM admin WHERE username = ? ", (username,))
            user = c.fetchone()
            if user and check_password_hash(user[0], password):
                session['admin'] = username
                flash('Login successful', 'success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid credentials', 'danger')
                return redirect('/login')

    return redirect('/login')

# 👤 Login Page
@app.route('/login')
def login():
    return render_template('login.html')


# 📊 Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash("You must be logged in to access the dashboard.", "warning")
        return redirect('/login')
    
     
    powerbi_link = "https://app.powerbi.com/reportEmbed?reportId=f2c6e5e6-ddc6-4f48-953b-effe02c71a26&autoAuth=true&ctid=1ea77eb9-a85b-4e25-9948-f1aecbfe3b6d"
    
    return f"""
    <h2>Welcome, {session['admin']}! This is the Admin Dashboard.</h2>
    <p><a href="{powerbi_link}" target="_blank">View Power BI Dashboard</a></p>
    <iframe width="100%" height="600" src="{powerbi_link}" frameborder="0" allowFullScreen="true"></iframe>
    """


    #return f"Welcome, {session['admin']}! This is the Admin Dashboard."

# 🚪 Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Logged out successfully.", "info")
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
