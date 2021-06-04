import pyodbc 
import threading

class db_array:
    def __init__(self, old_numbers, array_step, array_reverse, array_stop, array_coords, target_coords):
        self.old_numbers = old_numbers
        self.array_step = array_step
        self.array_reverse = array_reverse
        self.array_stop = array_stop
        self.array_coords = array_coords
        self.target_coords = target_coords

class DBManager:
    loop_resolver = [1,0,1]
    def __init__(self):
        self.ball_x = 0.0
        self.ball_y = 0.0
        self._conn = pyodbc.connect('Driver={FreeTDS};'
                      'Server=94.210.35.97,1433;'
                      'Database=BalanceDB;'
                      'UID=BalanceDB_ReadOnly;'
                      'PWD=Password')
    
        self._cursor = self._conn.cursor()
        self.array_data = db_array('', 0, 0, 0, [], [])
        self.__stop_flag = False
        self.__getData()
        self.getNextStep()

#########TARGET COORDS##########
# X: array_data.target_coords[0]
# Y: array_data.target_coords[1]
################################

    def __convert1dArrayTo2dArray(self, l):
        return[l[i:i+2] for i in range(0, len(l), 2)]

    def __convertStringTo2dArray(self, s):
        return self.__convert1dArrayTo2dArray(list(map(float, s.split(','))))

    def __getData(self):
        if not self.__stop_flag:
            threading.Timer(2, self.__getData).start()
    
        self._cursor.execute('SELECT Array_Data FROM BalanceDB.dbo.ArrayTable WHERE ID=1')

        for row in self._cursor:
            new_numbers = str(row)[2:-4]
            if (self.array_data.old_numbers != new_numbers):
                self.array_data.old_numbers = str(row)[2:-4]
                self.array_data.array_coords = self.__convertStringTo2dArray(self.array_data.old_numbers)
                self.array_data.array_step = 0
                self.array_data.array_reverse = 0
                self.array_data.array_stop = 0

    def set_ball_pos(self, x,y):
        self.ball_x = x 
        self.ball_y = y

    def getNextStep(self):
        #if not self.__stop_flag:
        #    threading.Timer(0.25, self.__getNextStep).start()
        
        dx = abs(self.ball_x-self.array_data.array_coords[self.array_data.array_step][0])
        dy = abs(self.ball_y-self.array_data.array_coords[self.array_data.array_step][1])

        radius = 0.2
        array_length = len(self.array_data.array_coords) - 1

        
        self.array_data.target_coords = [self.array_data.array_coords[self.array_data.array_step][0], self.array_data.array_coords[self.array_data.array_step][1]]

        if (array_length > 1):
            #if (dx*dx + dy*dy <= radius*radius):
            if (dx < radius and dy < radius):
                if (self.array_data.array_stop == 0):
                    if (self.array_data.array_reverse == 1):
                        self.array_data.array_step -= 1
                        if (self.array_data.array_step == 0):
                            self.array_data.array_reverse = 0
                    else: 
                        self.array_data.array_step += 1
                        print(self.array_data.array_step)

            if (self.array_data.array_step >= array_length - 1):
                if (self.array_data.array_coords[array_length][0] == 0): 
                    self.array_data.array_stop = 1
                elif (self.array_data.array_coords[array_length][0] == 1): 
                    self.array_data.array_step = 0
                elif (self.array_data.array_coords[array_length][0] == 2): 
                    self.array_data.array_reverse = 1

    def stop(self):
        self.__stop_flag = True
