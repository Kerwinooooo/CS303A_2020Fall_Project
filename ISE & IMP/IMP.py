import argparse
import math
import time
from copy import deepcopy
import random
import numpy as np
import multiprocessing as mp
import sys
import os


num_node = 0
num_edge = 0
network = {}
seed_size = 0
model = ''
time_limit = 0
time_start = 0
network_reverse = {}
alpha = 0
beta = 0
lamda_star = 0
lamda_pie = 0
log_n_k = 0
Epsoid = 0
Epsoid_pie = 0
l = 0
LB = 0
R = np.zeros(100000000, dtype='int32')
R_index = 0
R_length = 0
rrset_index = []
core = 8
TIMEOUT = False
Ratioic = 0.3
Ratiolt = 0.3
length_limit = 0
counter = 0


def NodeSelection():
    global R, num_node, seed_size, R_length, R_index, rrset_index
    S = []
    reach_num = [0] * (num_node+1)
    index = {i: set() for i in range(1, num_node+1)}
    R_length = R_index
    rrset_index.append(R_length)
    temp = 0
    # count = 0
    for i in range(R_length):
        while not (rrset_index[temp] <= i < rrset_index[temp + 1]):
            temp += 1
        index[R[i]].add(temp)

    for i in range(1, num_node+1):
        reach_num[i] = len(index[i])

    for i in range(seed_size):
        j = find_max_index(reach_num)
        # count += reach_num[j]
        S.append(j)
        for k in index[j]:
            for m in range(rrset_index[k], rrset_index[k+1]):
                if R[m] == j:
                    pass
                else:
                    reach_num[R[m]] -= 1
                    index[R[m]].remove(k)
        index[j] = set()
        reach_num[j] = 0

    return S#, count / len(R)


def init():
    global num_edge, num_node, seed_size, model, time_limit, network_reverse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--file_name', type=str, default='network.txt')
    parser.add_argument('-k', '--seed_size', type=int, default='5')
    parser.add_argument('-m', '--model', type=str, default='LT')
    parser.add_argument('-t', '--time_limit', type=int, default=60)

    args = parser.parse_args()
    seed_size = args.seed_size
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

        # delete
        start = int(line[0])
        end = int(line[1])
        ratio = float(line[2])

        # if start == 0 or end == 0:
        #     print(start, end, ratio)

        if end in network_reverse:
            network_reverse[end].append((start, ratio))
        else:
            network_reverse[end] = [(start, ratio)]


def IC_enter(num_node, network_reverse):
    global R, R_index
    while True:
        # IC()
        seed = random.randint(1, num_node)
        rr_set = [seed]
        activity = [False] * num_node
        activity[seed - 1] = True
        activitySet = [seed]

        while activitySet:
            newactivitySet = []
            for seed1 in activitySet:
                if seed1 in network_reverse:
                    for node1 in network_reverse[seed1]:
                        if not activity[node1[0] - 1] and random.random() < node1[1]:
                            activity[node1[0] - 1] = True
                            newactivitySet.append(node1[0])
                            rr_set.append(node1[0])
            activitySet = []
            for j in newactivitySet:
                activitySet.append(j)
        # R.append(rr_set)
        if R_index + len(rr_set) < 100000000:
            rrset_index.append(R_index)
            for i in rr_set:
                R[R_index] = i
                R_index += 1
        else:
            break
        if time.time() - time_start > Ratioic * time_limit:
            break


def LT_enter(num_node, network_reverse):
    global R, R_index, counter, rrset_index
    while True:
        # LT()
        seed = random.randint(1, num_node)
        rr_set = [seed]
        while True:
            if seed in network_reverse:
                lo = network_reverse[seed]
                seed = lo[random.randint(0, len(lo) - 1)][0]
                if seed in rr_set:
                    break
                else:
                    rr_set.append(seed)
            else:
                break
        # R.append(rr_set)
        # counter += len(rr_set)
        if R_index + len(rr_set) < 100000000:
            rrset_index.append(R_index)
            for i in rr_set:
                R[R_index] = i
                R_index += 1
        else:
            break
        if time.time() - time_start > Ratiolt * time_limit:
            break


def find_max_index(A) -> int:
    index = 1
    for i in range(1, len(A)):
        if A[index] <= A[i]:
            index = i
    return index


if __name__ == '__main__':
    time_start = time.time()
    init()
    # Epsoid = 0.05
    # l = 1
    # l = l * (1 + math.log(2) / math.log(num_node))

    # calculate log(Cnk)
    # log_n_k = 0
    # for i in range(num_node - seed_size + 1, num_node + 1):
    #     log_n_k += math.log(i)
    # for i in range(1, seed_size + 1):
    #     log_n_k -= math.log(i)

    # if num_node < 75:
    #     length_limit = 300000
    # elif num_node < 150:
    #     length_limit = 200000

    # time2 = time.time()
    # print(time2 - time_start)

    # Sampling()
    if model == 'IC':
        IC_enter(num_node, network_reverse)
    else:
        LT_enter(num_node, network_reverse)

    # print(len(R))
    # time3 = time.time()
    # print(time3 - time2)
    # print(R_index)
    # print(len(rrset_index))

    S = NodeSelection()

    for i in S:
        print(i)

    # time4 = time.time()
    # print(time4 - time3)
    # print('ratio:', (time4 - time3) / (time3 - time2))
    # print(time.time() - time_start)

    sys.stdout.flush()
    os._exit(0)
