import numpy as np
import random
import sys
import copy


def print_clusters(clustering, movies):
    for cluster in clustering:
        if len(cluster) > 0:
            for i in range(0, len(cluster)):
                line_i = movies[cluster[i]-1].split('::')
                print('{} {}'.format(cluster[i], line_i[1]), end='', flush=True)
                if i < len(cluster)-1:
                    print(', ', end='', flush=True)
            print('\n')


def pivot(v, edges, clust, ar):
    if len(v) == 0:
        return
    i = int(random.choice(v))
    c = [i]
    vtag = np.empty((0, 0), dtype=np.int64)
    for j in v:
        if j != i:
            if edges[i][j] == 1:
                c = np.append(c, [j])
            else:
                vtag = np.append(vtag, [j])
    clust.append(c)
    pivot(vtag, edges, clust, ar)


def calc_cost(clustering, ar):
    cost = 0
    for k in range(0, len(clustering)):
        if clustering[k] is None:
            continue
        elif len(clustering[k]) == 1:
            cost += np.log((1 / ar[clustering[k][0]][0]))
        elif len(clustering[k]) == 0:
            continue
        else:
            ata = []
            for i in clustering[k]:
                ata.append(i)
                for j in clustering[k]:
                    if j not in ata:
                        cost += (1 / (len(clustering[k]) - 1)) * np.log(1 / ar[i][j])
    return cost


def merge_clusters(clustering, ar):
    maxe = 0
    max_i =0
    max_j =0
    for i in range(0,len(clustering)):
        for j in range(i+1,len(clustering)):
            cost1 = calc_cost([clustering[i], clustering[j]],ar)
            thethe = np.append(clustering[i], clustering[j])
            cost2 = calc_cost([thethe],ar)
            if cost2 < cost1:
                if maxe < cost1-cost2:
                    maxe = cost1-cost2
                    max_i = i
                    max_j = j
    if max_i != 0 and max_j != 0:
        clustering[max_i] = np.append(clustering[max_i], clustering[max_j])
        del clustering[max_j]


def pivot_again(clustering, edges, ar, the_new):
    fixing = []
    for x in range(0, len(clustering)):
        pivot(clustering[x], edges, fixing, ar)
        fixing_cost = calc_cost(fixing, ar)
        past_cost = calc_cost([clustering[x]], ar)
        if fixing_cost < past_cost:
            for z in range(0, len(fixing)):
                the_new.append(fixing[z].copy())
        else:
            the_new.append(clustering[x].copy())
        fixing = []


def double_fix(clustering, ar):
    clust_copy = copy.deepcopy(clustering)
    max_change = -1
    max_i = -1
    max_j = -1
    m_to_move1 = -1
    m_to_move2 = -1
    for i in range(0, len(clust_copy)):
        if len(clust_copy[i]) >= 2:
            for m1 in range(0,len(clust_copy[i])):
                for m2 in range(m1+1,len(clust_copy[i])):
                    for j in range(i+1,len(clust_copy)):
                        new_i = copy.deepcopy(clust_copy[i])
                        new_j = copy.deepcopy(clust_copy[j])
                        new_j = np.append(copy.deepcopy([clust_copy[i][m1], clust_copy[i][m2]]), new_j)
                        if not isinstance(new_i, list):
                            new_i = new_i.tolist()
                        new_i.remove(clust_copy[i][m1])
                        new_i.remove(clust_copy[i][m2])
                        cost1 = calc_cost([new_i, new_j], ar)
                        cost2 = calc_cost([clust_copy[i], clust_copy[j]], ar)
                        if cost1 < cost2 and cost2 - cost1 > max_change:
                            max_change = cost2 - cost1
                            m_to_move1 = copy.deepcopy(clust_copy[i][m1])
                            m_to_move2 = copy.deepcopy(clust_copy[i][m2])
                            max_i = i
                            max_j = j
    if m_to_move1 > 0 and m_to_move2 > 0:
        if not isinstance(clustering[max_i], list):
            clustering[max_i] = clustering[max_i].tolist()
        clustering[max_j] = np.append(clustering[max_j], [m_to_move1, m_to_move2])
        if len(clustering[max_i]) == 1:
            clustering.pop(max_i)
        else:
            clustering[max_i].remove(m_to_move1)
            clustering[max_i].remove(m_to_move2)


