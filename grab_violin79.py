
#-*- coding: utf-8 -*-
from naver_cafe import naver_cafe, naver_dn,  LoginPage
from naver_log import configure_logger
from optparse import OptionParser
from pyvirtualdisplay import Display
import json, sys, os

def read_config(_fname):
    with open(_fname, 'rt') as f:
        cnf = json.load(f)
    return cnf




if __name__ =="__main__":

    display = Display(visible=0, size=(1280,1024))
    display.start()
    parser = OptionParser(usage="usage : %prog [option] filename",
                          version ="%prog 1.0")
    parser.add_option("-c", "--config",
                      action='store',
                      dest='cnf_file',
                      default='naver_cafe_cnf.json',
    help='create a cssfile')

    (options, args) = parser.parse_args()
    print(options)

    CONFIG = read_config(options.cnf_file)
    for key, i in CONFIG.items():
        print(key,i)

    logger = configure_logger('default', 'logging_config.json')

    drv = naver_cafe('firefox',  CONFIG['CAFE_ID'] )
    drv.goto_cf_menu(CONFIG['MENU_NAME'])


    dwnld = naver_dn() 
    drv.search_q(searchBy=CONFIG['Q_type'], keyword=CONFIG['Q_kwd'],date=CONFIG['Q_date'])

    df = drv.get_lst_whole_bulletin()


    lst_success = [] 
    for i in df.Addr.tolist():
        drv.get(i)
        try:
            _l = drv.download_in_page(CONFIG['DN_FOLDER'])
            lst_success.append(_l)
        except:
            logger.error('Download Error'+ _l)
            pass

    print('\n---- Download is completed ------')
    logger.info('successed')

    display.stop() 
