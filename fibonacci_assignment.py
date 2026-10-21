import sys
import time

# --- Part 1: Implementation ---
#here we define two different implementations of the Fibonacci function: fib_a and fib_b.
calls_a = 0
calls_b = 0
fibtable = {}
# then he defines the two functions, fib_a and fib_b, which compute the Fibonacci number for a given n. The function fib_a uses a simple recursive approach, while fib_b uses memoization to store previously computed values in a dictionary called fibtable.
def fib_a(n):
    global calls_a
    calls_a += 1
    if n == 0 or n == 1:
        return n
    return fib_a(n-1) + fib_a(n-2)

def fib_b(n):
    global calls_b
    calls_b += 1
    if n in fibtable:
        return fibtable[n]
    if n == 0 or n == 1:
        value = n
    else:
        value = fib_b(n-1) + fib_b(n-2)
    fibtable[n] = value
    return value

def run_a(n):
    global calls_a
    calls_a = 0
    start = time.perf_counter()
    value = fib_a(n)
    secs = time.perf_counter() - start
    return value, calls_a, secs

def run_b(n):
    global calls_b
    fibtable.clear()
    calls_b = 0
    start = time.perf_counter()
    value = fib_b(n)
    secs = time.perf_counter() - start
    return value, calls_b, secs

def true_fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# --- Part 4.2: Two Fixes ---
#then herre we define two fixes for the recursion limit issue. The first fix is to raise the recursion limit using sys.setrecursionlimit, and the second fix is to implement an iterative version of the Fibonacci function called fib_iterative.
def fib_b_raised_limit(n, limit=5000):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, limit))
    try:
        return run_b(n)
    finally:
        sys.setrecursionlimit(old)

def fib_iterative(n):
    if n == 0:
        return 0
    prev, cur = 0, 1
    for _ in range(2, n+1):
        prev, cur = cur, prev + cur
    return cur

# --- Part 4.3: Truthy check bug ---
fibtable_truthy = {}
calls_truthy = 0
def fib_b_truthy(n):
    global calls_truthy
    calls_truthy += 1
    if fibtable_truthy.get(n):  # BUG: 0 is treated as missing
        return fibtable_truthy[n]
    if n == 0 or n == 1:
        value = n
    else:
        value = fib_b_truthy(n-1) + fib_b_truthy(n-2)
    fibtable_truthy[n] = value
    return value

def run_truthy(n):
    global calls_truthy
    fibtable_truthy.clear()
    calls_truthy = 0
    value = fib_b_truthy(n)
    return value, calls_truthy

# --- Main ---
def main():
    # Part 1.3: check 0..20
    print("Part 1.3: check n=0..20")
    for n in range(21):
        a = run_a(n)[0]
        b = run_b(n)[0]
        ok = (a == b == true_fib(n))
        print(f" n={n:2d} A={a:5d} B={b:5d} ok={ok}")

    # Part 2.2: experiments
    #herre we run experiments for both algorithms A and B, measuring the number of calls and the time taken for various values of n. The results are printed to the console.
    print("\nPart 2.2 (a) Algorithm A: n=5,10,15,20,25,30,35")
    rows_a = []
    for n in [5, 10, 15, 20, 25, 30, 35]:
        v, c, s = run_a(n)
        rows_a.append((n, c, s))
        print(f" n={n:2d} calls={c:,} time={s:.6f}s")
        if s > 60:
            break

    print("\nPart 2.2 (b) Algorithm B: n=10,50,100,200,500,1000")
    rows_b = []
    for n in [10, 50, 100, 200, 500, 1000]:
        try:
            v, c, s = run_b(n)
            rows_b.append((n, c, s))
            print(f" n={n:4d} calls={c} time={s:.6f}s")
        except RecursionError:
            print(f" n={n:4d} FAILED at default limit {sys.getrecursionlimit()}")
            v, c, s = fib_b_raised_limit(n)
            rows_b.append((n, c, s))
            print(f"  with raised limit: calls={c} time={s:.6f}s")

    # Part 3.5: estimate for A at n=1000
    # here we estimate the number of calls for Algorithm A at n=1000 using the formula 2*F(1001)-1, where F(n) is the nth Fibonacci number. We also calculate the measured rate of calls per second based on the last entry in rows_a.
    n_big, calls_big, secs_big = rows_a[-1]
    rate = calls_big / secs_big
    f1001 = true_fib(1001)
    calls_1000 = 2 * f1001 - 1
    print(f"\nPart 3.5: Estimate A n=1000: calls ~ 2*F(1001)-1 = {len(str(calls_1000))} digits")
    print(f"  measured rate {rate:.0f} calls/sec")

    # Part 4.1: default limit
        #here we check the default recursion limit and attempt to run fib_b with n=1000. If it fails due to a RecursionError, we catch the exception and print an error message.
    print(f"\nPart 4.1: default recursion limit = {sys.getrecursionlimit()}")
    try:
        run_b(1000)
        print(" n=1000 worked at default limit")
    except RecursionError as e:
        print(f" n=1000 failed: {e}")

    # Part 4.2: fixes
    print("\nPart 4.2: Two fixes for n=1000")
    v1, c1, s1 = fib_b_raised_limit(1000)
    print(f" Fix1 raise limit: calls={c1} time={s1:.6f}s")
    v2 = fib_iterative(1000)
    print(f" Fix2 iterative: value={str(v2)[:15]}... digits={len(str(v2))}")

    # Part 4.3
    print("\nPart 4.3: Truthy check")
    for n in [0, 1, 2, 5, 20]:
        vt, ct = run_truthy(n)
        vc, cc, _ = run_b(n)
        print(f" n={n} correct_calls={cc} truthy_calls={ct} same_value={vc==vt}")

    # Part 2.3: Plot 
        # here we attempt to plot the results of the experiments using matplotlib. We create two subplots: one for Algorithm A with a logarithmic y-axis and one for Algorithm B with a linear y-axis. The measured data points are plotted alongside the theoretical values for comparison. If matplotlib is not installed, an ImportError is caught, and a message is printed to inform the user.
    try:
        import matplotlib.pyplot as plt
        na = [r[0] for r in rows_a]
        ca = [r[1] for r in rows_a]
        nb = [r[0] for r in rows_b]
        cb = [r[1] for r in rows_b]
        
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        xs = list(range(0, max(na)+1))
        ax[0].plot(xs, [2*true_fib(x+1)-1 for x in xs], label="2F(n+1)-1")
        ax[0].plot(na, ca, "o", label="measured")
        ax[0].set_yscale("log")
        ax[0].set_title("Algorithm A (log y-axis)")
        ax[0].set_xlabel("n")
        ax[0].set_ylabel("calls (log)")
        ax[0].legend()
        ax[0].grid(True, alpha=0.3)

        ax[1].plot(list(range(1,1001)), [2*x-1 for x in range(1,1001)], label="2n-1")
        ax[1].plot(nb, cb, "o", label="measured")
        ax[1].set_title("Algorithm B (linear)")
        ax[1].set_xlabel("n")
        ax[1].set_ylabel("calls")
        ax[1].legend()
        ax[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("fib_calls.png", dpi=150)
        print("\nSaved fib_calls.png")
    except ImportError:
        print("\nmatplotlib not installed: pip install matplotlib to plot")

if __name__ == "__main__":
    main()
