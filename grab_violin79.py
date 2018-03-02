
#-*- coding: utf-8 -*-
from naver_cafe import naver_cafe, naver_dn,  LoginPage
from naver_log import configure_logger
from optparse import OptionParser
import json, sys, os


def read_config(_fname):
    with open(_fname, 'rt') as f:
        cnf = json.load(f)
    return cnf




if __name__ =="__main__":
    parser = OptionParser(usage="usage : %prog [option] filename",
                          version ="%prog 1.0")
    parser.add_option("-c", "--config",
                      action='store', # -c �뿉 대�븳 args  諛쏆쓣 �븣
                      dest='cnf_file', # args媛� 저�옣�맆 蹂��닔
                      default='naver_cafe_cnf.json',
help='create a cssfile')
    (options, args) = parser.parse_args()

    # if  len(args) !=1:
    #     parser.error('Wrong number of arguments')
    print(options)

    CONFIG = read_config(options.cnf_file)
    logger = configure_logger('default', 'logging_config.json')

    drv = naver_cafe('firefox',  CONFIG['CAFE_ID'] )
    drv.goto_cf_menu(CONFIG['MENU_NAME'])


    dwnld = naver_dn() # �떎�슫濡쒕뱶 媛앹껜 �깮�꽦
    drv.search_q(searchBy=CONFIG['Q_type'], keyword=CONFIG['Q_kwd'],date=CONFIG['Q_date'])

    df = drv.get_lst_whole_bulletin()


    lst_success = [] #�떎�슫濡쒕뱶 �셿猷뚮맂 �뙆�씪紐⑸줉, 寃뚯떆�뙋 �젣紐�
    for i in df.Addr.tolist():
        drv.get(i)
        try:
            _l = drv.download_in_page(CONFIG['DN_FOLDER'])
            lst_success.append(_l)
        except:
            logger.error('Download Error')
            drv.logger.error('Download Error'+ _l)

    print('\n---- Download is completed ------')
    logger.info('successed')
