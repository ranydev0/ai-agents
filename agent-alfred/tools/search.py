import serpapi
from configuration.constants import SEARCH_API
from smolagents import tool


@tool
def get_search_results(search_query: str) -> list:
    """
    Search the web using Google and return an AI-generated overview as structured text blocks.

    Use this tool when you need up-to-date information from the web, such as current events,
    facts, definitions, or any topic that benefits from a live search.

    Args:
        search_query: The query string to search for on Google.

    Returns:
        A list of text block dicts representing the AI overview of the search results.
        Each block has a 'type' field, which is either 'paragraph' or 'list':

        - Paragraph block:
            {
                'type': 'paragraph',
                'snippet': str,                  # Summary text for this paragraph
                'reference_indexes': list[int]   # Optional. Indexes into the source references
            }

        - List block:
            {
                'type': 'list',
                'list': [
                    {'snippet': str},  # Each item is a short text snippet
                    ...
                ]
            }

        Example:
            [
                {'type': 'paragraph', 'snippet': 'Cybersecurity is the practice of ...', 'reference_indexes': [2, 5]},
                {'type': 'paragraph', 'snippet': 'Key components of cybersecurity include:'},
                {'type': 'list', 'list': [{'snippet': 'Network Security: ...'}, ...]},
                {'type': 'paragraph', 'snippet': 'Common threats include phishing ...', 'reference_indexes': [0, 1]}
            ]

        Returns an empty string if no AI overview is available for the query.
    """
    search_results = serpapi.search(
        engine="google",
        q=search_query,
        location="Sydney, New South Wales, Australia",
        google_domain="google.com.au",
        hl="en",
        gl="au",
        api_key=SEARCH_API,
    )

    return search_results.get("ai_overview", {}).get("text_blocks", [])
