import random
import matplotlib.pyplot as plt

def ler_voos_arquivo(caminho_arquivo):
    voos = []
    with open(caminho_arquivo, 'r') as file:
        for linha in file:
            partes = linha.strip().split(',')
            if len(partes) == 5:
                origem, destino, partida, chegada, preco = partes
                voo = {
                    "origem": origem,
                    "destino": destino,
                    "partida": partida,
                    "chegada": chegada,
                    "preco": int(preco)
                }
                voos.append(voo)
    return voos

def hora_para_minutos(hora):
    horas, minutos = map(int, hora.split(":"))
    return horas * 60 + minutos

def calcular_tempo_espera(individuo):
    tempo_espera_total = 0
    
    for i in range(0, len(individuo), 2):
        voo_ida = individuo[i]
        voo_volta = individuo[i + 1]
        
        chegada_roma = hora_para_minutos(voo_ida['chegada'])
        partida_volta = hora_para_minutos(voo_volta['partida'])
        
        # Tempo de espera em Roma antes do voo de volta
        if partida_volta > chegada_roma:
            tempo_espera_total += partida_volta - chegada_roma
        else:
            # Se o voo de volta parte no dia seguinte
            tempo_espera_total += (24 * 60 - chegada_roma) + partida_volta
    
    return tempo_espera_total

def calcular_fitness(individuo):
    custo_total = sum(voo['preco'] for voo in individuo)
    tempo_espera_total = calcular_tempo_espera(individuo)
    return custo_total + tempo_espera_total  # Quanto menor, melhor

def torneio(populacao, k):
    selecionados = random.sample(populacao, k)
    return min(selecionados, key=lambda ind: calcular_fitness(ind))

def crossover_um_ponto(pai1, pai2):
    ponto_corte = random.randint(1, len(pai1) - 1)
    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
    return filho1, filho2

def mutacao_troca_voo(individuo, voos_validos):
    indice_mutacao = random.randint(0, len(individuo) - 1)
    cidade = individuo[indice_mutacao]['origem']
    novo_voo = random.choice([voo for voo in voos_validos if voo['origem'] == cidade])
    individuo[indice_mutacao] = novo_voo

def inicializar_populacao(voos_validos, tamanho_populacao):
    populacao = []
    cidades = ["LIS", "MAD", "CDG", "DUB", "BRU", "LHR"]
    for _ in range(tamanho_populacao):
        individuo = []
        for cidade in cidades:
            voos_cidade = [voo for voo in voos_validos if voo['origem'] == cidade]
            individuo.append(random.choice(voos_cidade))
            voos_cidade_retorno = [voo for voo in voos_validos if voo['origem'] == "FCO" and voo['destino'] == cidade]
            individuo.append(random.choice(voos_cidade_retorno))
        populacao.append(individuo)
    return populacao

def algoritmo_genetico(voos_validos, tamanho_populacao, numero_geracoes, tamanho_torneio, prob_crossover, prob_mutacao, taxa_elitismo):
    populacao = inicializar_populacao(voos_validos, tamanho_populacao)
    historico_custos = []
    
    for geracao in range(numero_geracoes):
        nova_populacao = []
        
        numero_elites = int(taxa_elitismo * tamanho_populacao)
        elites = sorted(populacao, key=lambda ind: calcular_fitness(ind))[:numero_elites]
        nova_populacao.extend(elites)
        
        while len(nova_populacao) < tamanho_populacao:
            pai1 = torneio(populacao, tamanho_torneio)
            pai2 = torneio(populacao, tamanho_torneio)
            
            if random.random() < prob_crossover:
                filho1, filho2 = crossover_um_ponto(pai1, pai2)
            else:
                filho1, filho2 = pai1.copy(), pai2.copy()
            
            if random.random() < prob_mutacao:
                mutacao_troca_voo(filho1, voos_validos)
            if random.random() < prob_mutacao:
                mutacao_troca_voo(filho2, voos_validos)
            
            nova_populacao.append(filho1)
            nova_populacao.append(filho2)
        
        populacao = nova_populacao
        
        melhor_individuo = min(populacao, key=lambda ind: calcular_fitness(ind))
        historico_custos.append(calcular_fitness(melhor_individuo))
    
    melhor_individuo = min(populacao, key=lambda ind: calcular_fitness(ind))
    return melhor_individuo, historico_custos

def plotar_grafico(historico_custos):
    plt.figure(figsize=(10, 6))
    plt.plot(historico_custos, marker='o', linestyle='-', color='b')
    plt.title('Evolução do Custo Total ao Longo das Gerações')
    plt.xlabel('Geração')
    plt.ylabel('Custo Total')
    plt.grid(True)
    plt.show()

# Definindo os parâmetros
tamanho_populacao = 80
numero_geracoes = 120
tamanho_torneio = 2
prob_crossover = 0.5
prob_mutacao = 0.05
taxa_elitismo = 0.05

# Executando o algoritmo
caminho_arquivo = 'voos.txt'
voos_validos = ler_voos_arquivo(caminho_arquivo)
melhor_solucao, historico_custos = algoritmo_genetico(voos_validos, tamanho_populacao, numero_geracoes, tamanho_torneio, prob_crossover, prob_mutacao, taxa_elitismo)

# Plotando os resultados
plotar_grafico(historico_custos)

print("Melhor solução encontrada:", melhor_solucao)
print("Custo total:", calcular_fitness(melhor_solucao))
