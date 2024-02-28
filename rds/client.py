import os, traceback, psycopg2, psycopg2.extras

# os.environment['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

class OcdDB:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(dbname=DB_NAME, user=USER, password='', host=DB_ENDPOINT, port=DB_PORT)
        print('db connection is ready')

        self.nt_cur = self.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        print('DB cursor is ready')

    def get_records(self):
        try:
            q = 'SELECT * FROM transaction_details'
            nt_cur = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            nt_cur.execute(q)
            result = nt_cur.fetchall()
            nt_cur.close()
            return result
        except Exception as e:
            print(traceback.print_exc())
            print(e)

    def track_record(self, reference):
        try:
            q = f"SELECT * FROM transaction_details WHERE reference_id='{reference}' LIMIT 1"
            nt_cur = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            nt_cur.execute(q)
            result = nt_cur.fetchall()
            nt_cur.close()
            return result
        except Exception as e:
            print(traceback.print_exc())
            print(e)
            return False

    def insert_record(self, 
                      status, 
                      pay_to, 
                      pay_conf, 
                      payer_acc, 
                      payer_acc_conf, 
                      ifsc, 
                      ifsc_conf, 
                      amt, 
                      amt_conf, 
                      date_issued, 
                      date_status, 
                      micr, 
                      micr_conf, 
                      micr_status, 
                      micr_pin, 
                      micr_bank, 
                      micr_branch, 
                      conf, 
                      cheque, 
                      json_data,
                      sign_present,
                      sign_count,
                      payee_name,
                      payee_account,
                      contact_number, reference):
        try:
            q = f"INSERT INTO transaction_details (status, pay_to, pay_conf, payer_acc, payer_acc_conf, ifsc, ifsc_conf, amt, amt_conf, date_issued, date_status, micr, micr_conf, micr_status, micr_pin, micr_bank, micr_branch, conf, cheque, json_data, signature_check, signature_count, payee_input_name, payee_account, contact_number, reference_id) VALUES('{status}', '{pay_to}', {pay_conf}, '{payer_acc}', {payer_acc_conf}, '{ifsc}', {ifsc_conf}, '{amt}', {amt_conf}, '{date_issued}', '{date_status}', '{micr}', {micr_conf}, '{micr_status}', '{micr_pin}', '{micr_bank}', '{micr_branch}', {conf}, '{cheque}', '{json_data}', {sign_present}, {sign_count}, '{payee_name}', '{payee_account}', '{contact_number}', '{reference}')"

            print(q)

            nt_cur =self.conn.cursor()
            results = nt_cur.execute(q)
            self.conn.commit()
            nt_cur.close()
            return results
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            return False

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
