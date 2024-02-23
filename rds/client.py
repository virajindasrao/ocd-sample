import os, traceback, psycopg2, psycopg2.extras

DB_ENDPOINT = "hackathon2024.c9gg4u0cqaxq.us-east-1.rds.amazonaws.com"
DB_PORT = "5432"
USER = "postgres"
REGION = "us-east-1"
DB_NAME = "ocdDb"
# os.environment['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

class OcdDB:
    def __init__(self) -> None:
        print("asasd , ", os.getenv('dbpassword'))
        self.conn = psycopg2.connect(dbname=DB_NAME, user=USER, password='Hackathon2024$', host=DB_ENDPOINT, port=DB_PORT)
        print('db connection is ready')

        self.nt_cur = self.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        print('DB cursor is ready')

    def get_records(self):
        try:
            q = 'SELECT * FROM transaction_details'
            nt_cur = self.conn.cursor()
            nt_cur.execute(q)
            result = nt_cur.fetchall()
            nt_cur.close()
            return result
        except Exception as e:
            print(traceback.print_exc())
            print(e)

    def insert_record(self, status, pay_to, pay_conf, payer_acc, payer_acc_conf, ifsc, ifsc_conf, amt, amt_conf, date_issued, date_status, micr, micr_conf, micr_status, micr_pin, micr_bank, micr_branch, conf, cheque, json_data):
        try:
            q = f"INSERT INTO transaction_details (status, pay_to, pay_conf, payer_acc, payer_acc_conf, ifsc, ifsc_conf, amt, amt_conf, date_issued, date_status, micr, micr_conf, micr_status, micr_pin, micr_bank, micr_branch, conf, cheque, json_data) VALUES('{status}', '{pay_to}', '{pay_conf}', '{payer_acc}', '{payer_acc_conf}', '{ifsc}', '{ifsc_conf}', '{amt}', '{amt_conf}', '{date_issued}', '{date_status}', '{micr}', '{micr_conf}', '{micr_status}', '{micr_pin}', '{micr_bank}', '{micr_branch}', '{conf}', '{cheque}', '{json_data}')"

            print(q)

            nt_cur =self.conn.cursor()
            results = nt_cur.execute(q)
            self.conn.commit()
            nt_cur.close()
            return results
        except Exception as e:
            print(e)
            print(traceback.print_exc())

    def update_status(self, id, status):
        try:
            q = f"UPDATE transaction_details SET status='{status}' WHERE trasaction_id='{id}'"
            nt_cur =self.conn.cursor()
            results = nt_cur.execute(q)
            self.conn.commit()
            nt_cur.close()
            return results            
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            return False

    def update_record(self, id, pay_to, issued_on, payer_acc, amt, ifsc, micr_pin, micr_bank, micr_branch):
        try:
            q = f"UPDATE transaction_details SET pay_to='{pay_to}', pay_conf='100', date_issued='{issued_on}', payer_acc='{payer_acc}', payer_acc_conf='100', amt='{amt}', amt_conf='100', ifsc='{ifsc}', ifsc_conf='100', micr_pin='{micr_pin}', micr_bank='{micr_bank}', micr='{micr_branch}', micr_conf='100', conf='100' WHERE trasaction_id='{id}'"
            print(q)
            nt_cur =self.conn.cursor()
            results = nt_cur.execute(q)
            print(results)
            self.conn.commit()
            nt_cur.close()

            return True
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            return False
