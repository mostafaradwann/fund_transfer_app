
from main import app
import unittest
import io
from io import BytesIO
import pandas as pd
import string
import random
import json


class TransferAppTest(unittest.TestCase):

    def setUp(self):
        #use test client
        self.app = app.test_client()
        self.app.testing = True
    
    def test_show_accounts(self):
        headers = {'Accept': 'application/json'} 
        response = self.app.get('/accounts', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list, "invalid format")

    @staticmethod
    def random_id():
        count = 20
        all_char = string.ascii_letters + string.digits
        chars_count = len(all_char)
        random_id = []
        while count > 0:
            random_num = random.randint(0,chars_count - 1)
            random_charchter = all_char[random_num]
            random_id.append(random_charchter)

            count -= 1
        
        random_id = "".join(random_id)
        return random_id

    def test_csv_import(self):
        csv_data = f"""ID,Name,Balance
        {self.random_id()},John Mariston,1000.0
        {self.random_id()},Jane Megaston,4040.44"""

        response = self.app.post("/accounts/import", data={'file': (BytesIO(csv_data.encode('utf-8')), "test.csv")})
        self.assertEqual(response.status_code, 200, "CSV import failed")

    def test_excel_import(self):
        df = pd.DataFrame({
            "id" : [f"{self.random_id()}", f"{self.random_id()}"],
            "name" : ["John Don", "Jane Smith"],
            "balance" : [4404.4, 1002.22]
        })

        excel_file = "test.xlsx"
        df.to_excel(excel_file, index=False)
        response = self.app.post("/accounts/import", data={'file' : (excel_file, "test.xlsx")})
        self.assertEqual(response.status_code, 200, "excel file import faild")

    def test_empty_file(self):
        response = self.app.post("/accounts/import", data={'file' : ""})
        self.assertEqual(response.status_code, 404)
        response = self.app.post("/accounts/import", data={})
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        transfer_data = {
            "credited_account_id": "invalid-id",
            "debited_account_id": "invalid-id",
            "amount": 500
        }
        response = self.app.post('/transfer', data=transfer_data)
        self.assertEqual(response.status_code, 404)



    def test_get_account_by_id(self):
        account_id = "4b69e973-b77d-4b4f-be4b-5927b70669ba"
        response = self.app.get(f'/account/{account_id}')
        self.assertEqual(response.status_code, 200, "Invalid ID")
        data = json.loads(response.data)
        self.assertIsInstance(data, list, "invalid format")

    def test_transfer(self):
        transfer_data = {
            "credited_account_id": "a59db1b5-0e2a-46e6-add9-97727dc4a841",
            "debited_account_id": "cb1065d8-419f-4e41-bf23-7a221ff17465",
            "amount": 10
        }
        
        response = self.app.post("/transfer", data=transfer_data)
        self.assertEqual(response.status_code, 200)


    def test_insufficient_amount(self):
        credited_id = "cb1065d8-419f-4e41-bf23-7a221ff17465"
        debited_account_id = "a59db1b5-0e2a-46e6-add9-97727dc4a841"
        amount = "10000"
        response = self.app.post('/transfer', data={
            'credited_account_id': credited_id,
            'debited_account_id': debited_account_id,
            'amount': amount
        })
        
        self.assertEqual(response.status_code, 400)
        # Check the response content, assuming it returns a JSON response
        response_data = response.get_json()
        self.assertEqual(response_data['message'], "Insufficient balance for the transfer")


if __name__ == "__main__":
    unittest.main()

