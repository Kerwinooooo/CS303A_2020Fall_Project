import multiprocessing as mp
import time
import sys
import argparse
import os
import numpy as np
import random
from multiprocessing import Process


num_node = 0
num_edge = 0
seed = []
model = ''
time_limit = 0
network = {}
time_start = 0


def init():
    global num_node, num_edge, seed, time_limit, model, network
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='in1.txt')
    parser.add_argument('-s', '--seed', type=str, default='seed1.txt')
    parser.add_argument('-m', '--model', type=str, default='IC')
    parser.add_argument('-t', '--time_limit', type=int, default=60)

    args = parser.parse_args()
    model = args.model
    time_limit = args.time_limit

    f = open(args.file_name)
    lines = f.readlines()

    line = lines[0].split(' ')
    num_node = int(line[0])
    num_edge = int(line[1])

    # print('Nodes: ', num_node, '\nEdges: ', num_edge)

    for j in range(1, len(lines)):
        line = lines[j].split(' ')

        start = int(line[0])
        end = int(line[1])
        ratio = float(line[2])

        if start in network:
            network[start].append((end, ratio))
        else:
            network[start] = [(end, ratio)]

    f = open(args.seed)
    lines = f.readlines()
    for j in lines:
        seed.append(int(j))


def IC(seed, network, num_node):
    count = len(seed)
    activitySet = []
    activity = [False] * num_node

    for j in seed:
        activity[j-1] = True
        activitySet.append(j)

    while activitySet:
        newactivitySet = []
        for seed1 in activitySet:
            if seed1 in network:
                neigh = network[seed1]
                for node1 in neigh:
                    if not activity[node1[0]-1] and random.random() < node1[1]:
                        activity[node1[0]-1] = True
                        newactivitySet.append(node1[0])
        count += len(newactivitySet)
        activitySet = []
        for j in newactivitySet:
            activitySet.append(j)
    return count


def LT(seed, network, num_node):

    activitySet = []
    activity = [False] * num_node

    for j in seed:
        activity[j-1] = True
        activitySet.append(j)
    
    # threshold = [1] * num_node
    wtotal = [0] * num_node
    threshold = np.random.uniform(size=num_node)

    for j in range(num_node):
        # threshold[j] = random.random()
        if threshold[j] == 0 and not activity[j-1]:
            activity[j-1] = True
            activitySet.append(j)

    for node1 in activitySet:
        if node1 in network:
            neigh = network[node1]
            for node2 in neigh:
                wtotal[node2[0]-1] += node2[1]

    count = len(activitySet)
    
    while activitySet:
        newactivitySet = []
        for seed1 in activitySet:
            if seed1 in network:
                neigh = network[seed1]
                for node1 in neigh:
                    if not activity[node1[0]-1] and wtotal[node1[0]-1] >= threshold[node1[0]-1]:
                        activity[node1[0]-1] = True
                        newactivitySet.append(node1[0])
                        if node1[0] in network:
                            neig = network[node1[0]]
                            for node2 in neig:
                                wtotal[node2[0]-1] += node2[1]
                                
        count += len(newactivitySet)
        activitySet = []
        for j in newactivitySet:
            activitySet.append(j)
    return count


def ISE(model, tim, seed, network, num_node):

    TIMEOUT = False
    sum_node = 0
    counter = 0
    N = 10000000

    if model == 'IC':
        for j in range(N):
            if time.time() > tim:
                TIMEOUT = True
                break
            sum_node = sum_node + IC(seed, network, num_node)
            counter += 1
    else:
        for j in range(N):
            if time.time() > tim:
                TIMEOUT = True
                break
            sum_node = sum_node + LT(seed, network, num_node)
            counter += 1

    if TIMEOUT:
        return sum_node, counter
    else:
        return sum_node, N


if __name__ == '__main__':
    # TODO: 并行读取文件

    time_start = time.time()

    init()
    # print('file open: ', time.time() - time_start)

    core = 8
    pool = mp.Pool(core)
    result = []
    p = []
    for i in range(core):
        p.append(pool.apply_async(ISE, args=(model, time_start + time_limit - 3, seed, network, num_node)))
    pool.close()
    pool.join()
    sys.stdout.flush()
    for pp in p:
        result.append(pp.get())
    # print(result)

    summ = 0
    counterr = 0
    for i in range(core):
        summ += result[i][0]
        counterr += result[i][1]
    print(summ / counterr)
    # print(counterr)
    # print('parallel: ', time.time() - time_start)


    # a = ISE(model, time_start + time_limit - 3, seed, network, num_node)
    # print(time.time() - time_start)

    # print(time.time() - time_start)
