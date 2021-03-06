# -*- coding: utf-8 -*-
"""
Bot SNIIM v.1.0


@author: Wilfrido J Paredes
"""

#La estructura de datos para el manejo de la información. Es el corazón y cerebro del bot.
import market_products_structure as mps

import datetime
import pickle
import time
import re


"""
download sniim
    Input: 
        ids -- Número entre 0 y 45 de acuerdo a nuestra listas de mercados. Por ejemplo Qro es el 28.
        day -- Día inicial de la búsqueda, si no se proporciona se iniciará en 2009-01-01
        max_tries -- A veces hay falla al realizar la petición por razones externas al SNIIM, entonces el sistema lo vuelve a intentar, por default hasta 5 veces más
        time_delay -- Tiempo de espera entre intento e intento, por default 5 segundos
    Output: Día alcanzado
"""

def download_sniim(ids, day=None, max_tries = 4, time_delay = 5):
    if day is None:
        day = datetime.datetime(2009, 1, 1)
    
    market_ids = mps.load_market_database().loc[ids]
    end_day = datetime.datetime(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)

    while day <= end_day:
        print(day)
        #Market_data es la información ya en nuestro poder, arroja 0 si no existe información alguna
        market_data = mps.load_market_information(ids)
        
        #Market_name es el nombre con el que se identifica el mercado actual de consulta
        try:
            market_name= re.findall(r'[Mm]erca.*', market_ids.Mercado)[0]
        
        except:
            market_name= re.findall(r'[Cc]entr.*', market_ids.Mercado)[0]
        
        if isinstance(market_data, int):
            
            market_obj = mps.market(market_name, day)
            market_obj.make_logs()
    
            day_data = mps.get_day(market_ids,day.strftime('%d/%m/%Y'))
            market_obj.add_record(day_data)
            market_obj.make_records()
            
            f = open(str(ids)+'/information.gdata','wb')
            pickle.dump(market_obj, f)
            f.close()
            
            day = mps.next_day(day)
            
        else:
            market_obj = pickle.load(market_data)
            market_obj.make_logs(day)
            
            status = 0
            number_try = 1
            while (status == 0) and (number_try < max_tries):
                try:
                    day_data = mps.get_day(market_ids,day.strftime('%d/%m/%Y'))
                    status = 1
                except:
                    print("Upss! Algo salió mal, volveré a intentar. Intento no. "+str(number_try))
                    number_try += 1
                    time.sleep(time_delay)
            
            if status == 1:
                market_obj.add_record(day_data)
                market_obj.make_records()
                f = open(str(ids)+'/information.gdata','wb')
                pickle.dump(market_obj, f)
                f.close()
                
            day = mps.next_day(day)
    return end_day


def main():
    try:
        while True:
            print("Este bot se puede detener con CTRL+C.\n")
            for i in range(45):
                try:
                    market_data = mps.load_market_information(i)
                    if not isinstance(market_data, int):
                        thereisdata = True
                    else:
                        thereisdata = False
                except:
                    print("Algo falló")                    
                    
                
                if thereisdata:
                    print("\nSe intentará poner al día al mercado "+str(i+1)+'\n')
                    today_day = datetime.datetime(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
                    market_obj = pickle.load(market_data)
                    
                    if (market_obj.status == 0) and (today_day >= market_obj.last_update):
                        download_sniim(i, day=market_obj.last_update)
                        print("\nSe puso al día al mercado "+str(i+1)+'\n')
                    elif (market_obj.status == 1) and (today_day > market_obj.last_update):
                        download_sniim(i, day=market_obj.last_update+datetime.timedelta(days=1))
                        print("\nSe puso al día al mercado "+str(i+1)+'\n')
                    else:
                        print("\nEl mercado "+str(i+1)+' está al día, se volverá a intentar en 24 hrs.\n')
                else:
                    print('El mercado '+str(i+1)+' se iniciará a descargar')
                    download_sniim(i)
            
            time.sleep(86400)
    except KeyboardInterrupt:
        pass
            
main()