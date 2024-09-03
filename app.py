import requests
import logging
import os
from datetime import datetime

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs to stdout
    ]
)

logger = logging.getLogger(__name__)

# Fetch environment variables
RADARR_INSTANCES = [
    {"url": os.getenv("RADARR_URL_1"), "api_key": os.getenv("RADARR_API_KEY_1")},
    {"url": os.getenv("RADARR_URL_2"), "api_key": os.getenv("RADARR_API_KEY_2")},
    {"url": os.getenv("RADARR_URL_3"), "api_key": os.getenv("RADARR_API_KEY_3")}
]

def trigger_search(instance):
    logger.info(f"Starting search trigger for {instance['url']}")
    url = f"{instance['url']}/api/v3/command"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": instance['api_key']
    }
    data = {
        "name": "missingMoviesSearch"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 201:
            logger.info(f"Successfully triggered search for missing movies on {instance['url']}")
        else:
            response_json = response.json()
            logger.error(f"Failed to trigger search on {instance['url']}: {response.status_code}, {response_json}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred while triggering search on {instance['url']}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred while triggering search on {instance['url']}: {req_err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while triggering search on {instance['url']}: {e}")

def clear_blocklist(instance):
    logger.info(f"Starting blocklist clearance for {instance['url']} at {datetime.now()}")
    url = f"{instance['url']}/api/v3/blocklist"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": instance['api_key']
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            logger.info(f"Successfully cleared blocklist on {instance['url']} at {datetime.now()}")
        else:
            response_json = response.json()
            logger.error(f"Failed to clear blocklist on {instance['url']} at {datetime.now()}: {response.status_code}, {response_json}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred while clearing blocklist on {instance['url']} at {datetime.now()}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred while clearing blocklist on {instance['url']} at {datetime.now()}: {req_err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while clearing blocklist on {instance['url']} at {datetime.now()}: {e}")

def main_startup():
    logger.info("Starting script execution at container startup")
    for instance in RADARR_INSTANCES:
        logger.info(f"Processing instance: {instance['url']}")
        trigger_search(instance)
        clear_blocklist(instance)
    logger.info("Container startup script execution completed")

def main():
    task = os.getenv('TASK', 'search')
    logger.info(f"Running task: {task}")
    
    if task == 'startup':
        main_startup()
    elif task == 'search':
        for instance in RADARR_INSTANCES:
            logger.info(f"Processing instance: {instance['url']}")
            trigger_search(instance)
    elif task == 'clear_blocklist':
        for instance in RADARR_INSTANCES:
            logger.info(f"Processing instance: {instance['url']}")
            clear_blocklist(instance)
    logger.info("Script execution completed")

if __name__ == "__main__":
    main()