def last_fix(clustering, ar):
    clust_copy = copy.deepcopy(clustering)
    max_change = -1
    max_i = -1
    max_j = -1
    m_to_move = -1
    for i in range(0,len(clust_copy)):
        for m in clust_copy[i]:
            clust_copy = [x for x in clust_copy if x != []]
            for j in range(i+1,len(clust_copy)):
                new_i = copy.deepcopy(clust_copy[i])
                new_j = copy.deepcopy(clust_copy[j])
                new_j = np.append(copy.deepcopy(m), new_j)
                if not isinstance(new_i,list):
                    new_i = new_i.tolist()
                new_i.remove(m)
                cost1 = calc_cost([new_i,new_j], ar)
                cost2 = calc_cost([clust_copy[i], clust_copy[j]], ar)
                if cost1 < cost2 and cost2-cost1 > max_change:
                    max_change = cost2 - cost1
                    m_to_move = copy.deepcopy(m)
                    max_i = i
                    max_j = j
    if m_to_move > 0:
        if not isinstance(clustering[max_i], list):
            clustering[max_i] = clustering[max_i].tolist()
        clustering[max_j] = np.append(clustering[max_j], m_to_move)
        if len(clustering[max_i]) == 1:
            clustering.pop(max_i)
        else:
            clustering[max_i].remove(m_to_move)
    else:
        return -1


def partition_cluster(clustering, ar):
    clust_copy = copy.deepcopy(clustering)
    max_change = -1
    max_i = -1
    m_to_move = -1
    for i in range(0,len(clust_copy)):
        if len(clust_copy[i]) > 1:
            for m in clust_copy[i]:
                new_i = copy.deepcopy(clust_copy[i])
                new_j = [copy.deepcopy(m)]
                if not isinstance(new_i, list):
                    new_i = new_i.tolist()
                new_i.remove(m)
                cost1 = calc_cost([new_i,new_j], ar)
                cost2 = calc_cost([clust_copy[i]], ar)
                if cost1 < cost2 and cost2-cost1 > max_change:
                    max_change = cost2 - cost1
                    m_to_move = copy.deepcopy(m)
                    max_i = i
    if m_to_move > 0:
        if not isinstance(clustering[max_i], list):
            clustering[max_i] = clustering[max_i].tolist()
        clustering.append([copy.deepcopy(m_to_move)])
        clustering[max_i].remove(m_to_move)
    else:
        return -1


def validate_movie_file(mv_file):
    lines = mv_file.readlines()
    lines = [x.strip() for x in lines]

    for line in lines:
        if not line.isdigit():
            return -1
    return 1


def correlation():
    ####################################################
    #       LOAD DATA                #
    ####################################################
    ar = np.load('probpy.npy')
    num_rate = np.load('num_rate_movie.npy')
    ####################################################
    #       LOAD MOVIES SET FROM PATH GIVEN            #
    ####################################################
    # load movie set
    file = open(sys.argv[2], 'r')
    movie_set = []
    if validate_movie_file(file) < 0:
        print('Bad input in movie subset file\n')
        return
    file.seek(0)
    for line in file:
        if num_rate[int(line)] >= 10:
            movie_set.append(int(line))
        else:
            print('Movie {} ignored because it has only {} ratings\n'.format(int(line), num_rate[int(line)][0]))
    file.close()
    file = open('movies_updated.dat', 'r', encoding='latin-1')
    movies = file.readlines()
    file.close()
    max_val = np.amax(movie_set)
    edges = np.empty((max_val + 1, max_val + 1), dtype=np.int64)
  #  for x in movie_set:
  #      edges[x][0] = 0
    # calculate correlation
    for x in movie_set:
        for j in movie_set:
            if x != j:
                if ar[x][j] >= ar[x][0] * ar[j][0]:
                    edges[x][j] = 1
                else:
                    edges[x][j] = -1

    #try to fix the graph a bit
    for x in movie_set:
        for j in movie_set:
            if x != j:
                if edges[x][j] == 1:
                    for z in movie_set:
                        if x != z and j != z and (edges[j][z] == 1) and (edges[x][z] != 1):
                            if ar[z][j] > ar[x][j]:
                                edges[x][j] = -1


    min_cost = 999999
    min_clustering = []

    for x in range(1, 20):
        clustering = []
        pivot(movie_set, edges, clustering,ar)
        cost = calc_cost(clustering, ar)
        if cost < min_cost:
            min_cost = cost
            min_clustering = clustering

    to_finish =0
    while 1:
        tmp = min_clustering.copy()
        min_clustering =[]
        pivot_again(tmp,edges,ar,min_clustering)
        merge_clusters(min_clustering,ar)
        if calc_cost(min_clustering,ar) == calc_cost(tmp,ar):
            to_finish += 1
            if to_finish == 5:
                break
    for j in range(0, 10):
        lf = last_fix(min_clustering, ar)
        min_clustering = [x for x in min_clustering if x != []]
        pc = partition_cluster(min_clustering, ar)
        if lf == -1 and pc == -1:
            break
        min_clustering.reverse()
    tmp = []
    pivot_again(min_clustering,edges,ar,tmp)
    merge_clusters(tmp,ar)
    print_clusters(min_clustering, movies)
    print(calc_cost(min_clustering, ar))
    return min_clustering


def main():
    correlation()


if __name__ == "__main__":
    main()
