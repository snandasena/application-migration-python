import csv
import json
import logging
from threading import Thread

import math
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename='../logs/rest-migrate.log', filemode='w')

vasabi_root = 'https://run.mocky.io/'

wallet_root = "https://run.mocky.io/"

vasabi_headers = {'Content-type': 'application/json'}

wallet_headers = {'Content-type': 'application/json'}

vasabi_username = 'tdte'
vasabi_password = 'vcbcbvcbcvb'

wallet_username = 'test'
wallet_password = 'test'

wallet_token = "test"

wallet_headers['Authorization'] = wallet_token

csv_file_name = '../data/sample.csv'

# Actions
wallet_customer_creation = 'wallet_customer_creation'
wallet_creation = 'wallet_creation'
wallet_money_transfer = 'wallet_money_transfer'
vasabi_chargin = 'vasabi_chargin'

cache = {}


def post(url, post_data, headers):
    try:
        return requests.post(url=url, data=json.dumps(post_data), headers=headers)

    except Exception as e:
        print(e)


def vasabi_authenticate():
    vasabi_headers['username'] = vasabi_username
    vasabi_headers['password'] = vasabi_password
    url_vasabi_login = vasabi_root + 'v3/e34a3479-ad0f-4eed-b2ec-92263d643571'
    v_res = post(url_vasabi_login, {}, vasabi_headers)
    json_res = json.loads(v_res.text)
    return json_res['data']['access_token']


