#!/usr/bin/env python3
"""Measure cold and warm latency of the deployed chat backend.

Standard library only, so it runs anywhere with Python 3.

How to get an honest cold-start number
--------------------------------------
Render's free tier puts a service to sleep after a period of inactivity (about
15 minutes). Leave BOTH services untouched for 20+ minutes, then run:

    python3 scripts/measure_latency.py

The script makes one GET /health (wakes the backend) and then several
POST /api/chat requests. The first chat also wakes the embedding service, so it
is the slowest question. The rest are warm. The chat endpoint allows 5 requests
per hour per client IP, so the script sends at most 5 and stops on a 429.

It prints a Markdown table you can paste into the README. It reports what it
measured, from where you ran it; it does not know whether the service was really
asleep, so it flags a fast first response instead of calling it a cold start.
"""
import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import date

DEFAULT_URL = "https://portfolio-react-app-ed20.onrender.com"
QUESTIONS = [
    "What is your cloud experience?",
    "Which programming languages do you use?",
    "Where did you study?",
    "What projects have you built?",
    "What are you looking for in your next role?",
]
COLD_THRESHOLD_S = 5.0  # a first /health faster than this was probably not a cold start


def timed_request(req: urllib.request.Request, timeout: float):
    """Return (status, seconds). Status is an int, or a string describing the failure."""
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            status = resp.status
    except urllib.error.HTTPError as err:
        err.read()
        status = err.code
    except Exception as err:  # timeouts, DNS, connection errors
        status = f"{type(err).__name__}"
    return status, time.perf_counter() - start


def chat_request(base_url: str, question: str) -> urllib.request.Request:
    body = json.dumps({"message": question, "language": "en", "history": []}).encode()
    return urllib.request.Request(
        f"{base_url}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", default=DEFAULT_URL, help="backend base URL")
    parser.add_argument("--chats", type=int, default=4, help="chat requests to send (1-5)")
    parser.add_argument("--timeout", type=float, default=120, help="per-request timeout, seconds")
    args = parser.parse_args()

    if not 1 <= args.chats <= 5:
        print("--chats must be between 1 and 5 (the endpoint allows 5 per hour per IP)")
        return 2
    base_url = args.url.rstrip("/")

    print(f"Target: {base_url}\n")

    status, health_s = timed_request(urllib.request.Request(f"{base_url}/health"), args.timeout)
    print(f"GET  /health     -> {status}  {health_s:6.2f}s")
    if status != 200:
        print("Backend did not answer /health with 200; aborting.")
        return 1

    chat_times = []
    for i in range(args.chats):
        question = QUESTIONS[i % len(QUESTIONS)]
        status, secs = timed_request(chat_request(base_url, question), args.timeout)
        print(f"POST /api/chat #{i + 1} -> {status}  {secs:6.2f}s  ({question})")
        if status == 429:
            print("Rate limited (5 chats/hour per IP). Wait an hour, or use fewer --chats.")
            break
        if status != 200:
            print("Non-200 response; stopping so the numbers are not misleading.")
            break
        chat_times.append(secs)

    if not chat_times:
        return 1

    first, warm = chat_times[0], chat_times[1:]
    print("\n--- Markdown for the README ---\n")
    print(f"Measured {date.today().isoformat()} against the free-tier deployment "
          f"(one run, from one location):\n")
    print("| Measurement | Time |")
    print("|---|---|")
    print(f"| Backend, first request after idle (`GET /health`) | {health_s:.1f} s |")
    print(f"| First question (embedding service + retrieval + LLM) | {first:.1f} s |")
    if warm:
        print(f"| Warm question, median of {len(warm)} (min {min(warm):.1f} s, max {max(warm):.1f} s) "
              f"| {statistics.median(warm):.1f} s |")

    if health_s < COLD_THRESHOLD_S:
        print("\nNOTE: /health answered in under "
              f"{COLD_THRESHOLD_S:.0f}s, so the backend was probably already warm. "
              "This is not a cold-start measurement. Leave both services idle for "
              "20+ minutes and run it again before publishing the first two rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
