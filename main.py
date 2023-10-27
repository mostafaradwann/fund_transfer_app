#Create App for transfer money
# Import from CSV files, at /account/import
# List All Account , /accounts
# GET an account inforamtion, /account<id>
# transfer funds, at /transfer
from flask import Flask, jsonify, request, render_template
import sqlite3
import csv
import codecs
import pandas as pd

app = Flask(__name__)

#database connection function
def db_connection():
    db = None
    try:
        db = sqlite3.connect("accounts.db")
        cr = db.cursor()

    except sqlite3.error as e:
        print(e)
    return db, cr

@app.route('/')
def homepage():
    return render_template("home.html", pagetitle="Home")

db, cr = db_connection()
@app.route('/accounts/import', methods=['POST'])
def import_accounts():
    db, cr = db_connection()
    
    if 'file' not in request.files:
        return "no file in request"
    
    file = request.files['file']

    if file.filename == '':
        return " no Selected file"
    
    #variable to store accounts data
    accounts = []
    if file:
        filename = file.filename
        if filename.endswith('.csv'):
            
            csv_reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'), delimiter=",")

            #add data to the accounts list
            for row in csv_reader:
                accounts.append({
                    "id" : row["ID"],
                    "name" : row["Name"],
                    "balance" : row["Balance"]
                })

        elif filename.lower().endswith(('.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt')):
            df = pd.read_excel(file)
            df.columns = map(str.lower, df.columns)  
            data = df.to_dict(orient='records')
            accounts.extend(data)
            #add data to the accounts list

        sql_query = "INSERT INTO accounts ('id', 'name', 'balance') values(?,?,?)"
        try:
            # Begin a transaction
            db.execute('BEGIN TRANSACTION')

            for account in accounts:
                cr.execute(sql_query, (account['id'], account['name'], account['balance']))

            # Commit the transaction
            db.commit()
        
        except sqlite3.Error as e:
            db.rollback()  # Roll back the transaction in case of an error
            print(e)

        finally:
            db.close()  # Always close the database connection
        return jsonify(accounts)
            


@app.route("/accounts", methods=["GET"])
def get_all_accounts():
    db, cr = db_connection()
    if request.method == "GET":
        cr.execute("SELECT * From accounts")
        rows = cr.fetchall()
        accounts = [
            dict(id = row[0], name = row[1], balance = row[2])
            for row in rows
        ]
        db.close()
        if accounts is not None:
            return jsonify(accounts)
    


# @app.route("/account/<id>", methods=["GET"])
# def get_account_by_id(id):
#     if request.method == "GET":
#         for account in accounts_list:
#             if account['id'] == id:
#                 return jsonify(account)

# @app.route("/transfer", methods=["POST"])
# def transfer_fund():
#     pass

if __name__ == "__main__":
    app.run(debug=True, port=9000)






