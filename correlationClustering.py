import numpy as np
import random
import sys


def print_clusters(clustering, movies):
    for cluster in clustering:
        for i in range(0, len(cluster)):
            line_i = movies[cluster[i] - 1].split('::')
            print('{} {}'.format(cluster[i], line_i[1]), end='', flush=True)
            if i < len(cluster) - 1:
                print(', ', end='', flush=True)
        print('\n')


def pivot(v, edges, clust):
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
    pivot(vtag, edges, clust)


def calc_cost(clustering, ar):
    cost = 0
    for k in range(0, len(clustering)):
        if len(clustering[k]) == 1:
            cost = cost + np.log((1 / ar[clustering[k][0]][0]))
        else:
            ata = []
            for i in clustering[k]:
                ata.append(i)
                for j in clustering[k]:
                    if j not in ata:
                        cost += (1 / (len(clustering[k]) - 1)) * np.log(1 / ar[i][j])
    return cost


def validate_movie_file(mv_file):
    lines = mv_file.readlines()
    lines = [x.strip() for x in lines]

    for line in lines:
        if not line.isdigit():
            return -1
    return 1


def correlation():
    ####################################################
    #       LOAD DATA FROM THE PATH GIVEN              #
    ####################################################
    ar = np.load('probpy.npy')
    num_rate = np.load('num_rate_movie.npy')
    ####################################################
    #       LOAD MOVIES SET FROM PATH GIVEN            #
    ####################################################
    # load movie set
    file = open(sys.argv[2], 'r')
    movie_set = []
 #   lines = file.readlines()
 #   file.seek(0)
    if validate_movie_file(file) < 0:
        print('Bad input in movie subset file\n')
        return
    file.seek(0)
    for line in file:
        if num_rate[int(line[:-1])] >= 10:
            movie_set.append(int(line[:-1]))
        else:
            print('Movie {} ignored because it has only {} ratings\n'.format(int(line), num_rate[int(line)][0]))
    file.close()
    file = open('movies_updated.dat', 'r', encoding='latin-1')
    movies = file.readlines()
    file.close()
    max_val = np.amax(movie_set)
    edges = np.empty((max_val + 1, max_val + 1), dtype=np.int64)
    # calculate correlation
    for x in movie_set:
        for j in movie_set:
            if x != j:
                if ar[x][j] >= ar[x][0] * ar[j][0]:
                    edges[x][j] = 1
                else:
                    edges[x][j] = -1
    clustering = []
    pivot(movie_set, edges, clustering)
    print_clusters(clustering, movies)
    cost = calc_cost(clustering, ar)
    print(cost)


def main():
    correlation()


if __name__ == "__main__":
    main()
