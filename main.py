#Create App for transfer money
# Import from CSV files, at /account/import
# List All Account , /accounts
# GET an account inforamtion, /account<id>
# transfer funds, at /transfer


from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

accounts_list = [
    {
        "id" : "cc26b56c-36f6-41f1-b689-d1d5065b95af",
        "name" : "Joy Dean",
        "balance" :4497.22,
    },
    {
        "id" : "be6acfdc-cae1-4611-b3b2-dfb5167ba5fe",
        "name" : "Bryan Rice",
        "balance" :2632.76,
    },{
        "id" : "43caa0b8-76a4-4e61-b7c3-f2f5ee4b4f77",
        "name" : "Ms. Jamie Lopez",
        "balance" :1827.85,
    },{
        "id" : "69c93967-e20f-4735-9b8d-1b7dd56340ab",
        "name" : "Lauren David",
        "balance" :9778.7,
    },
]

@app.route('/')
def homepage():
    return render_template("home.html", pagetitle="Home")

# @app.route('/accounts/import', methods=['POST'])
# def import_accounts():
#     pass

@app.route("/accounts", methods=["GET"])
def get_all_accounts():
    if request.method == "GET":
        if len(accounts_list) > 0:
            return jsonify(accounts_list)


@app.route("/account/<id>", methods=["GET"])
def get_account_by_id(id):
    if request.method == "GET":
        for account in accounts_list:
            if account['id'] == id:
                return jsonify(account)

# @app.route("/transfer", methods=["POST"])
# def transfer_fund():
#     pass

if __name__ == "__main__":
    app.run(debug=True, port=9000)






