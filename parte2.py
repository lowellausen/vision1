import cv2   # biblioteca opencv utilizada para funções de imagem
import numpy as np  # biblioteca numpy para funções matemáticas, como a SDV


# função que projeta o ponto 3d arr (coord homo) para o plano 2d de imagem utilizando a matriz mat, já realizando divisão perspectiva
def project(mat, arr):
    res = np.zeros((3, 1))
    for i in range(3):
        for j in range(3):
            res[i] += mat[i][j] * arr[j]
    res = res // res[2]
    return res


def reproject(mat, arr):
    res = np.zeros((3, 1))
    arr2 = [arr[0], arr[1], 1.0]
    for i in range(3):
        for j in range(3):
            res[i] += mat[i][j]*arr2[j]
    res = res / res[2]
    return res


def draw_square_at(pos):
    img[int(pos[1]) - 2:int(pos[1]) + 2, int(pos[0]) - 2:int(pos[0]) + 2] = [0, 0, 255]


# função callback chamada quando é detectado um clique de mouse, desenha o jogador na tela
def mouse_callback(event, x, y, flags, params):
    if event == 1:
        pos = (x, y)

        point_plane3d = reproject(p_inv, pos)

        #print(point_plane)
        #print(project(p_matrix, point_plane))

        line_point = point_plane3d

        print(line_point)

        line_point[0] += 1.0

        #print(head_point)

        line_point2d = project(p_matrix, line_point)

        #print(head_point3d)

        draw_square_at(pos)
        draw_square_at(line_point2d)

        cv2.imshow('image', img)

        print(pos)


# carregamos a imagem, dimensionamos uma janela para exibí-la, setamos a função de callback definida anteriormente
img = cv2.imread('maracana2.jpg')
size = (img.shape[1], img.shape[0])
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', size[0], size[1])
cv2.setMouseCallback('image', mouse_callback)

# pontos medidos manualmente que serão utilizados para a calibração da câmera
# dicionário onde a chave é uma tupla 2d de coordenadas de pixel e seus valores são os correspondentes pontos 3d (coord homo) representando o ponto no mundo
points = {
    (189, 116): (0.0, 0.0, 1.0),  # origem (trave esquerda com lina de fundo)
    (377, 134): (-3.66, 11.0, 1.0),  # marca de penal
    (268, 60): (16.5, 16.5, 1.0),  # grande área
    (508, 177): (-(5.5 + 7.32), 5.5, 1.0),  # pequena área
}

# estrutura que armezanará a matriz P de câmera
p_matrix = np.zeros((3, 3))

# dimensões da matriz de equações lineares
dima1 = len(points) * 2
dima2 = p_matrix.size

# matriz A de equações lineares que será a base para estimar P
a_matrix = np.zeros((dima1, dima2))

# preenchimento da matriz A de acordo com o slide 10 da aula 4
# utlizando os pontos definidos anteriormente e medidos manualmente
i = 0
keys = list(points.keys())
for k in range(dima1 // 2):
    point2d = keys[k]
    point3d = points[point2d]

    i = k * 2

    a_matrix[i][0] = point3d[0]
    a_matrix[i][1] = point3d[1]
    a_matrix[i][2] = 1.0
    a_matrix[i][3] = 0.0
    a_matrix[i][4] = 0.0
    a_matrix[i][5] = 0.0
    a_matrix[i][6] = -1 * point2d[0] * point3d[0]
    a_matrix[i][7] = -1 * point2d[0] * point3d[1]
    a_matrix[i][8] = -1 * point2d[0]

    i = i + 1

    a_matrix[i][0] = 0.0
    a_matrix[i][1] = 0.0
    a_matrix[i][2] = 0.0
    a_matrix[i][3] = point3d[0]
    a_matrix[i][4] = point3d[1]
    a_matrix[i][5] = 1.0
    a_matrix[i][6] = -1 * point2d[1] * point3d[0]
    a_matrix[i][7] = -1 * point2d[1] * point3d[1]
    a_matrix[i][8] = -1 * point2d[1]

# função numpy para o algoritmo de svd
# s é um array com os valores singulares ordenados de forma decrescente
# colunas de u são os autovetores de AA^t
# linhas de vh são os autovetores de A^tA, estando aqui o autovetor de interesse
# a = u diag(s) vh  onde diag(s) é uma matriz diagonal sendo o vetor s sua diagonal
u, s, vh = np.linalg.svd(a_matrix)

# o resultado do nosso sistema é o autovetor correspondente au menot valor singular de a
# como s é ordenado de forma decrescente, o menor valor singular é a última posição de s, correspondente na última linha de vh
# m é o solução para o nosso sisteminha a
m = vh[dima2 - 1, :]

# transformamos o array m da solução para o formato de matriz 3x4 de interesse
# p_matrix agora está devidamente ajustada e é a matriz de transformação de interesse!!
k = 0
for i in range(3):
    for j in range(3):
        p_matrix[i][j] = m[k]
        k += 1

print(p_matrix)

print(project(p_matrix, [0, 0, 1]))

p_inv = np.linalg.inv(p_matrix)
proj = reproject(p_inv, (189, 116))
print(proj)



# exibimos a imagem por último para não receber cliques antes de tudo devidamente calculado
cv2.imshow('image', img)


# ficamos em laço esperando o usuário ou fechar a janela ou clicar na imagem (botão esquerdo) para adicionar um jogador
k = 0
while 1:
    k = cv2.waitKey(0)

    if k == 27:
        cv2.destroyAllWindows()
        break
