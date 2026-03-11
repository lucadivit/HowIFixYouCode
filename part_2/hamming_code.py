from itertools import product
from typing import List, Tuple
import random


def _validate(bits: List[int]) -> None:
    if not bits:
        raise ValueError("Message must not be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Message must be a list of 0 and 1")


def _print_matrix(title: str, matrix: List[List[int]]) -> None:
    print(title)
    for row in matrix:
        print(row)


def _build_f2m_space(m: int) -> List[Tuple[int, ...]]:
    if m <= 1:
        raise ValueError("m must be > 1")

    return list(product([0, 1], repeat=m))


def _build_h_matrix(m: int) -> Tuple[List[List[int]], List[List[int]]]:
    v_space = _build_f2m_space(m=m)
    zero = tuple(0 for _ in range(m))
    non_zero_vectors = [vector for vector in v_space if vector != zero]

    i_columns = [tuple(1 if row == col else 0 for row in range(m)) for col in range(m)]
    p_columns = [vector for vector in non_zero_vectors if vector not in i_columns]
    all_columns = p_columns + i_columns

    # H = [P | I_m] dim = (m, n)
    H = []
    for idx in range(m):
        row = [col[idx] for col in all_columns]
        H.append(row)

    P = []  # dim = (k, m)
    for row in p_columns:
        P.append(list(row))

    return H, P


def _build_g_matrix(P: List[List[int]], k: int) -> List[List[int]]:
    # G = [I_k | P] dim = (k, n)
    G = []
    for row_idx in range(k):
        identity_row = [1 if row_idx == col_idx else 0 for col_idx in range(k)]
        p_row = P[row_idx]
        G.append(identity_row + p_row)
    return G


def build_matrixes(m: int, k: int) -> Tuple[List[List[int]], List[List[int]]]:
    H, P = _build_h_matrix(m=m)
    G = _build_g_matrix(P=P, k=k)
    return H, G


def _vector_matrix_product(vector: List[int], matrix: List[List[int]]) -> List[int]:
    _validate(bits=vector)
    cols = len(matrix[0])
    result = []
    for col_idx in range(cols):
        value = 0
        for row_idx, bit in enumerate(vector):
            value += bit * matrix[row_idx][col_idx]
        value = value % 2
        result.append(value)
    return result


def _transpose(matrix: List[List[int]]) -> List[List[int]]:
    return [list(col) for col in zip(*matrix)]


def _search_syndrome(H: List[List[int]], syndrome: List[int], m: int, n: int) -> int:
    for col_idx in range(n):
        column = []
        for row_idx in range(m):
            column.append(H[row_idx][col_idx])
        if column == syndrome:
            return col_idx
    return -1


def send(message: List[int], G: List[List[int]]) -> List[int]:
    _validate(bits=message)

    k = len(G)
    if len(message) != k:
        raise ValueError(f"Message length must be {k}")

    print("Encoding Message ", message)
    encoded = _vector_matrix_product(vector=message, matrix=G)
    print("Sending Message ", encoded)
    return encoded


def noise_channel(encoded_message: List[int], p_flip: float = 0.1) -> List[int]:
    _validate(bits=encoded_message)
    if not 0 <= p_flip <= 1:
        raise ValueError("p_flip must be between 0 and 1")

    noisy = []
    for idx, bit in enumerate(encoded_message):
        if random.random() < p_flip:
            print(f"Flipped Bit In Position {idx}")
            noisy.append(1 - bit)
        else:
            noisy.append(bit)

    print("Output Of The Noisy Channel ", noisy)
    return noisy


def receive(message: List[int], H: List[List[int]], k: int, m: int, n: int) -> List[int]:
    _validate(bits=message)
    print("Receiving Message r: ", message)
    H_T = _transpose(H)
    syndrome = _vector_matrix_product(vector=message, matrix=H_T)
    print("Syndrome: ", syndrome)

    corrected = message.copy()
    if all(bit == 0 for bit in syndrome):
        print("Hamming Check Passed")
    else:
        print("Detected Error With Hamming Check")
        error_position = _search_syndrome(H=H, syndrome=syndrome, m=m, n=n)
        print(f"Detected Error At Position {error_position}")
        corrected[error_position] = 1 - corrected[error_position]
        print(f"Corrected Bit At Position {error_position}")
    decoded = corrected[:k]
    print("Decoded Message: ", decoded)
    return decoded


if __name__ == "__main__":
    m = 3
    n = (2 ** m) - 1
    k = (2 ** m) - m - 1
    H, G = build_matrixes(m=m, k=k)
    print(f"--- Building [{n}, {k}] Hamming Code ---")

    print("m:", m)
    print("n:", n)
    print("k:", k)
    _print_matrix("H matrix:", H)
    _print_matrix("G matrix:", G)

    message = [1, 0, 1, 1]
    p_flip = 0.1
    encoded_message = send(message=message, G=G)
    channel_message = noise_channel(encoded_message=encoded_message, p_flip=p_flip)
    decoded = receive(message=channel_message, H=H, k=k, m=m, n=n)

    print("Is Message Equal: ", message == decoded)

    print("----------------------------")
