import math
import cv2
import random
import numpy as np
import pandas as pd
import os


def ponto_aleatorio_dentro_do_circulo(x, y, raio):
    # Gera um ângulo aleatório em radianos
    angulo = random.uniform(0, 2 * math.pi)
    # Gera uma distância aleatória dentro do raio
    distancia = math.sqrt(random.uniform(0, 1)) * raio
    # Calcula as coordenadas x, y do ponto aleatório
    ponto_x = x + distancia * math.cos(angulo)
    ponto_y = y + distancia * math.sin(angulo)
    return (int(ponto_x), int(ponto_y))

df = pd.read_csv("./mnist_train.csv", delimiter=",")

labels = []
images = []
ones = []
for i in range(len(df)):
    number = df.iloc[i]["label"]
    pixels = df.iloc[i,1:]
    pixels = np.array(pixels, dtype=np.uint8)
    pixels = pixels.reshape(28,28)
    pixels = (255-pixels)
    images.append(pixels)
    labels.append(number)
    if number == "1" or number == 1:
        ones.append(pixels)


equals = os.listdir("./equals")
addition = os.listdir("./addition")
subtraction = os.listdir("./subtraction")

N_GENERATE = 4000
sizes = [(600, 1000), (1100, 1700), (1500, 2200)]

while N_GENERATE > 2000:
    text_label = ""
    size = sizes[random.randrange(0, len(sizes)-1)]
    width = random.randrange(size[0], size[1])
    height = random.randrange(size[0], size[1])
    img_synthetic = np.ones((height, width), dtype=np.uint8)*255

    top_digits = []
    bottom_digits = []
    res_digits = []

    p1 = ponto_aleatorio_dentro_do_circulo(int(width*0.3), int(height*0.2), int(height/65))
    p2 = ponto_aleatorio_dentro_do_circulo(int(width*0.5), int(height*0.2), int(height/65))
    p3 = ponto_aleatorio_dentro_do_circulo(int(width*0.7), int(height*0.2), int(height/65))
    top_digits.append(p1)
    top_digits.append(p2)
    top_digits.append(p3)

    p4 = ponto_aleatorio_dentro_do_circulo(int(width*0.3), int(height*0.45), int(height/65))
    p5 = ponto_aleatorio_dentro_do_circulo(int(width*0.5), int(height*0.45), int(height/65))
    p6 = ponto_aleatorio_dentro_do_circulo(int(width*0.7), int(height*0.45), int(height/65))
    bottom_digits.append(p4)
    bottom_digits.append(p5)
    bottom_digits.append(p6)

    p7 = ponto_aleatorio_dentro_do_circulo(int(width*0.3), int(height*0.77), int(height/65))
    p8 = ponto_aleatorio_dentro_do_circulo(int(width*0.5), int(height*0.77), int(height/65))
    p9 = ponto_aleatorio_dentro_do_circulo(int(width*0.7), int(height*0.77), int(height/65))
    res_digits.append(p7)
    res_digits.append(p8)
    res_digits.append(p9)

    psig = ponto_aleatorio_dentro_do_circulo(int(width*0.13), int(height*0.5), int(height/20))
    pequal = ponto_aleatorio_dentro_do_circulo(int(width*0.1), int(height*0.6), int(height/45))

    digit_w = int(width/5)
    digit_h = int(height/5)




    equal = cv2.imread("./equals/"+equals[random.randrange(0, len(equals)-1)], cv2.IMREAD_GRAYSCALE)
    equal = cv2.resize(equal, (int(width*0.85), int(height*0.06)))
    x1 = int(pequal[0])
    y1 = int(pequal[1])
    x2 = int(pequal[0]+equal.shape[1])
    y2 = int(pequal[1]+equal.shape[0])
    img_synthetic[y1:y2, x1:x2] = equal
    text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(12, ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height) + "\n"


    try:
        signal = cv2.imread("./addition/"+addition[random.randrange(0, len(addition)-1)], cv2.IMREAD_GRAYSCALE)
        signal = cv2.resize(signal, (int(digit_h*0.75) , int(digit_w*0.5)))
        x1 = int(psig[0] - signal.shape[1]/2)
        y1 = int(psig[1] - signal.shape[0]/2)
        x2 = int(psig[0] + signal.shape[1]/2)
        y2 = int(psig[1] + signal.shape[0]/2)
        img_synthetic[y1:y2, x1:x2] = signal & img_synthetic[y1:y2, x1:x2]
        text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(10, ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height) + "\n"

        n = random.randrange(0, len(top_digits))-1
        for p in top_digits[n:]:
            index = random.randrange(0, len(images)-1)
            digit = images[index]
            digit = cv2.resize(digit, (digit_h, digit_w))
            x1 = int(p[0] - digit.shape[1]/2)
            y1 = int(p[1] - digit.shape[0]/2)
            x2 = int(p[0] + digit.shape[1]/2)
            y2 = int(p[1] + digit.shape[0]/2)
            text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(labels[index], ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height)+"\n"
            img_synthetic[y1:y2, x1:x2] = digit & img_synthetic[y1:y2, x1:x2]

            number_shape = digit.shape
            put_c1 = random.randrange(0, 100) < 35
            if put_c1:
                index = random.randrange(0, len(ones)-1)
                c1 = ones[index]
                c1 = cv2.resize(c1, (int(digit_h*0.45), int(digit_w*0.45)))
                c1 = cv2.GaussianBlur(c1, (5,5), 3)
                factor = (random.randrange(20, 60)/100)
                x1 = int(x1-(digit.shape[1]* factor))
                y1 = int(y1-(digit.shape[0]* factor))
                x2 = int(x1+c1.shape[1])
                y2 = int(y1+c1.shape[0])
                img_synthetic[y1:y2, x1:x2] = c1 & img_synthetic[y1:y2, x1:x2]
                text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(13, ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height)+"\n"
                

        n = random.randrange(0, len(bottom_digits))-1
        for p in bottom_digits[n:]:
            index = random.randrange(0, len(images)-1)
            digit = images[index]
            digit = cv2.resize(digit, (digit_h, digit_w))
            x1 = int(p[0] - digit.shape[1]/2)
            y1 = int(p[1] - digit.shape[0]/2)
            x2 = int(p[0] + digit.shape[1]/2)
            y2 = int(p[1] + digit.shape[0]/2)
            text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(labels[index], ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height)+"\n"
            img_synthetic[y1:y2, x1:x2] = digit & img_synthetic[y1:y2, x1:x2]

            number_shape = digit.shape
            put_c1 = random.randrange(0, 100) < 35
            if put_c1:
                index = random.randrange(0, len(ones)-1)
                c1 = ones[index]
                c1 = cv2.resize(c1, (int(digit_h*0.45), int(digit_w*0.45)))
                c1 = cv2.GaussianBlur(c1, (5,5), 3)
                factor = (random.randrange(20, 40)/100)
                x1 = int(x1-(digit.shape[1]* factor))
                y1 = int(y1-(digit.shape[0]* factor))
                x2 = int(x1+c1.shape[1])
                y2 = int(y1+c1.shape[0])
                img_synthetic[y1:y2, x1:x2] = c1 & img_synthetic[y1:y2, x1:x2]
                text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(13, ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height)+"\n"

        n = random.randrange(0, len(res_digits))-1
        for p in res_digits[n:]:
            index = random.randrange(0, len(images)-1)
            digit = images[index]
            digit = cv2.resize(digit, (digit_h, digit_w))
            x1 = int(p[0] - digit.shape[1]/2)
            y1 = int(p[1] - digit.shape[0]/2)
            x2 = int(p[0] + digit.shape[1]/2)
            y2 = int(p[1] + digit.shape[0]/2)
            text_label += "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(labels[index], ((x2+x1)/2)/width, ((y2+y1)/2)/height, (x2-x1)/width, (y2-y1)/height)+"\n"
            #img_synthetic = cv2.rectangle(img_synthetic, (x1, y1), (x2, y2), (1,1,1), 3)
            img_synthetic[y1:y2, x1:x2] = digit & img_synthetic[y1:y2, x1:x2]

        print(N_GENERATE)
        N_GENERATE -= 1
    except:
        continue