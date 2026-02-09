from typing import List, Tuple
import random

def _validate_bits(bits: List[int]) -> None:
    if not bits:
        raise ValueError("Message must not be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Message must be a list of 0 and 1")

def compute_parity_bit(message: List[int]) -> int:
    _validate_bits(message)
    return sum(message) % 2

def send(message: List[int]) -> List[int]:
    _validate_bits(message)
    print("Encoding Message ", message)
    parity = compute_parity_bit(message)
    encoded = message + [parity]
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

def parity_check(received: List[int]) -> bool:
    return sum(received) % 2 == 0

def receive(received: List[int]) -> Tuple[List[int], bool]:
    print("Receiving Message ", received)
    is_valid = parity_check(received)
    payload = received[:-1]
    if is_valid:
        print("Parity Check Passed")
    else:
        print("Detected Error With Parity Check")
    print("Decoded Message: ", payload)
    return payload, is_valid

if __name__ == "__main__":
    message = [1, 1, 1, 0, 0, 1, 0]
    p_flip = 0.1
    d_min = 2
    s = d_min - 1
    t = (d_min - 1) // 2

    encoded = send(message)
    noisy = noise_channel(encoded, p_flip)
    decoded_payload, is_valid = receive(noisy)

    print("s: ", s)
    print("t: ", t)
