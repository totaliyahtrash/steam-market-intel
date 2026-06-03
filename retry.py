import time
import logging

logger = logging.getLogger('retry')


def with_retry(func, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == retries:
                logger.error(f"All {retries} retry attempts failed. Raising error.")
                raise e

            logger.warning(f"Attempt {attempt}/{retries} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
