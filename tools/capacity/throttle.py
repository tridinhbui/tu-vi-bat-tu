"""Approximates a CFS CPU quota for one process: run for fraction*100ms, SIGSTOP for the rest of each 100ms period."""
import os, signal, sys, time
pid, frac = int(sys.argv[1]), float(sys.argv[2]); period = 0.1; run = period * frac
def cont(*_): 
    try: os.kill(pid, signal.SIGCONT)
    except ProcessLookupError: pass
    sys.exit(0)
signal.signal(signal.SIGTERM, cont); signal.signal(signal.SIGINT, cont)
while True:
    t = time.perf_counter()
    try: os.kill(pid, signal.SIGCONT)
    except ProcessLookupError: break
    time.sleep(run)
    try: os.kill(pid, signal.SIGSTOP)
    except ProcessLookupError: break
    time.sleep(max(0, period - (time.perf_counter() - t)))
