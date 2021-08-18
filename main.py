import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def print_hi(name):
    print(f'Hi, {name}')


def read_data():
    # read the excel file
    data = pd.read_excel('data.xlsx')
    df = data.sort_values(by=['Lat', 'Long', 'Direction'])  # sort the values of data
    return df


def dropDuplicated(df):
    # convert to 2D numpy array
    arr = list()
    pos = []  # use for next function
    for row in df.itertuples():
        l = list()
        for i in range(1, 5):
            l.append(row[i])
        arr.append(l)
        pos.append(-1)  # use for next function
    arr = np.array(arr)

    # find the duplicated position and direction
    x = 0
    while x < len(pos) - 1:
        loc = []  # calculate mean value of the same location and direction
        if pos[x] == -1:
            pos[x] = x
            loc.append(x)
            for y in range(x + 1, len(pos)):
                if (arr[x][0] == arr[y][0]) & (arr[x][1] == arr[y][1]) & (arr[x][2] == arr[y][2]):
                    pos[y] = -2
                    loc.append(y)
            if len(loc) > 1:
                # find the mean value
                mean = 0.0
                for z in range(len(loc)):
                    mean += arr[loc[z]][3]
                #  update the mean value to the first row in 'loc'
                arr[loc[0]][3] = mean / len(loc)
        else:
            while (pos[x] != -1) & (x < len(pos) - 1):
                x = x + 1

    # remove the duplicated position and direction
    pos = pos[::-1]  # reverse the list
    for i in range(len(pos)):
        if pos[i] == -2:
            j = len(pos) - 1 - i  # the right position in the previous list
            arr = np.delete(arr, j, 0)  # axis = 0 that means we want to delete the row
    return arr


# calculate Power (power1, angle1, power2, angle2, min power)
def calPowerAngle(p1, a1, p2, a2, minp):
    if a1 > a2: # make sure p1 have a min direction
        a1, a2 = a2, a1
        p1, p2 = p2, p1
    power = p1
    angle = a1
    if p1 >= p2:
        if (a2 - a1) * (a2 - a1) > 180 * 180:
            angle = ((a1 + 360) * pow(10, (p1 - p2) / 10) + a2) / (1 + pow(10, (p1 - p2) / 10))
            if angle >= 360:
                angle -= 360
            power = p1 + (p2 - minp) * (a1 + 360 - angle) / (a1 + 360 - a2)
        else:
            angle = (a1 * pow(10, (p1 - p2) / 10) + a2) / (1 + pow(10, (p1 - p2) / 10))
            power = p1 + (p2 - minp) * (a1 - angle) / (a1 - a2)
    elif p2 > p1:
        if (a2 - a1) * (a2 - a1) > 180 * 180:
            angle = ((a2 + 360) * pow(10, (p2 - p1) / 10) + a1) / (1 + pow(10, (p2 - p1) / 10))
            if angle >= 360:
                angle -= 360
            power = p2 + (p1 - minp) * (a2 + 360 - angle) / (a2 + 360 - a1)
        else:
            angle = (a2 * pow(10, (p2 - p1) / 10) + a1) / (1 + pow(10, (p2 - p1) / 10))
            power = p2 + (p1 - minp) * (a2 - angle) / (a2 - a1)
    return power, angle


