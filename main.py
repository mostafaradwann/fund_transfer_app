#Create App for transfer money
# Import from CSV files, at /account/import
# List All Account , /accounts
# GET an account inforamtion, /account<id>
# transfer funds, at /transfer


from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("home.html", pagetitle="Home")

# @app.route('/accounts/import', method=['POST'])
# def import_accounts():
#     pass

# @app.route("/accounts", method=["GET"])
# def get_all_accounts():
#     pass

@app.route("/account/<id>")
def get_account_by_id(id):
    return f"the Id, {id}"

# @app.route("/transfer", method=["POST"])
# def transfer_fund():
#     pass

if __name__ == "__main__":
    app.run(debug=True, port=9000)






