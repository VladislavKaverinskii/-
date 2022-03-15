
ebay_submit_options = config(filename='odoo.conf', section="EbaySubmitOptions")
odoo_conf = config(filename='odoo.conf', section='options')
job_timeout = odoo_conf['limit_time_real']
enable_log = odoo_conf['enable_log']
time_for_exec = datetime.datetime.now() + datetime.timedelta(seconds=int(job_timeout) - 30)

conn = None
try:
    params = config()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()

    while datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") < time_for_exec.strftime("%Y-%m-%d %H:%M:%S"):
        cursor.callproc('external."spAppGeteBayProductsPage"')
        total = 0
        for record in cursor:
            product = {
                "availability": {
                    "shipToLocationAvailability": {
                        "quantity": int(record[5])
                    }
                },
                "condition": "NEW",
                "product": {
                    "title": str(record[13])[:79],
                    "description": str(record[11]),
                    "aspects": {
                        "Type": [
                            str(record[14])
                        ],
                    },
                    "upc": [str(record[1])],
                    "imageUrls": [
                        str(record[12])
                    ],

                }
            }

            product = json.dumps(product)
            response = None
            err_counter = 0
            is_pushed = False
            if datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") >= time_for_exec.strftime(
                    "%Y-%m-%d %H:%M:%S"):
                _logger.info(
                    'Timeout for downloading buy box prices reached after {}s.'.format(int(job_timeout) - 30))
                break
            while response is None and err_counter < 100:
                response, is_pushed = self.make_request(record, product, self._get_http_headers())
                err_counter += 1
            if is_pushed:
                total += 1
                _logger.info(total)
            if total >= int(ebay_submit_options['number_submit_products']):
                break

    conn.commit()
    cursor.close()
except (Exception, psycopg2.DatabaseError) as error:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    _logger.error(str(error) + '. line:' + str(exc_tb.tb_lineno))
finally:
    if conn is not None:
        conn.close()