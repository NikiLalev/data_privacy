import time
import math
import numpy as np
import tenseal as ts
from client import Client

def measure_time(func, num_runs=100):
    """
    Executes a function `num_runs` times and returns the average 
    execution time in milliseconds.
    """
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    return (sum(times) / num_runs) * 1000

def run_benchmarks(dim=256, num_runs=100):
    print(f"--- Initializing Benchmark (dim={dim}, runs={num_runs}) ---")
    
    # Initialize client to reuse the existing CKKS context
    client = Client()
    
    # Generate plaintext NumPy vectors
    v1 = np.random.rand(dim)
    v2 = np.random.rand(dim)
    
    print("Encrypting vectors for CKKS...")
    c1 = client.ckks_encrypt_embeddings(np.array([v1]))[0]
    c2 = client.ckks_encrypt_embeddings(np.array([v2]))[0]
    
    # Convert to a standard Python list for ciphertext-plaintext multiplication
    v2_list = v2.tolist()
    
    print("Running operations...")
    
    # 1. Ciphertext-Ciphertext Multiplication
    cc_time = measure_time(lambda: c1 * c2, num_runs)
    np_cc_time = measure_time(lambda: v1 * v2, num_runs)
    
    # 2. Ciphertext-Plaintext Multiplication
    cp_time = measure_time(lambda: c1 * v2_list, num_runs)
    np_cp_time = measure_time(lambda: v1 * v2, num_runs)
    
    # 3. Addition (Ciphertext-Ciphertext)
    add_time = measure_time(lambda: c1 + c2, num_runs)
    np_add_time = measure_time(lambda: v1 + v2, num_runs)
    
    # 4. Rotation (Derived mathematically via .sum())
    # .sum() uses a "rotate and sum" algorithm. For a vector of size N, 
    # it performs log2(N) rotations and log2(N) additions.
    num_ops = int(math.log2(dim))
    
    sum_time = measure_time(lambda: c1.sum(), num_runs)
    
    # Calculate single rotation time: (Total Sum Time - Total Additions Time) / Rotations
    rot_time = (sum_time - (num_ops * add_time)) / num_ops
    np_rot_time = measure_time(lambda: np.roll(v1, 1), num_runs)
    
    # --- Results ---
    print("\n--- Benchmark Results ---")
    print(f"{'Operation':<35} | {'CKKS (ms)':<15} | {'NumPy (ms)':<15} | {'Slowdown'}")
    print("-" * 85)
    
    results = [
        ("Ciphertext-Ciphertext Mult", cc_time, np_cc_time),
        ("Ciphertext-Plaintext Mult", cp_time, np_cp_time),
        ("Addition (Ciphertext)", add_time, np_add_time),
        ("Rotation (Derived from sum)", rot_time, np_rot_time)
    ]
    
    for name, ckks_t, np_t in results:
        # Fallback to prevent negative times from minor Python execution variances
        display_ckks = max(0.0001, ckks_t) 
        slowdown = f"{int(display_ckks / np_t)}x" if np_t > 0 else "N/A"
        print(f"{name:<35} | {displaygit_ckks:<15.4f} | {np_t:<15.6f} | {slowdown}")

if __name__ == "__main__":
    run_benchmarks(dim=256, num_runs=100)