
import sys
import time
import json

# Part 1: Implementation (with a global call counter in each function)
# here we use global variables to count the number of calls to each algorithm. This is not a good practice in general, but it is acceptable for this assignment.
calls_a = 0          # call counter for Algorithm A
calls_b = 0          # call counter for Algorithm B
fibtable = {}        # memo table for Algorithm B


def fib_a(n):
    """Algorithm A: plain recursion."""
    global calls_a
    calls_a += 1
    if n == 0 or n == 1:
        value = n
    else:
        value = fib_a(n - 1) + fib_a(n - 2)
    return value


def fib_b(n):
    """Algorithm B: recursion with memoization."""
    global calls_b
    calls_b += 1
    if n in fibtable:                 # "if fibtable[n] exists"
        return fibtable[n]
    if n == 0 or n == 1:
        value = n
    else:
        value = fib_b(n - 1) + fib_b(n - 2)
    fibtable[n] = value
    return value


def run_a(n):
    """Run Algorithm A once. Returns (value, calls, seconds)."""
    global calls_a
    calls_a = 0
    start = time.perf_counter()
    value = fib_a(n)
    seconds = time.perf_counter() - start
    return value, calls_a, seconds


def run_b(n):
    """Run Algorithm B once, clearing fibtable first."""
    global calls_b
    fibtable.clear()
    calls_b = 0
    start = time.perf_counter()
    value = fib_b(n)
    seconds = time.perf_counter() - start
    return value, calls_b, seconds


def true_fib(n):
    """Reference Fibonacci (simple loop) used only for checking."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# Part 4 fixes
# here we implement two fixes for the recursion limit problem in Algorithm B. The first fix is to raise the recursion limit, and the second fix is to use an iterative approach.
def fib_b_raised_limit(n, limit=5000):
    """Fix 1: keep Algorithm B but raise Python's recursion limit."""
    global calls_b
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, limit))
    try:
        return run_b(n)
    finally:
        sys.setrecursionlimit(old)


def fib_iterative(n):
    """Fix 2: bottom-up (iterative) version. No recursion at all."""
    calls = 0
    if n == 0:
        return 0, 1
    previous, current = 0, 1          # F(0), F(1)
    for _ in range(2, n + 1):
        previous, current = current, previous + current
        calls += 1                    # one loop step = one subproblem solved
    return current, calls


# Part 4, question 3: a table check that treats the stored value 0 as "missing"
# here we implement a version of Algorithm B that uses a "truthy" check for the memoization table. This means that if the stored value is 0, it will be treated as if it is missing, which can lead to incorrect behavior.
fibtable_truthy = {}
calls_truthy = 0


def fib_b_truthy(n):
    """Algorithm B, but the check is 'if fibtable.get(n):' (0 counts as missing)."""
    global calls_truthy
    calls_truthy += 1
    if fibtable_truthy.get(n):        # BUG-prone: False when the stored value is 0
        return fibtable_truthy[n]
    if n == 0 or n == 1:
        value = n
    else:
        value = fib_b_truthy(n - 1) + fib_b_truthy(n - 2)
    fibtable_truthy[n] = value
    return value


def run_truthy(n):
    global calls_truthy
    fibtable_truthy.clear()
    calls_truthy = 0
    value = fib_b_truthy(n)
    return value, calls_truthy


def largest_n_at_default_limit():
    """Find the largest n for which Algorithm B works at the default limit."""
    lo, hi = 1, 3000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        try:
            run_b(mid)
            lo = mid
        except RecursionError:
            hi = mid - 1
    return lo


