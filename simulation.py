import sys
import os
import random
import math
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pygame
from pygame.locals import *

# Definindo cores
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (204, 0, 0)
grey = (210, 210, 210)
blue =  (61, 133, 198)
yellow = (255, 255, 0)

#Inicializar pygame
pygame.init()

#Nome
pygame.display.set_caption("Robot Map")

#Estados possíveis de cada célula:
livre = 0
visitado = 1
robo = 2
obstaculo = 3
alcool_temp = 7 #variável temporária para onde o alcool teoricamente estaria

#tamanho maximo da matriz (a partir de 20 pode ser que fique difícil a visualização no prompt de comando)
os.system('clear')
max_size = int(input('Digite a dimensão N do mapa quadrado NxN:\n'))

#Margem entre blocos
margin = 1

#Setando tamanho dos blocos
width = (350 - margin)/max_size - margin
height = (350 - margin)/max_size - margin

#Setar tamanho da tela
screen_width = 350
screen_height = 350
WINDOW_SIZE = [350, 350]

screen = pygame.display.set_mode(WINDOW_SIZE)
 
#Para saber o tempo de atualizar
clock = pygame.time.Clock()
frame = max_size*100

#mapa
matrix = []
alcoolmap = [[0]*max_size for i in range (0, max_size)]

#matriz de movimentação com prioridade dos robôs
moves = [(-1, 0), (0, -1), (0, 1), (1, 0)]

#matriz de caminhos de cada robô sendo inicializada como uma lista q tem 4 listas vazias
#uma lista pra cada movimentação de robô
path = [[] for i in range(0, 4)]

#função para inicializar a matriz
def matrix_init():
	for i in range (0, max_size):
		line = []
		for j in range (0, max_size):
			num = random.random()
			#geração do mapa por aleatoriedade
			if num <= 0.1:
				new_cell = alcool_temp
			elif num > 0.1 and num <= 0.2:
				new_cell = obstaculo
			else:
				new_cell = livre
			line.append(new_cell)
		matrix.append(line)

	

#função para mostrar a matriz na tela
def print_matrix():
	for i in range (0, max_size):
		for j in range (0, max_size):
			if matrix[i][j] == robo:
				CRED = '\033[91m'
				CEND = '\033[0m'
			elif matrix[i][j] == visitado:
				CRED = '\033[34m'
				CEND = '\033[0m'
			elif matrix[i][j] == obstaculo:
				CRED = '\033[92m'
				CEND = '\033[0m'
			elif matrix[i][j] == alcool_temp:
				CRED = '\033[33m'
				CEND = '\033[0m'
			else:
				CRED = '\033[0m'
				CEND = '\033[0m'
			print(CRED + str(matrix[i][j]) + CEND, sep="", end=" ")
		print("\n")

#função para verificar se a matriz ainda tem espaços disponiveis para ser visitado
def verify_matrix():
	for i in range (0, max_size):
		for j in range (0, max_size):
			if matrix[i][j] == livre or matrix[i][j] == alcool_temp:
				return True
	return False


#função para verificar se uma coordenada está dentro dos limites da matriz
#para que seja utilizada posteriormente
def verify_coord(newi, newj):
	return newi >= 0 and newi < max_size and newj >= 0 and newj < max_size 

def cross(coords, i):
		if coords[i][1]+1 < max_size:
			#olhando pra todas as casas a DIREITA da posição de cada robô
			for j in range (coords[i][1]+1, max_size):
				if matrix[coords[i][0]][j] == obstaculo or matrix[coords[i][0]][j] == robo:
					# se ele achar algum obstáculo ou robô na linha, ele não pode chegar de forma segura a célula livre
					# então apenas cancela a análise
					break
				elif matrix[coords[i][0]][j] == livre or matrix[coords[i][0]][j] == alcool_temp:
					# se ele não achou nenhum obstáculo ou robô e tem uma célula livre pra onde ele pode se movimentar
					# então retorna a movimentação para a DIREITA -|
					newj = coords[i][1] + 1              #         |
					if verify_coord(coords[i][0], newj): #         |
						return (0, 1) # <---------------------------
				else: continue
		if coords[i][1]-1 >= 0:
			# exatamente a mesma análise para a ESQUERDA
			for j in range (coords[i][1]-1, -1, -1):
				if matrix[coords[i][0]][j] == obstaculo or matrix[coords[i][0]][j] == robo:
					break
				elif matrix[coords[i][0]][j] == livre or matrix[coords[i][0]][j] == alcool_temp:
					newj = coords[i][1] - 1
					if verify_coord(coords[i][0], newj):
						return (0, -1)
				else: continue
		if coords[i][0]+1 < max_size:
			# exatamente a mesma análise para BAIXO
			for j in range (coords[i][0]+1, max_size):
				if matrix[j][coords[i][1]] == obstaculo or matrix[j][coords[i][1]] == robo:
					break
				elif matrix[j][coords[i][1]] == livre or matrix[j][coords[i][1]] == alcool_temp:
					newi = coords[i][0] + 1
					if verify_coord(newi, coords[i][1]):
						return (1, 0)
				else: continue
		if coords[i][0]-1 >= 0:
			# exatamente a mesma análise para CIMA
			for j in range (coords[i][0]-1, -1, -1):
				if matrix[j][coords[i][1]] == obstaculo or matrix[j][coords[i][1]] == robo:
					break
				elif matrix[j][coords[i][1]] == livre or matrix[j][coords[i][1]] == alcool_temp:
					newi = coords[i][0] - 1
					if verify_coord(newi, coords[i][1]):
						return (-1, 0)
				else: continue
		
		# caso não tenha achado NENHUMA célula livre olhando na cruz, então o robô 
		# não deve se movimentar baseado nessa função
		return (0, 0)


