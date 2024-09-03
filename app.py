import requests
import logging
import os
import datetime

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

def get_blocklist(instance):
    """Fetch the current blocklist."""
    logger.info(f"Fetching blocklist from {instance['url']}")
    url = f"{instance['url']}/api/v3/blocklist"
    headers = {
        "X-Api-Key": instance['api_key']
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        blocklist = response.json()
        logger.info(f"Fetched blocklist from {instance['url']}: {blocklist}")
        return [item['id'] for item in blocklist]  # Adjust based on actual response structure
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching blocklist on {instance['url']} at {datetime.datetime.now()}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred while fetching blocklist on {instance['url']} at {datetime.datetime.now()}: {req_err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching blocklist on {instance['url']} at {datetime.datetime.now()}: {e}")
    return []

def clear_blocklist(instance):
    """Clear the blocklist using bulk delete."""
    logger.info(f"Starting blocklist clearance for {instance['url']} at {datetime.datetime.now()}")
    url = f"{instance['url']}/api/v3/blocklist/bulk"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": instance['api_key']
    }
    
    # Step 1: Fetch current blocklist
    blocklist_ids = get_blocklist(instance)
    if not blocklist_ids:
        logger.info(f"No blocklist items to clear on {instance['url']}")
        return
    
    # Step 2: Define the request body with the list of IDs
    data = {
        "ids": blocklist_ids
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            logger.info(f"Successfully cleared blocklist on {instance['url']}")
        else:
            response_json = response.json()
            logger.error(f"Failed to clear blocklist on {instance['url']}: {response.status_code}, {response_json}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred while clearing blocklist on {instance['url']} at {datetime.datetime.now()}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred while clearing blocklist on {instance['url']} at {datetime.datetime.now()}: {req_err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while clearing blocklist on {instance['url']} at {datetime.datetime.now()}: {e}")
    finally:
        logger.info(f"Finished blocklist clearance for {instance['url']} at {datetime.datetime.now()}")

def trigger_search(instance):
    """Trigger a search for missing movies."""
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

def main_startup():
    """Run both search and blocklist clearance tasks at startup."""
    logger.info("Starting script execution at container startup")
    for instance in RADARR_INSTANCES:
        logger.info(f"Processing instance: {instance['url']}")
        trigger_search(instance)
        clear_blocklist(instance)
    logger.info("Container startup script execution completed")

def main():
    """Determine and run the task specified by the TASK environment variable."""
    task = os.getenv('TASK', 'search')
    logger.info(f"Running task: {task}")
    
    if task == 'startup':
        main_startup()
    elif task == 'search':
        logger.info("Running search tasks")
        for instance in RADARR_INSTANCES:
            logger.info(f"Processing instance: {instance['url']}")
            trigger_search(instance)
    elif task == 'clear_blocklist':
        logger.info("Running clear blocklist tasks")
        for instance in RADARR_INSTANCES:
            logger.info(f"Processing instance: {instance['url']}")
            clear_blocklist(instance)
    logger.info("Script execution completed")

if __name__ == "__main__":
    main()
