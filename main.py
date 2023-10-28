#Create App for transfering fund
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
    return render_template(
        "home.html", pagetitle="Home", 
        page_head="Transfer App", 
        page_description="Sending Money is Easier than you think")

db, cr = db_connection()
@app.route('/accounts/import', methods=['POST'])
def import_accounts():
    #call sqlite db variable and cursor varialbe
    db, cr = db_connection()
    
    #check if a file is in the request sent
    if 'file' not in request.files:
        return jsonify({"message" : "no file in request"}), 404
    
    #get the file from the request
    file = request.files['file']

    #check if the file exists and has a name
    if file.filename == '':
        return jsonify({"message" : "no Selected File"}), 404
    
    #variable to store accounts data
    accounts = []
    if file:

        filename = file.filename
        #check if the uploaded file is a CSV file
        if filename.lower().endswith('.csv'):
            #create a dictionary from the CSV file
            csv_reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'), delimiter=",")
            
            #append data of each row as dictionary to the accounts list variable
            for row in csv_reader:
                accounts.append({
                    "id" : row["ID"].strip(),
                    "name" : row["Name"].strip(),
                    "balance" : row["Balance"].strip()
                })
        #check if the uploaded file is an excel file (most excel extentions)
        elif filename.lower().endswith(('.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt')):
            try: 
                #create a dataframe from the EXCEL File
                df = pd.read_excel(file, engine="openpyxl")
                df.columns = map(str.lower, df.columns)
                #store each row of the dataframe as a dictionary  
                data = df.to_dict(orient='records')
                #add data to accounts list varaiable
                accounts.extend(data)
            except Exception as e:
                print("Error Reading excel file:", str(e))

    
        #insert accounts data to the database
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
            print("ERROR in Inserting to database:",e, "ID: ", account['id'])
            return render_template('import_result.html', response_code=400, error_message="File upload failed")

        finally:
            db.close()  # close database connection
        request_header = request.headers.get('Accept')
        if request_header == "application/json":
            return jsonify(accounts), 200

        return render_template('import_result.html', response_code=200, json_data=accounts)




@app.route("/accounts", methods=["GET"])
def get_all_accounts():
    #call db and cursor variables
    db, cr = db_connection()
    if request.method == "GET":
        #select all accounts data from database
        cr.execute("SELECT * From accounts")
        rows = cr.fetchall()
        # store the data as dict in accounts variable
        accounts = [
            dict(id = row[0], name = row[1], balance = row[2])
            for row in rows
        ]
        #close database connection
        db.close()
        request_header = request.headers.get('Accept')
        if request_header == "application/json":
            if accounts:
                return jsonify(accounts), 200
            else:
                return jsonify({"Message" : "No Accounts available in DB"}), 404
        
        return render_template("all_users.html", accounts=accounts)
        
                
    


@app.route("/account/<id>", methods=["GET"])
def get_account_by_id(id):
    #call db and cursor variables
    db, cr = db_connection()
    if request.method == "GET":
        # select all account data with ID
        cr.execute("SELECT * From accounts where id = ?", (id,))
        rows = cr.fetchall()
        # store the data as dict in account variable
        account = [
            dict(id = row[0], name = row[1], balance = row[2])
            for row in rows
        ]
        # close db connection
        db.close()
    
        if account:
            return jsonify(account), 200
        else:
            return jsonify({"Message" : f"The Account With ID {id} does not exist"}), 404

@app.route("/transfer", methods=["POST"])
def transfer_fund():
    #call sqlite db variable and cursor varialbe
    db, cr = db_connection()
    credited_account_id = request.form.get("credited_account_id")
    debited_account_id = request.form.get("debited_account_id")
    amount = float(request.form.get("amount"))

    #select the balance of the credited account usnig ID
    cr.execute("SELECT balance FROM accounts where id = ?", (credited_account_id,))
    credited_account_bal = cr.fetchone()
    
    #check if credited account with provided ID exists
    if credited_account_bal is None:
        return jsonify({"Message" : f"The account with ID{credited_account_id} does not exist"}), 404
    
    # Check if the debited account exists
    cr.execute("SELECT balance FROM accounts WHERE id = ?", (debited_account_id,))
    debited_account_bal = cr.fetchone()
    if debited_account_bal is None:
        return jsonify({"Message": f"Debited account with ID {debited_account_id} does not exist"}), 404

    #check if credited account has suffecient balance
    if credited_account_bal[0] < amount:
        return jsonify({"message" : "Insufficient balance for the transfer"}), 400

    #update the credited account balance 
    cr.execute("UPDATE accounts SET balance = round(balance - ?, 2) WHERE id = ?", (amount, credited_account_id,))
    #update the Debited account balance    
    cr.execute("UPDATE accounts SET balance = round(balance + ?, 2) WHERE id = ?", (amount, debited_account_id),)

    # Fetch the updated balances
    cr.execute("SELECT balance FROM accounts where id = ?", (credited_account_id,))
    credited_new_balance = cr.fetchone()[0]
    cr.execute("SELECT balance FROM accounts WHERE id = ?", (debited_account_id,))
    debited_new_balance = cr.fetchone()[0]
    #commit and close connection
    db.commit()
    db.close()
    request_header = request.headers.get('Accept')
    if request_header == "application/json":
        #return if the process was successfull
        return jsonify({"Message" : f" A Transfer of amount {amount} was sent to the account with ID '{debited_account_id}' From the account with ID '{credited_account_id}'"}), 200
    return render_template("transfer_result.html", credited_account_id=credited_account_id, debited_account_id=debited_account_id, amount=amount, credited_account_bal=credited_account_bal, debited_account_bal=debited_account_bal, credited_new_balance=credited_new_balance, debited_new_balance=debited_new_balance)



@app.route("/account", methods=["GET"])
def get_account_data_id():
    account_id = request.args.get('id')
    #call db and cursor variables
    db, cr = db_connection()
    if request.method == "GET":
        # select all account data with ID
        cr.execute("SELECT * From accounts where id = ?", (account_id,))
        rows = cr.fetchall()
        # store the data as dict in account variable
        account = [
            dict(id = row[0], name = row[1], balance = row[2])
            for row in rows
        ]
        # close db connection
        db.close()
        return render_template("user_by_id.html", account=account)



if __name__ == "__main__":
    app.run(debug=True, port=9000)






