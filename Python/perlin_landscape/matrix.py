import pygame


def vec_to_matrix(v):
    if len(v) > 2:
        m = [[v.x, 0, 0], [v.y, 0, 0], [v.z, 0, 0]]
    else:
        m = [[v.x, 0, 0], [v.y, 0, 0]]
    return m


def matrix_to_vec(m):
    if len(m) > 2:
        return pygame.Vector3(m[0][0], m[1][0], m[2][0])
    else:
        return pygame.Vector2(m[0][0], m[1][0])


def matrix_mult(m1, m2):
    if m2 is pygame.Vector2 or m2 is pygame.Vector3:
        return matrix_mult_vec(m1, m2)

    a_rows = len(m1)
    a_cols = len(m1[0])
    b_rows = len(m2)
    b_cols = len(m2[0])

    if a_cols != b_rows:
        print("Matrix multiplication error - columns of M1 must match rows of M2")
        return None

    result = []
    for i in range(a_rows):
        result.append([])
        for j in range(b_cols):
            total = 0
            for k in range(a_cols):
                total += m1[i][k] * m2[k][j]
            result[i].append(total)
    return result


def matrix_mult_vec(m, v):
    vm = vec_to_matrix(v)
    result = matrix_mult(m, vm)
    return matrix_to_vec(result)


def print_matrix(m):
    rows = len(m)
    cols = len(m[0])
    print(f'{rows}x{cols}')
    for i in range(rows):
        for j in range(cols):
            print(f'{m[i][j]}', end=' ')
        print("")
    print("")
