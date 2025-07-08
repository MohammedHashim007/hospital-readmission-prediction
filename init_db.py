import sqlite3

def init_db():
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    
    # Create predictions table
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  prediction INTEGER,
                  gender TEXT,
                  age REAL,
                  admission_type_id TEXT,
                  discharge_disposition_id TEXT,
                  admission_source_id TEXT,
                  time_in_hospital REAL,
                  num_lab_procedures REAL,
                  num_procedures REAL,
                  num_medications REAL,
                  diag_1 REAL,
                  diag_2 REAL,
                  diag_3 REAL,
                  number_diagnoses REAL,
                  max_glu_serum TEXT,
                  A1Cresult TEXT,
                  metformin REAL,
                  glipizide REAL,
                  glyburide REAL,
                  insulin REAL,
                  change TEXT,
                  diabetesMed TEXT,
                  service_utilization REAL,
                  Asian REAL,
                  Caucasian REAL,
                  Hispanic REAL,
                  Other REAL)''')
                 

    # Create admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )''')
             


    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized!")