def mainProcess(arr):
    #  calculate accurate direction of the position with interference
    minp = 0.0  # find the min power in the table
    pos = []  # reset the list pos
    for i in range(arr.shape[0]):
        pos.append(-1)
        if minp > arr[i][3]:
            minp = arr[i][3]
    x = 0  # initial x
    while x < len(pos) - 1:
        loc = []  # calculate mean value if only same the location
        if pos[x] == -1:
            pos[x] = x
            loc.append(x)
            for y in range(x + 1, len(pos)):
                if (arr[x][0] == arr[y][0]) & (arr[x][1] == arr[y][1]):
                    pos[y] = -2  # we will exchange if the value is less than others
                    loc.append(y)
            # we do nothing if len(loc) = 1
            if len(loc) == 2:
                # find the max value
                p1 = arr[loc[0]][3]
                a1 = arr[loc[0]][2]
                p2 = arr[loc[1]][3]
                a2 = arr[loc[1]][2]
                power, angle = calPowerAngle(p1, a1, p2, a2, minp)
                if arr[loc[0]][3] >= arr[loc[1]][3]:
                    arr[loc[0]][3] = power
                    arr[loc[0]][2] = angle
                else:
                    arr[loc[1]][3] = power
                    arr[loc[1]][2] = angle
                    pos[loc[1]] = x + 1
                    pos[loc[0]] = -2

            if len(loc) == 3:
                p0 = arr[loc[0]][3]
                a0 = arr[loc[0]][2]
                p1 = arr[loc[1]][3]
                a1 = arr[loc[1]][2]
                p2 = arr[loc[2]][3]
                a2 = arr[loc[2]][2]
                #  Case 1: P0 >= P1 > P2
                if (p0 >= p1) & (p1 > p2):
                    p, a = calPowerAngle(p0, a0, p1, a1, minp)
                    arr[loc[0]][3] = p
                    arr[loc[0]][2] = a
                # Case 2: P0 >= P2 > P1
                if (p0 >= p2) & (p2 > p1):
                    p, a = calPowerAngle(p0, a0, p2, a2, minp)
                    arr[loc[0]][3] = p
                    arr[loc[0]][2] = a
                # Case 3: P1 >= P2 > P0
                if (p1 >= p2) & (p2 > p0):
                    p, a = calPowerAngle(p1, a1, p2, a2, minp)
                    arr[loc[1]][3] = p
                    arr[loc[1]][2] = a
                    pos[loc[1]] = x + 1
                    pos[loc[0]] = -2
                # Case 4: P1 >= P0 > P2
                if (p1 > p0) & (p0 > p2):
                    p, a = calPowerAngle(p0, a0, p1, a1, minp)
                    arr[loc[1]][3] = p
                    arr[loc[1]][2] = a
                    pos[loc[1]] = x + 1
                    pos[loc[0]] = -2
                # Case 5: P2 >= P1 > P0
                if (p2 > p1) & (p1 > p0):
                    p, a = calPowerAngle(p1, a1, p2, a2, minp)
                    arr[loc[2]][3] = p
                    arr[loc[2]][2] = a
                    pos[loc[2]] = x + 2
                    pos[loc[0]] = -2
                # Case 6: P2 >= P0 > P1
                if (p2 > p0) & (p0 > p1):
                    p, a = calPowerAngle(p0, a0, p2, a2, minp)
                    arr[loc[2]][3] = p
                    arr[loc[2]][2] = a
                    pos[loc[2]] = x + 2
                    pos[loc[0]] = -2
            if len(loc) > 3:
                print("There is a problem! Please check the data input!")
        else:
            while (pos[x] != -1) & (x < len(pos) - 1):
                x = x + 1
    # remove the duplicated position and direction
    pos = pos[::-1]  # reverse the list
    for i in range(len(pos)):
        if pos[i] == -2:
            j = len(pos) - 1 - i  # the right position in the previous list
            arr = np.delete(arr, j, 0)  # axis = 0 that means we want to delete the row
    # print(pos)
    return arr


# Convert the degree in mobile system to Radian in Mathematics and return it
def calculateGradient(x):
    m = x*3.14/180
    m = math.tan(m)
    return m


# Calc the point 'b' where line crosses the Y axis
def calculateYAxisIntersect(p, m):
   return  p[1] - (m * p[0])