def main():
    results = {"python": sys.version.split()[0],
               "default_limit": sys.getrecursionlimit()}

    # ---- Part 1.3: both functions agree for n = 0..20 ----
    # here we check that both algorithms produce the same results for n = 0 to 20, and that they match the reference implementation.
    print("Part 1: check n = 0..20")
    all_ok = True
    check_rows = []
    for n in range(21):
        a = run_a(n)[0]
        b = run_b(n)[0]
        ok = (a == b == true_fib(n))
        all_ok = all_ok and ok
        check_rows.append([n, a, b, ok])
        print(f"  n={n:2d}  A={a:5d}  B={b:5d}  equal={ok}")
    print("  All equal:", all_ok)
    results["check"] = check_rows
    results["check_all_ok"] = all_ok

    # ---- Part 2: experiments ----
        # from the results of running both algorithms for various values of n, we will record the number of calls and the time taken for each algorithm. We will also keep track of the largest n for which Algorithm A completes within 60 seconds.
    print("\nAlgorithm A experiments")
    rows_a = []
    largest_a = None
    for n in [5, 10, 15, 20, 25, 30, 35]:
        value, calls, secs = run_a(n)
        rows_a.append([n, calls, secs])
        print(f"  n={n:2d}  calls={calls:>12,}  time={secs:.6f} s")
        if secs > 60:
            print("  Stopped: run took longer than 60 seconds")
            break
        largest_a = n
    results["rows_a"] = rows_a
    results["largest_a"] = largest_a

    print("\nAlgorithm B experiments (default recursion limit)")
    rows_b = []
    n1000_default = None
    for n in [10, 50, 100, 200, 500, 1000]:
        try:
            value, calls, secs = run_b(n)
            rows_b.append([n, calls, secs, "default"])
            print(f"  n={n:4d}  calls={calls:>6,}  time={secs:.6f} s")
        except RecursionError as e:
            n1000_default = f"{type(e).__name__}: {e}"
            print(f"  n={n:4d}  FAILED at default limit -> {n1000_default}")
            value, calls, secs = fib_b_raised_limit(n)
            rows_b.append([n, calls, secs, "raised limit"])
            print(f"  n={n:4d}  (with raised limit)  calls={calls:>6,}  time={secs:.6f} s")
    results["rows_b"] = rows_b
    results["n1000_default_error"] = n1000_default

    # ---- Part 3.5: estimate for Algorithm A at n = 1000 ----
        # from here we will estimate the number of calls and time taken for Algorithm A at n = 1000 based on the measured rate from the largest n we ran.
    n_big, calls_big, secs_big = rows_a[-1]
    rate = calls_big / secs_big
    f1001 = true_fib(1001)
    calls_1000 = 2 * f1001 - 1
    seconds_est = calls_1000 / rate
    results["rate_calls_per_sec"] = rate
    results["calls_a_1000_digits"] = len(str(calls_1000))
    results["calls_a_1000_str"] = str(calls_1000)
    # scientific notation from the big integer
    s = str(calls_1000)
    results["calls_a_1000_sci"] = f"{s[0]}.{s[1:4]}e+{len(s) - 1}"
    t = seconds_est if seconds_est < 1e300 else None
    ts = str(int(calls_1000 // int(rate)))
    results["time_a_1000_sci"] = f"{ts[0]}.{ts[1:4]}e+{len(ts) - 1}"
    results["time_a_1000_years_sci"] = None
    years = int(ts) // (365 * 24 * 3600)
    ys = str(years)
    results["time_a_1000_years_sci"] = f"{ys[0]}.{ys[1:4]}e+{len(ys) - 1}"
    print("\nEstimate for Algorithm A, n = 1000")
    print("  measured rate:", f"{rate:,.0f}", "calls/second")
    print("  calls:", results["calls_a_1000_sci"], " time (s):", results["time_a_1000_sci"],
          " time (years):", results["time_a_1000_years_sci"])

    # ---- Part 4.1: default recursion limit ----
        # rom here we will check if Algorithm B can compute F(1000) at the default recursion limit, and find the largest n that works at the default limit.
    print("\nPart 4.1: default recursion limit =", sys.getrecursionlimit())
    try:
        run_b(1000)
        print("  n=1000 worked at the default limit")
        results["n1000_default_worked"] = True
    except RecursionError as e:
        print("  n=1000 failed:", e)
        results["n1000_default_worked"] = False
        results["n1000_default_error"] = f"RecursionError: {e}"
    largest_default = largest_n_at_default_limit()
    print("  largest n that works at the default limit:", largest_default)
    results["largest_default"] = largest_default

    # ---- Part 4.2: two fixes ----
        # from here we will apply the two fixes for Algorithm B to compute F(1000): raising the recursion limit and using an iterative approach. We will compare the number of calls and time taken for both fixes, and check that they produce the same result as the reference implementation.
    v1, c1, s1 = fib_b_raised_limit(1000)
    v2, c2 = fib_iterative(1000)
    t0 = time.perf_counter()
    fib_iterative(1000)
    s2 = time.perf_counter() - t0
    same = (v1 == v2 == true_fib(1000))
    print("\nPart 4.2: fixes for n = 1000")
    print(f"  Fix 1 (raise limit): calls={c1}, time={s1:.6f} s")
    print(f"  Fix 2 (iterative):   loop steps={c2}, time={s2:.6f} s")
    print("  Same value from both and from reference:", same)
    print("  F(1000) has", len(str(v1)), "digits; starts", str(v1)[:15] + "...")
    results["fix1"] = [c1, s1]
    results["fix2"] = [c2, s2]
    results["fix_same"] = same
    results["f1000_digits"] = len(str(v1))
    results["f1000_start"] = str(v1)[:15]

    # ---- Part 4.3: the 'if fibtable[n]' check with the value 0 ---
        #from here we will check the behavior of Algorithm B when using a "truthy" check for the memoization table, which treats the stored value 0 as missing. We will compare the number of calls and values returned for various n, and check if they match the reference implementation.
    print("\nPart 4.3: check that treats 0 as missing")
    rows_t = []
    for n in [0, 1, 2, 5, 20, 100, 500]:
        v_t, c_t = run_truthy(n)
        v_c, c_c, _ = run_b(n)
        rows_t.append([n, c_c, c_t, v_c == v_t])
        print(f"  n={n:4d}  correct check calls={c_c:4d}  truthy check calls={c_t:4d}  same value={v_c == v_t}")
    results["truthy_rows"] = rows_t

    # ---- Plot ----
        # from here we will plot the number of calls against n for both algorithms, using a logarithmic scale for Algorithm A and a linear scale for Algorithm B. We will also include the theoretical formulas for the number of calls for both algorithms.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        na = [r[0] for r in rows_a]
        ca = [r[1] for r in rows_a]
        nb = [r[0] for r in rows_b]
        cb = [r[1] for r in rows_b]
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

        xs = list(range(0, max(na) + 1))
        ax[0].plot(xs, [2 * true_fib(x + 1) - 1 for x in xs], "-", color="#B0B0B0", label="2F(n+1) - 1 (formula)")
        ax[0].plot(na, ca, "o", color="#C00000", label="measured")
        ax[0].set_yscale("log")
        ax[0].set_title("Algorithm A (log scale on y-axis)")
        ax[0].set_xlabel("n")
        ax[0].set_ylabel("number of calls (log scale)")
        ax[0].legend()
        ax[0].grid(True, which="both", alpha=0.3)

        xb = list(range(1, 1001))
        ax[1].plot(xb, [2 * x - 1 for x in xb], "-", color="#B0B0B0", label="2n - 1 (formula)")
        ax[1].plot(nb, cb, "o", color="#1F3864", label="measured")
        ax[1].set_title("Algorithm B (linear scale)")
        ax[1].set_xlabel("n")
        ax[1].set_ylabel("number of calls")
        ax[1].legend()
        ax[1].grid(True, alpha=0.3)

        fig.suptitle("n against number of function calls")
        fig.tight_layout()
        fig.savefig("fib_calls.png", dpi=170)
        print("\nSaved fib_calls.png")
    except ImportError:
        print("\nmatplotlib not installed: pip install matplotlib to draw the graph")

    with open("results.json", "w") as f:
        json.dump(results, f, indent=1)
    print("Saved results.json")


if __name__ == "__main__":
    main()
