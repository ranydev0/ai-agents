import httpx
from configuration.constants import NL_URL


async def get_light_state() -> dict:
    """
    Retrieve the full current state of the room light.

    Use this tool when you need details about the light such as whether it is on,
    its brightness, colour mode, colour temperature, hue, or saturation.

    Returns:
        dict: The full light state from the API, including:
            - on (dict): Power state, e.g. {"value": False}.
            - brightness (dict): Brightness level, e.g. {"value": 100, "max": 100, "min": 0}.
            - colorMode (str): Active colour mode, e.g. "hs".
            - ct (dict): Colour temperature in Kelvin, e.g. {"value": 2700, "max": 6500, "min": 1200}.
            - hue (dict): Hue angle, e.g. {"value": 30, "max": 360, "min": 0}.
            - sat (dict): Saturation level, e.g. {"value": 67, "max": 100, "min": 0}.

    Raises:
        ValueError: The request was malformed (400).
        PermissionError: Authentication failed or access is denied (401).
        LookupError: The light resource could not be found (404).
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NL_URL}/state")
            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 400:
            raise ValueError(f"Bad request to light API: {e.response.text}") from e
        elif status == 401:
            raise PermissionError(
                f"Unauthorized access to light API: {e.response.text}"
            ) from e
        elif status == 404:
            raise LookupError(f"Light resource not found: {e.response.text}") from e
        raise


async def switch_light(user_value: bool | None = None) -> str:
    """
    Turn the room light on or off, or toggle it if no user_value is provided.

    Use this tool to explicitly turn the light on (user_value=True), turn it off (user_value=False),
    or toggle it to the opposite of its current state (no user_value provided).

    Args:
        user_value (bool | None): True to turn on, False to turn off, None to toggle.

    Returns:
        str: "Light switched on successfully." or "Light switched off successfully."
             if the request succeeds (204 No Content), or "Failed to switch light." otherwise.
             Returns "Light is already on." or "Light is already off." if the light is
             already in the requested state.

    Raises:
        ValueError: The request was malformed (400).
        PermissionError: Authentication failed or access is denied (401).
        LookupError: The light resource could not be found (404).
    """
    current_state = await get_light_state()
    is_on = current_state.get("on", {}).get("value", False)

    if user_value is True and is_on:
        return "Light is already on."
    if user_value is False and not is_on:
        return "Light is already off."

    new_value = not is_on if user_value is None else user_value
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{NL_URL}/state",
                json={"on": {"value": new_value}},
            )
            response.raise_for_status()
            if response.status_code == 204:
                return f"Light switched {'on' if new_value else 'off'} successfully."
            return "Failed to switch light."
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 400:
            raise ValueError(f"Bad request to light API: {e.response.text}") from e
        elif status == 401:
            raise PermissionError(
                f"Unauthorized access to light API: {e.response.text}"
            ) from e
        elif status == 404:
            raise LookupError(
                f"Light resource could not be found: {e.response.text}"
            ) from e
        raise
