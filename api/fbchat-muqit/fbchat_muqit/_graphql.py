import json
from typing import List, Union, Dict, Any
from . import _util
from .models import FBchatException

# Lord Yuuta doesnt copy he invents

def split_json_objects(json_string: str)-> List[Dict[str, Any]]:
    # Remove very long spaces
    json_string = "".join(json_string.split())
    # Json string contains list of json objects without the `[` and `]` 

    # We need to parse them into a list of Dict in order to use json.loads()
    depth = 0
    start = 0
    results = []
    
    for i, char in enumerate(json_string):
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                results.append(json_string[start:i+1])
    
    return [json.loads(chunk) for chunk in results]



def queries_to_json(*queries)-> str:
    """
    queries should be a list/tuple of GraphQL objects
    returns Json string.
    """
    rtn = {
        f"q{i}": query for i, query in enumerate(queries)
    }
    return json.dumps(rtn)


def response_to_json(content)-> List[Union[None, Dict[str, Any]]]:
    """
    Process JSON-like content and extract data into a structured list.

    Args:
        content (str): The raw JSON string to process.

    Returns:
        List[Union[None, Dict[str, Any]]]: A list where each index corresponds to a parsed JSON object.
        - None: If no valid data is found for that index.
        - Dict[str, Any]: If valid JSON data is found at that index.
    """
    # Remove unwanted characters from the content
    content = _util.strip_json_cruft(content)
    # Parse JSON objects
    try:
        parsed_objects = split_json_objects(content)
    except Exception as e:
        raise FBchatException(f"Error while parsing JSON: {repr(content)}") from e
    # Initialize the result list
    results = [None] * len(parsed_objects)
    for obj in parsed_objects:
        # Skip objects with "error_results"
        if "error_results" in obj:
            results.pop()  # Remove the last element
            continue
        # Handle potential errors in the payload and GraphQL
        _util.handle_payload_error(obj)
        [(key, value)] = obj.items()
        _util.handle_graphql_errors(value)
        # Extract response or data
        index = int(key[1:])  # Extract numeric part from key (e.g., "q0" -> 0)
        if "response" in value:
            results[index] = value["response"]
        else:
            results[index] = value["data"]
    return results  #type: ignore


def from_query(query, params):
    return {"priority": 0, "q": query, "query_params": params}


def from_query_id(query_id, params):
    return {"query_id": query_id, "query_params": params}


def from_doc(doc, params):
    return {"doc": doc, "query_params": params}


def from_doc_id(doc_id, params):
    return {"doc_id": doc_id, "query_params": params}


FRAGMENT_USER = """
QueryFragment User: User {
    id,
    name,
    first_name,
    last_name,
    profile_picture.width(<pic_size>).height(<pic_size>) {
        uri
    },
    is_viewer_friend,
    url,
    gender,
    viewer_affinity
}
"""

FRAGMENT_GROUP = """
QueryFragment Group: MessageThread {
    name,
    thread_key {
        thread_fbid
    },
    image {
        uri
    },
    is_group_thread,
    all_participants {
        nodes {
            messaging_actor {
                id
            }
        }
    },
    customization_info {
        participant_customizations {
            participant_id,
            nickname
        },
        outgoing_bubble_color,
        emoji
    },
    thread_admins {
        id
    },
    group_approval_queue {
        nodes {
            requester {
                id
            }
        }
    },
    approval_mode,
    joinable_mode {
        mode,
        link
    },
    event_reminders {
        nodes {
            id,
            lightweight_event_creator {
                id
            },
            time,
            location_name,
            event_title,
            event_reminder_members {
                edges {
                    node {
                        id
                    },
                    guest_list_state
                }
            }
        }
    }
}
"""

FRAGMENT_PAGE = """
QueryFragment Page: Page {
    id,
    name,
    profile_picture.width(32).height(32) {
        uri
    },
    url,
    category_type,
    city {
        name
    }
}
"""

SEARCH_USER = (
    """
Query SearchUser(<search> = '', <limit> = 10) {
    entities_named(<search>) {
        search_results.of_type(user).first(<limit>) as users {
            nodes {
                @User
            }
        }
    }
}
"""
    + FRAGMENT_USER
)

SEARCH_GROUP = (
    """
Query SearchGroup(<search> = '', <limit> = 10, <pic_size> = 32) {
    viewer() {
        message_threads.with_thread_name(<search>).last(<limit>) as groups {
            nodes {
                @Group
            }
        }
    }
}
"""
    + FRAGMENT_GROUP
)

SEARCH_PAGE = (
    """
Query SearchPage(<search> = '', <limit> = 10) {
    entities_named(<search>) {
        search_results.of_type(page).first(<limit>) as pages {
            nodes {
                @Page
            }
        }
    }
}
"""
    + FRAGMENT_PAGE
)

SEARCH_THREAD = (
    """
Query SearchThread(<search> = '', <limit> = 10) {
    entities_named(<search>) {
        search_results.first(<limit>) as threads {
            nodes {
                __typename,
                @User,
                @Group,
                @Page
            }
        }
    }
}
"""
    + FRAGMENT_USER
    + FRAGMENT_GROUP
    + FRAGMENT_PAGE
)
