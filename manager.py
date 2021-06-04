import threading
import pyodbc
import serial

class Manager:
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=94.210.35.97,1433;'
                      'Database=BalanceDB;'
                      'UID=BalanceDB_ReadOnly;'
                      'PWD=Password')
    cursor = conn.cursor()
    LASTNUMBER = ''
    def __convert1dArrayTo2dArray(self, l):
        return[l[i:i+2] for i in range(0, len(l), 2)]

    def __convertStringTo2dArray(self, s):
        return self.__convert1dArrayTo2dArray(list(map(int, s.split(','))))

    def __getData(self):
        threading.Timer(2, getData).start()
    
        cursor.execute('SELECT Array_Data FROM BalanceDB.dbo.ArrayTable WHERE ID=1')

        for row in cursor:
            global LASTNUMBER
            global coord_arr
            CURRENTNUMBER = str(row)[2:-4]
            if (LASTNUMBER != CURRENTNUMBER):
                LASTNUMBER = str(row)[2:-4]
                self.list_of_points_mtx.acquire()
                self.list_of_points = self.__convertStringTo2dArray(LASTNUMBER)
                self.list_of_points_mtx.release()

    def __init__(self):
        self.list_of_points_mtx = threading.Lock()
        #self.__getData()
        self.uart = serial.Serial("/dev/ttyUSB0", 115200)

    def send(self, ball, target, delta_time):
        uart.write(struct.pack('fffff', ball.x, ball.y, target[0], target[1], delta_time))