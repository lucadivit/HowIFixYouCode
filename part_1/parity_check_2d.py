from typing import List, Tuple
import math
import random


def _validate_bits(bits: List[int]) -> None:
    if not bits:
        raise ValueError("Message must not be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Message must be a list of 0 and 1")


def _infer_shape(total_bits: int) -> Tuple[int, int]:
    if total_bits <= 0:
        raise ValueError("Bit length must be > 0")

    for cols in range(int(math.sqrt(total_bits)), 0, -1):
        if total_bits % cols == 0:
            rows = total_bits // cols
            return rows, cols

    raise ValueError("Cannot infer matrix shape")


def _infer_encoded_shape(total_bits: int) -> Tuple[int, int]:
    if total_bits <= 0:
        raise ValueError("Bit length must be > 0")

    candidates = []
    for cols in range(int(math.sqrt(total_bits)), 0, -1):
        if total_bits % cols != 0:
            continue

        rows = total_bits // cols
        if rows < 2 or cols < 2:
            continue

        payload_bits = (rows - 1) * (cols - 1)
        if payload_bits <= 0:
            continue
        if payload_bits % 2 != 0:
            continue

        candidates.append((rows, cols))

    if not candidates:
        raise ValueError("Cannot infer encoded matrix shape")

    candidates.sort(key=lambda rc: (abs(rc[0] - rc[1]), -rc[0]))
    return candidates[0]


def _to_matrix(bits: List[int], rows: int, cols: int) -> List[List[int]]:
    if len(bits) != rows * cols:
        raise ValueError("Invalid shape for given bit length")
    return [bits[r * cols:(r + 1) * cols] for r in range(rows)]


def _flatten(matrix: List[List[int]]) -> List[int]:
    return [bit for row in matrix for bit in row]


def _print_matrix(title: str, matrix: List[List[int]]) -> None:
    print(title)
    for row in matrix:
        print(row)


def send(message: List[int]) -> List[int]:
    _validate_bits(message)
    if len(message) % 2 != 0:
        raise ValueError("Message bit length must be even")

    rows, cols = _infer_shape(len(message))
    payload = _to_matrix(message, rows, cols)
    _print_matrix(f"Payload Matrix ({rows}x{cols})", payload)

    encoded_matrix = []
    for row in payload:
        row_parity = sum(row) % 2
        encoded_matrix.append(row + [row_parity])

    col_parity_row = []
    for c in range(cols):
        col_sum = sum(payload[r][c] for r in range(rows))
        col_parity_row.append(col_sum % 2)

    corner = sum(col_parity_row) % 2
    encoded_matrix.append(col_parity_row + [corner])

    _print_matrix(f"Encoded Matrix ({rows + 1}x{cols + 1})", encoded_matrix)
    return _flatten(encoded_matrix)


def noise_channel(encoded: List[int], p_flip: float = 0.1) -> List[int]:
    if not 0 <= p_flip <= 1:
        raise ValueError("p_flip must be between 0 and 1")
    _validate_bits(encoded)

    total_rows, total_cols = _infer_encoded_shape(len(encoded))
    channel_input = _to_matrix(encoded, total_rows, total_cols)
    _print_matrix(f"Noisy Channel Input Matrix ({total_rows}x{total_cols})", channel_input)

    noisy = []
    for i, bit in enumerate(encoded):
        if random.random() < p_flip:
            row = i // total_cols
            col = i % total_cols
            print(f"Flipped Bit At Coordinates ({row}, {col})")
            noisy.append(1 - bit)
        else:
            noisy.append(bit)

    noisy_matrix = _to_matrix(noisy, total_rows, total_cols)
    _print_matrix(f"Noisy Channel Output Matrix ({total_rows}x{total_cols})", noisy_matrix)
    return noisy


def _syndrome(matrix: List[List[int]]) -> Tuple[List[int], List[int]]:
    bad_rows = [r for r in range(len(matrix)) if sum(matrix[r]) % 2 != 0]
    bad_cols = [c for c in range(len(matrix[0])) if sum(matrix[r][c] for r in range(len(matrix))) % 2 != 0]
    return bad_rows, bad_cols


def receive(noisy: List[int]) -> List[int]:
    _validate_bits(noisy)

    total_rows, total_cols = _infer_encoded_shape(len(noisy))
    if total_rows < 2 or total_cols < 2:
        raise ValueError("Encoded matrix must be at least 2x2")

    rows = total_rows - 1
    cols = total_cols - 1
    matrix = _to_matrix(noisy, total_rows, total_cols)
    _print_matrix(f"Received Matrix ({total_rows}x{total_cols})", matrix)

    bad_rows, bad_cols = _syndrome(matrix)
    detected_error = bool(bad_rows or bad_cols)
    corrected = False

    if len(bad_rows) == 1 and len(bad_cols) == 1:
        r = bad_rows[0]
        c = bad_cols[0]
        print(f"Detected Error At Coordinates ({r}, {c})")
        matrix[r][c] = 1 - matrix[r][c]
        corrected = True
        print(f"Corrected Bit At Position ({r}, {c})")
        _print_matrix("Corrected Matrix", matrix)
    elif detected_error:
        print("Detected Error But Cannot Correct")
        if bad_rows and bad_cols:
            candidate_coordinates = [(r, c) for r in bad_rows for c in bad_cols]
            print(f"Candidate Error Coordinates {candidate_coordinates}")

    if not detected_error:
        print("2D Parity Check Passed")
    elif corrected:
        bad_rows_after, bad_cols_after = _syndrome(matrix)
        if not bad_rows_after and not bad_cols_after:
            print("Detected Error With 2D Parity Check")
            print("Error Corrected Successfully")
        else:
            print("Detected Error With 2D Parity Check")
            print("Correction Attempted But Message Still Inconsistent")
    else:
        print("Detected Error With 2D Parity Check")

    payload_matrix = [row[:cols] for row in matrix[:rows]]
    _print_matrix(f"Decoded Message ({rows}x{cols})", payload_matrix)
    decoded = _flatten(payload_matrix)
    return decoded


if __name__ == "__main__":
    message = [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]
    p_flip = 0.01

    payload_rows, payload_cols = _infer_shape(len(message))
    d_min = 4 if payload_rows > 1 and payload_cols > 1 else 2
    s = d_min - 1
    t = (d_min - 1) // 2

    encoded = send(message)
    noisy = noise_channel(encoded, p_flip)
    decoded = receive(noisy)
    print("Is Message Equal: ", message == decoded)
    print("s: ", s)
    print("t: ", t)