#função que vai atualizar a matriz geral do programa
def change_matrix(coords):
	#um loop para analisar cada robô
	for i in range (0, 4):
		flag = 0 #flag pra saber se conseguiu se movimentar (1) ou não (0) 
		#um loop para analisar os movimentos de cada robô
		for j in range (0, 4):
			#calculando as possíveis novas coordenadas desse robô
			newi = coords[i][0] + moves[j][0]
			newj = coords[i][1] + moves[j][1]
			if verify_coord(newi, newj):
				#se ele encontrar alcool, ele salva no mapa de concentração
				if matrix[newi][newj] == alcool_temp:
						alcoolmap[newi][newj] = alcool_temp
				#se o espaço pra onde ele estiver querendo ir for livre, então ele vai
				#e quebra o loop de movimentação pra esse robô específico
				if matrix[newi][newj] == livre or matrix[newi][newj] == alcool_temp:
					matrix[newi][newj] = (robo)
					matrix[coords[i][0]][coords[i][1]] = (visitado)
					#ativando a flag
					flag = 1
					path[i].append((coords[i][0], coords[i][1]))
					coords[i][0] = newi
					coords[i][1] = newj
					break

		# caso não tenha se movimentado, o robô deve procurar em uma cruz pelo mapa inteiro
		# para posições que estejam livres
		if not flag:
			# pega a movimentação a ser feita pelo robô após a análise em cruz
			(movi, movj) = cross(coords, i)
			
			# se a tupla de movimentos for (0,0) significa que é pra ele não há espaços livres na
			# cruz que foi analisada, então pula para o próximo caso (o de voltar no caminho já feito)
			if (movi, movj) != (0, 0):
				# se entrou aqui, apenas faz a mudança de estado das células e aciona a flag de movimentação
				matrix[coords[i][0]][coords[i][1]] = (visitado)
				path[i].append((coords[i][0], coords[i][1]))
				flag = 1
				coords[i][0] = coords[i][0] + movi
				coords[i][1] = coords[i][1] + movj
				matrix[coords[i][0]][coords[i][1]] = (robo)

		# caso não tenha se movimentado ainda mesmo depois dessas verificações, o robô 
		# deve regredir para a posição que estava anteriormente e realizá-las novamente (as verificações)
		if not flag and path[i]:
			flag = 0
			newcoord = path[i].pop()
			matrix[newcoord[0]][newcoord[1]] = (robo)
			matrix[coords[i][0]][coords[i][1]] = (visitado)
			coords[i][0] = newcoord[0]
			coords[i][1] = newcoord[1]

#aumentando o alcance do alcool(como se estivesse espalhado)
def heatmap():
	for i in range (0, max_size):
		for j in range (0, max_size):
			if alcoolmap[i][j] == alcool_temp:
				alcoolmap[i][j] = 100
				if i - 1 > 0: alcoolmap[i-1][j] = 95
				if i + 1 < max_size: alcoolmap[i+1][j] = 90
				if j - 1 > 0: alcoolmap[i][j-1] = 85
				if j + 1 < max_size: alcoolmap[i][j+1] = 90

#plota o mapa de concentração
def print_heatmap(map):
	plt.imshow(alcoolmap, interpolation='sinc', cmap='rainbow')

	#salvar o mapa de concentração em png
	if map: plt.savefig('heatmap1.png')
	if not map: plt.savefig('heatmap2.png')

	#mostrar o mapa de concentração
	plt.show()

def color_map():
	for i in range (max_size):
		for j in range (max_size):
			#cor do bloco
			if matrix[i][j] == robo:
				color = red
			elif matrix[i][j] == visitado:
				color = blue
			elif matrix[i][j] == obstaculo:
				color = green
			elif matrix[i][j] == alcool_temp:
				color = yellow
			else:
				color = grey
			
			#atualizar a cor do bloco
			pygame.draw.rect(screen,
							color,
							[(margin + width) * j + margin,
							(margin + height) * i + margin,
							width,
							height])
			#Frames por segundo
			clock.tick(frame)
			#Update da tela
			pygame.display.flip()

def main():
	#coordenadas iniciais de cada robô
	coords = [[max_size-1, max_size//2 - 1], [max_size-1, max_size//2], [max_size-1, max_size//2 + 1], [max_size-1, max_size//2 + 2]]
	matrix_init()
	#colocando cada robô no mapa (independente do que foi gerado pela aleatoriedade)
	for i in range (0, 4):
		matrix[coords[i][0]][coords[i][1]] = (robo)

	# variavel pra saber em quantos passos ele vai fazer o mapeamento completo
	passos = 0

	# Set the screen background
	screen.fill(white)

	print_matrix()
	while verify_matrix() == True:
		os.system('clear') #limpar a tela pra não printar mil coisas
		change_matrix(coords) #chamando a função de atualização para cada posição dos robôs
		passos+=1
		#print(coords)
		print_matrix()

		#Para visualizar o mapa com pygame
		color_map()

		time.sleep(0.1) #dar um delay pra melhorar a visualização
	print(passos)
	
	#nao espalhado
	print_heatmap(1)

	#para ver a diferenca entre espalhado e nao espalhado
	heatmap()
	print_heatmap(0)

	#Esperar para fechar o mapa
	time.sleep(0.5)
	pygame.quit()

	return 0


main()