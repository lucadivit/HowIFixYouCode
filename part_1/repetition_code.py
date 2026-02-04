from typing import List
import math, random

def repetition_error_probability(repetitions: int, p_flip: float):
    p_error = 0.0
    for k in range((repetitions + 1) // 2, repetitions + 1):
        p_error += math.comb(repetitions, k) * (p_flip ** k) * ((1 - p_flip) ** (repetitions - k))
    return p_error

def success_proba(repetitions: int, p_flip: float, message_len: int):
    return (1 - repetition_error_probability(repetitions, p_flip)) ** message_len

def send(message: List[int], repetitions: int) -> List[int]:
    encoded = []
    for bit in message:
        if bit not in [0, 1]:
            raise Exception("Message must be a list of 0 and 1")
        else:
            encoded.extend([bit] * repetitions)
    return encoded

def noise_channel(encoded: List[int], p_flip: float = 0.1) -> List[int]:
    noisy = []
    for bit in encoded:
        if random.random() < p_flip:
            noisy.append(1 - bit)
        else:
            noisy.append(bit)
    return noisy

def receive(noisy: List[int], repetitions: int) -> List[int]:
    decoded = []
    for i in range(0, len(noisy), repetitions):
        block = noisy[i:i + repetitions]
        decoded_bit = 1 if sum(block) > repetitions // 2 else 0
        decoded.append(decoded_bit)
    return decoded


if __name__ == "__main__":
    message = [0]
    repetitions = 3
    p_flip = 0.1

    encoded = send(message, repetitions)
    noisy = noise_channel(encoded, p_flip)
    decoded = receive(noisy, repetitions)

    print("Message: ", message)
    print("Encoded: ", encoded)
    print("Noisy:   ", noisy)
    print("Decoded: ", decoded)
    print("Decoded Proba Success:", success_proba(repetitions=repetitions, p_flip=p_flip, message_len=len(message)))