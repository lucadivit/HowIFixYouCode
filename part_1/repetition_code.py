from typing import List
import math, random

def _validate_bits(bits: List[int]) -> None:
    if not bits:
        raise ValueError("Message must not be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Message must be a list of 0 and 1")

def _repetition_error_probability(repetitions: int, p_flip: float):
    p_error = 0.0
    for k in range((repetitions + 1) // 2, repetitions + 1):
        p_error += math.comb(repetitions, k) * (p_flip ** k) * ((1 - p_flip) ** (repetitions - k))
    return p_error

def success_proba(repetitions: int, p_flip: float, message_len: int):
    return (1 - _repetition_error_probability(repetitions, p_flip)) ** message_len

def send(message: List[int], repetitions: int) -> List[int]:
    _validate_bits(message)
    print("Encoding Message ", message)
    encoded = message.copy() * repetitions
    print("Sending Message ", encoded)
    return encoded

def noise_channel(encoded: List[int], p_flip: float = 0.1) -> List[int]:
    if not 0 <= p_flip <= 1:
        raise ValueError("p_flip must be between 0 and 1")
    noisy = []
    for i, bit in enumerate(encoded):
        if random.random() < p_flip:
            print(f"Flipped Bit In Position {i}")
            noisy.append(1 - bit)
        else:
            noisy.append(bit)
    print("Output Of The Noisy Channel ", noisy)
    return noisy

def receive(noisy: List[int], repetitions: int) -> List[int]:
    print("Receiving Message ", noisy)
    if repetitions <= 0:
        raise ValueError("repetitions must be > 0")
    if len(noisy) % repetitions != 0:
        raise ValueError("Invalid encoded length for given repetitions")

    payload_len = len(noisy) // repetitions
    copies = []
    for i in range(0, len(noisy), payload_len):
        copies.append(noisy[i:i + payload_len])

    decoded = []
    for bit_idx in range(payload_len):
        ones = sum(copy[bit_idx] for copy in copies)
        decoded_bit = 1 if ones > repetitions // 2 else 0
        corrected_positions = [
            copy_idx * payload_len + bit_idx
            for copy_idx, copy in enumerate(copies)
            if copy[bit_idx] != decoded_bit
        ]
        if corrected_positions:
            print(f"Corrected Bit At Position {corrected_positions[0]}")
        decoded.append(decoded_bit)
    print("Decoded Message: ", decoded)
    return decoded


if __name__ == "__main__":
    message = [0]
    repetitions = 3
    p_flip = 0.1
    d_min = repetitions
    s = d_min - 1
    t = (d_min - 1) // 2

    encoded = send(message, repetitions)
    noisy = noise_channel(encoded, p_flip)
    decoded = receive(noisy, repetitions)

    print("Is Message Equal: ", message == decoded)
    print("s: ", s)
    print("t: ", t)
    print("Decoded Proba Success:", success_proba(repetitions=repetitions, p_flip=p_flip, message_len=len(message)))
