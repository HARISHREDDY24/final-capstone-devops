#!/usr/bin/env python3
"""Small standard-library load generator for observing request metrics / HPA."""
import argparse
import concurrent.futures
import time
import urllib.error
import urllib.request


def hit(url: str, timeout: float) -> tuple[bool, float, str]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            response.read(128)
            return 200 <= response.status < 400, time.perf_counter() - started, str(response.status)
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, time.perf_counter() - started, type(exc).__name__


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000/health", help="Endpoint URL to request repeatedly")
    parser.add_argument("--seconds", type=int, default=30, help="Run duration in seconds")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent worker count")
    parser.add_argument("--timeout", type=float, default=3.0, help="Per-request timeout in seconds")
    args = parser.parse_args()
    if args.seconds < 1 or args.workers < 1:
        parser.error("--seconds and --workers must be positive")

    deadline = time.monotonic() + args.seconds
    total = failed = 0
    durations: list[float] = []
    print(f"Sending requests to {args.url} for ~{args.seconds}s with {args.workers} workers")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = set()
        while time.monotonic() < deadline or pending:
            while time.monotonic() < deadline and len(pending) < args.workers * 3:
                pending.add(pool.submit(hit, args.url, args.timeout))
            done, pending = concurrent.futures.wait(
                pending, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future in done:
                ok, duration, code = future.result()
                total += 1
                failed += not ok
                durations.append(duration)
                if total % 100 == 0:
                    print(f"completed={total} errors={failed} last_status={code}")
    durations.sort()
    p95 = durations[min(len(durations) - 1, int(len(durations) * 0.95))] if durations else 0
    print(f"Finished: requests={total}, errors={failed}, p95_seconds={p95:.4f}")


if __name__ == "__main__":
    main()
