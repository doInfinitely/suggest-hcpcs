
def levenshtein_distance(s, t):
    D = [[0 for i in range(len(t)+1)] for j in range(len(s)+1)]
    for i in range(1,len(s)+1):
        D[i][0] = i
    for j in range(1, len(t)+1):
        D[0][j] = j
    for j in range(1, len(t)+1):
        for i in range(1, len(s)+1):
            try:
                cost = int(not s[i-1] == t[j-1])
            except IndexError:
                cost = 1
            D[i][j] = min([D[i-1][j]+1, D[i][j-1]+1, D[i-1][j-1]+cost])
    return D[len(s)][len(t)]

if __name__ == "__main__":
    print(levenshtein_distance("sitting", "kitten"))          
