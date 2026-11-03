import logging
import time
from contextlib import contextmanager

log = logging.getLogger("pipeline")

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("data/pipeline.log")],
    )

@contextmanager
def stage(name):
    start = time.perf_counter()
    log.info("start %s", name)
    try:
        yield
    finally:
        log.info("end %s (%.1fs)", name, time.perf_counter() - start)