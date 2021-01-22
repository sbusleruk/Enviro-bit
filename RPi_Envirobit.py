
import serial
from time import sleep
import time
import datetime as dt
import datetime
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import mariadb
import sys
import mpld3
from datetime import datetime

###################################
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('info.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

logger.info('See the info.log file')
############################################


## Edit the line below to the correct port
PORT = "/dev/ttyACM0"  ##NOT PORT = "/dev/ttyAMA0"

s = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
#Not 9600 ???
BAUD = 115200
#s = serial.Serial(PORT)
#s.baudrate = BAUD
s.parity   = serial.PARITY_NONE
s.databits = serial.EIGHTBITS
s.stopbits = serial.STOPBITS_ONE

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="*****************",
        password="*******************",
        host="127.0.0.1",
        port=3306,
        database="envirobit"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    logger.info(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()
x = 0

# Create figure for plotting
xs = []
ys = []
ys_hum = []
ys_pres = []
labels = []
ys_light = []
start_time = dt.datetime.now().strftime('%A, %H:%M:%S')
log_time = dt.datetime.now().strftime('%H:%M:%S')
def writehtml():     
    fig = plt.figure()
    ax = fig.add_subplot(111)

    mariadb_connection = mariadb.connect(user='*******', password='****************', database='envirobit')

    cur = mariadb_connection.cursor()
    cur.execute("SELECT * FROM ( SELECT * FROM sensors ORDER BY TimeValue DESC LIMIT 4400 ) sub ORDER BY TimeValue ASC")

    #data = []
    #xTickMarks = []

    xs = []
    ys = []
    ys_hum = []
    ys_pres = []
    labels = []
    ys_light = []
    for row in cur.fetchall():

        xs.append(str(row[3])   )
        ys.append( float(row[0]) )
        ys_hum.append( float(row[1]) )
        ys_pres.append( float(row[2]) )
        
 #   mariadb_connection.close()

    start_time = xs[0]
    write_time = xs[-1]

    #from datetime import datetime

    date_time_str = start_time
    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

    # current date and time
    now = datetime.now()
    now = date_time_obj

    t = now.strftime("%H:%M:%S")

    s1 = now.strftime("%m/%d/%Y, %H:%M:%S")

    # mm/dd/YY H:M:S format

    s2 = now.strftime("%d/%m/%Y, %H:%M:%S")
    # dd/mm/YY H:M:S format

    #######
    date_time_obj = datetime.strptime(write_time, '%Y-%m-%d %H:%M:%S')
    now = date_time_obj
    s3 = now.strftime("%d/%m/%Y, %H:%M:%S")

    write_html_time = datetime.now()

    print('starting writehtml', str(write_html_time))
    logger.info('starting writehtml')
    # Create figure for plotting

    try:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 9))
        fig.tight_layout(pad=3)
        ax1.plot(xs, ys)
        ax1.set(title='Temperature over Time: ' + str(s2) + ' to ' + str(s3), ylabel='Temp', xlabel='Time')
        ax1.xaxis.set_major_locator(plt.MaxNLocator(4))
        log_time = dt.datetime.now().strftime('%H:%M:%S')
        logger.info('1st plot finished')        
        print( '1st plot finished', log_time )
    except:
        logger.warning('1st plot fin - except route')   
        print ('1st plot fin - except route')
        pass
    try:
        ax2.plot(xs, ys_hum)
        ax2.set(title='Humidity', ylabel='Humidity' )
        ax2.xaxis.set_major_locator(plt.MaxNLocator(5))
        log_time = dt.datetime.now().strftime('%H:%M:%S')
        logger.info('2nd plot finished') 
        print( '2nd plot finished', log_time )
    except:
        logger.warning('2nd plot fin - except route') 
        print ('2nd plot fin - except route')
    ax3.plot(xs, ys_pres)
    ax3.set(title='Pressure', ylabel='Pressure', xlabel='Time')
    ax3.xaxis.set_major_locator(plt.MaxNLocator(4))

    try:
        log_time = dt.datetime.now().strftime('%H:%M:%S')
        logger.info('3rd plot finished')         
        print( '3rd plot finished', log_time )
    except:
        logger.warning('3rd plot fin - except route')         
        print ('3rd plot fin - except route')

    fig.tight_layout()
    fig.savefig('//var//www//html//my_plot.png')

    log_time = dt.datetime.now().strftime('%H:%M:%S')
    print( 'saving fig:', log_time )
    logger.info('saving fig:')         
    
    #plt.close(fig)

    #plt.show()

    plt.close('all')


def rewrite():
    for t in range(0, 600):
        data = s.readline().decode('UTF-8') 
    #    data_list = data.rstrip().split(' ')
        data_list = data.rstrip().split( )
        y = list(data_list)
        print (y)
        try:
            result = [float(x.strip('')) for x in y]
            y = result
        except:
            log_time = dt.datetime.now().strftime('%H:%M:%S')
            print ('inconsistent data, moving on: ', log_time)
            logger.warning('inconsistent data, moving on: ')              
            #y = y_prev
            #continue 
        #y_prev = y'
        if len(y) < 4:
            print (len(y))

        now = datetime.now()
        
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        y[-1] = formatted_date
        x = tuple(y)
        if len(x) < 4:
            print (len(x))
        if len(x) == 4:
    #       if sensor debugging then use this...
            query = f"INSERT INTO sensors VALUES %s;" % (tuple(x),)
            try:
                cur.execute(query)
                conn.commit()
            except mariadb.Error as e:
                conn.rollback()

# Clear the log of previous readings for 40 hours
        if len(ys) > 2500: #301220 - was 2500
            xs.clear()
            ys.clear()
            ys_hum.clear()
            ys_pres.clear()
            print ('len > 59')
            logger.info('len > 59')  
# Update the graph every 10 mins
        #if t == 598:
        if t == 20:
            print('writing page')
            logger.info('writing page')  
            writehtml()

            rewrite()
        
        time.sleep(30)

rewrite()


        