def getIntersectPoint(p1, a1, p2, a2):
    m1 = calculateGradient(a1)
    m2 = calculateGradient(a2)

    # See if the the lines are parallel
    if (m1 != m2):  # Not parallel
        # See if either line is vertical
        if (m1 is not None and m2 is not None):
            # Neither line vertical
            c1 = calculateYAxisIntersect(p1, m1)
            c2 = calculateYAxisIntersect(p2, m2)
            x = (c2 - c1) / (m1 - m2)
            y = (m1 * x) + c1
        else:
            # Line 1 is vertical so use line 2's values
            if (m1 is None):
                b2 = calculateYAxisIntersect(p2, m2)
                x = p1[0]
                y = (m2 * x) + b2
            # Line 2 is vertical so use line 1's values
            elif (m2 is None):
                b1 = calculateYAxisIntersect(p1, m1)
                x = p2[0]
                y = (m1 * x) + b1
            else:
                print("Check m1 and m2")
        return x, y
    else: # parallel so we can get the middle point
        x = (p1[0] + p2[0])/2
        y = (p1[1] + p2[1])/2
        return x, y


def finalIntersectPoint(arr):
    # find min value
    min = arr[0][3] # initial value
    for i in range(arr.shape[0]):
        if min > arr[i][3]:
            min = arr[i][3]

    # find dB when compare with min value
    power = []  # compare with min value
    for i in range(arr.shape[0]):
        p = arr[i][3] - min
        power.append(p)

    # find list of intersect points
    sumx = 0.0
    sumy = 0.0
    sumPower = 0.0
    for i in range(arr.shape[0]-1):
         for j in range(i+1, arr.shape[0]):
             p1 = (arr[i][0], arr[i][1])
             a1 = arr[i][2]
             p2 = (arr[j][0], arr[j][1])
             a2 = arr[j][2]
             x, y = getIntersectPoint(p1, a1, p2, a2)
             p = (power[i] + power[j])/2 # find the mean power of intersect point
             sumx += x*p
             sumy += y*p
             sumPower += p
    if sumPower == 0: # make sure sumPower always not equal to zero
        sumPower = 1
    x = sumx/sumPower
    y = sumy/sumPower
    return x,y


def outResult(x, y):
    f = open("result.txt", "w")
    result = str(x) + " " + str(y)
    f.write(result)
    f.close()


def drawing(arr, yp, xp): # we already exchanged x, y here because position is opposite on the map
    print("\nDRAWING!")

    # find min and max of Latitude
    minLat = arr[0][0] # initial number
    maxLat = arr[0][0] # initial number
    for i in range(arr.shape[0]):
        if minLat > arr[i][0]:
            minLat = arr[i][0]
        if maxLat < arr[i][0]:
            maxLat = arr[i][0]

    # find min and max of Longitude
    minLong = arr[0][1] # initial number
    maxLong = arr[0][1] # initial number
    for i in range(arr.shape[0]):
        if minLong > arr[i][1]:
            minLong = arr[i][1]
        if maxLong < arr[i][1]:
            maxLong = arr[i][1]

    # draw line
    m = []
    b = []
    for i in range(arr.shape[0]):
        m.append(calculateGradient(arr[i][2]))
        p = (arr[i][0], arr[i][1])
        b.append(calculateYAxisIntersect(p,m[i]))
    print("m: ", m)
    print("b: ", b)
    x = np.linspace(minLat, maxLat, 500)
    for i in range(len(m)):
        plt.plot(x * m[i] + b[i], x)

    # scatter on the graph
    for i in range(arr.shape[0]):
        plt.scatter(arr[i][1], arr[i][0])
    plt.scatter(xp,yp)

    plt.xlim(minLong*0.9999,maxLong*1.0001)  # longitude 106
    plt.ylim(minLat*0.9999,maxLat*1.0001) # latitude 10
    plt.title('Intersect Point', fontsize=10)
    plt.grid(linestyle='dotted')
    plt.show()

if __name__ == '__main__':
    print_hi('Project 2')
    df = read_data()
    arr = dropDuplicated(df)
    print(arr)
    print()
    arr = mainProcess(arr)
    print(arr)
    print()
    x, y = finalIntersectPoint(arr)
    print("Final Intersect Point: ", x, y)
    outResult(x, y)  # output result to a file
    drawing(arr, x, y)

