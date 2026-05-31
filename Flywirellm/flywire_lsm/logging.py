import logging
import os
import sys
import time


class _MicrosecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ts = time.strftime("%H:%M:%S", time.localtime(record.created))
        ms = int((record.created - int(record.created)) * 1_000_000)
        return f"{ts}.{ms:06d}"


class FlyWireLogger:
    FORMAT = "[%(asctime)s] [%(levelname)-7s] %(message)s"

    @staticmethod
    def get_logger(name: str = "FlyWireLSM", level: int = logging.DEBUG) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(_MicrosecondFormatter(FlyWireLogger.FORMAT))
        logger.handlers.clear()
        logger.addHandler(handler)
        return logger

    @staticmethod
    def log_memory(logger: logging.Logger, tag: str) -> None:
        try:
            import psutil
            rss = psutil.Process(os.getpid()).memory_info().rss / 1048576
            logger.info("[MEM] %s: RSS=%.2f MB", tag, rss)
        except ImportError:
            try:
                with open(f"/proc/{os.getpid()}/status") as f:
                    for line in f:
                        if line.startswith("VmRSS:"):
                            rss = float(line.split()[1]) / 1024
                            logger.info("[MEM] %s: RSS~%.2f MB", tag, rss)
                            break
            except Exception:
                pass


_LOG = FlyWireLogger.get_logger()


def get_logger() -> logging.Logger:
    return _LOG