def process(row_data, worker_id):
    create_wallet_customer_queue = []
    create_wallet_queue = []
    transfer_credit_to_wallet_queue = []
    total_tasks = len(row_data)
    print("total works : {}".format(total_tasks))

    def create_wallet_customer():
        total_t_tasks = 0

        for data in row_data:
            create_cum_json = {
                "mobile": str(data[0]).strip(),
                "NIC": str(data[1]).strip(),
                "isActive": True,
                "source": "SMS"
            }

            url_customer = wallet_root + 'v3/4292be6e-51da-48d9-92b1-e7b679aa2b85'
            w_create_cus_res = post(url_customer, create_cum_json, wallet_headers)

            create_wal_cus_res = json.loads(w_create_cus_res.text)
            print(create_wal_cus_res)
            if 'isActive' in create_wal_cus_res or 'description' in create_wal_cus_res:
                if 'isActive' in create_wal_cus_res:

                    log_message = str(data[0]) + ' | ' + str(data[1]) + ' | ' + str(
                        data[2]) + '| {} | {}'.format(
                        wallet_customer_creation, create_wal_cus_res['isActive'])

                    logging.info(log_message)

                if 'description' in create_wal_cus_res:
                    log_message = str(data[0]) + ' | ' + str(data[1]) + ' | ' + str(
                        data[2]) + '| {} | {}'.format(
                        wallet_customer_creation, create_wal_cus_res['description'])

                    logging.info(log_message)

            create_wallet_customer_queue.append(data)

            total_t_tasks = total_t_tasks + 1

        print("worker[{}] total create_wallet_customer tasks : {}".format(worker_id, total_t_tasks))

    def create_wallet():
        total_t_tasks = 0
        while True:
            if len(create_wallet_customer_queue) != 0:
                data = create_wallet_customer_queue.pop()

                wallet_create_json = {
                    'mobileNo': str(data[0]).strip()
                }
                # url_wallet = wallet_root + 'web/wallet'
                url_wallet = wallet_root + 'v3/f79f5088-33d9-4ac1-972b-dbb3db86e328'

                w_create_res = post(url_wallet, wallet_create_json, wallet_headers)

                create_wallet_res = json.loads(w_create_res.text)
                print(create_wallet_res)

                if 'accountNo' in create_wallet_res or 'description' in create_wallet_res:
                    if 'accountNo' in create_wallet_res:
                        log_message = str(data[0]) + ' | ' + str(data[1]) + ' | ' + str(data[2]) + '| {} | {}'.format(
                            wallet_creation, create_wallet_res['accountNo'])
                        logging.info(log_message)

                    if 'description' in create_wallet_res:
                        log_message = str(data[0]) + ' | ' + str(data[1]) + ' | ' + str(data[2]) + '| {} | {}'.format(
                            wallet_creation, create_wallet_res['description'])
                        logging.info(log_message)

                create_wallet_queue.append(data)

                total_t_tasks = total_t_tasks + 1

            if total_t_tasks == total_tasks:
                break

        print("worker[{}] total create_wallet tasks : {}".format(worker_id, total_t_tasks))

    def transfer_credit_to_wallet():
        total_t_tasks = 0
        while True:
            if len(create_wallet_queue) != 0:
                data = create_wallet_queue.pop()

                transfer_money_json = {
                    "amount": str(data[2]).strip(),
                    "description": "Wallet migration"
                }

                # url_transfer = wallet_root + 'web/wallet/' + str(data[0]).strip() + '/money-transfer'
                url_transfer = wallet_root + 'v3/bffd85f5-bf6b-4594-a344-eb6de5e1c52d'
                w_transfer_res = post(url_transfer, transfer_money_json, wallet_headers)

                transfer_credit_res = json.loads(w_transfer_res.text)
                print(transfer_credit_res)

                if 'status' in transfer_credit_res:
                    log_message = str(data[0]) + ' | ' + str(data[1]) + ' | ' + str(data[2]) + '| {} | {}'.format(
                        wallet_money_transfer, transfer_credit_res['status'])
                    logging.info(log_message)

                if transfer_credit_res['status'] == 'Success':
                    data.append(1)
                else:
                    data.append(0)

                transfer_credit_to_wallet_queue.append(data)
                total_t_tasks = total_t_tasks + 1

            if total_t_tasks == total_tasks:
                break

        print("worker[{}] total transfer_credit_to_wallet tasks : {}".format(worker_id, total_t_tasks))

    def charge_vasabi():
        total_t_tasks = 0
        while True:
            if len(transfer_credit_to_wallet_queue) != 0:
                data = transfer_credit_to_wallet_queue.pop()

                if data[3] == 1:
                    charge_vasabi_json = {
                        "mobile": str(data[0]).strip(),
                        "amount": str(data[2]).strip(),
                        "app_id": 100,
                        "method": "wallet",
                        "comment": "live data migration"
                    }

                    if 'vas_token' not in cache:
                        cache['vas_token'] = vasabi_authenticate()

                    vasabi_headers['access_token'] = cache['vas_token']
                    url_vasabi_chargin = vasabi_root + 'v3/bffd85f5-bf6b-4594-a344-eb6de5e1c52d'
                    v_charge_res = post(url_vasabi_chargin, charge_vasabi_json, vasabi_headers)

                    charge_vas = json.loads(v_charge_res.text)
                    print(charge_vas)

                    if 'status' in charge_vas:
                        log_message = str(data[0]) + ' | ' + str(data[1]) + ' | ' + str(data[2]) + '| {} | {}'.format(
                            vasabi_chargin, charge_vas['status'])
                        logging.info(log_message)

                    total_t_tasks = total_t_tasks + 1

            if total_t_tasks == total_tasks:
                break

        print("worker[{}] total charge_vasabi tasks : {}".format(worker_id, total_t_tasks))

    def init():
        t1 = Thread(target=create_wallet_customer)
        t1.start()

        t2 = Thread(target=create_wallet)
        t2.start()

        t3 = Thread(target=transfer_credit_to_wallet)
        t3.start()

        t4 = Thread(target=charge_vasabi)
        t4.start()

        t3.join()
        t1.join()
        t2.join()
        t4.join()

    # process init
    init()


def main(vasabi_data, chunk_size):
    totals_works = len(vasabi_data)
    num_of_workers = math.ceil(totals_works / chunk_size)
    jobs = []
    for w_id in range(num_of_workers):
        start = w_id * chunk_size
        end = start + chunk_size
        worker_tasks = vasabi_data[start:end]
        t = Thread(target=process(worker_tasks, w_id))
        t.start()
        jobs.append(t)

    for job in jobs:
        job.join()


if __name__ == '__main__':
    with open(csv_file_name, 'r', newline='') as data_csv:
        vasabi_data = csv.reader(data_csv, delimiter=',')
        main(list(vasabi_data), 4)
