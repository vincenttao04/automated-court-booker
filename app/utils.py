# Utility function to check the status of an API response
def check_status(data: dict, action: str) -> None:
    if data.get("status") != "success":
        raise RuntimeError(f"{action} FAILED: {data.get('message', 'Unknown error')}")
