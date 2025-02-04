import json
from time import time
from random import random
from contextlib import contextmanager
from mimetypes import guess_type
from os.path import basename
from urllib.parse import parse_qs, urlparse
from .models import (
FBchatException,
    FBchatFacebookError,
    FBchatInvalidParameters,
    FBchatNotLoggedIn,
    FBchatPleaseRefresh,
)

def now():
    return int(time() * 1000)


def json_minimal(data):
    """Get JSON data in minimal form."""
    return json.dumps(data, separators=(",", ":"))


def strip_json_cruft(text):
    """Removes `for(;;);` (and other cruft) that preceeds JSON responses."""
    try:
        return text[text.index("{") :]
    except ValueError:
        raise FBchatException("No JSON object found: {!r}".format(text))


def get_decoded_r(r):
    return get_decoded(r._content)


def get_decoded(content):
    return content.decode("utf-8")


def parse_json(content):
    try:
        return json.loads(content)
    except ValueError:
        raise FBchatFacebookError("Error while parsing JSON: {!r}".format(content))


def digitToChar(digit):
    if digit < 10:
        return str(digit)
    return chr(ord("a") + digit - 10)


def str_base(number, base):
    if number < 0:
        return "-" + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digitToChar(m)
    return digitToChar(m)


def generateMessageID(client_id=None):
    k = now()
    l = int(random() * 4294967295)
    return "<{}:{}-{}@mail.projektitan.com>".format(k, l, client_id)


def getSignatureID():
    return hex(int(random() * 2147483648))


def generateOfflineThreadingID():
    ret = now()
    value = int(random() * 4294967295)
    string = ("0000000000000000000000" + format(value, "b"))[-22:]
    msgs = format(ret, "b") + string
    return str(int(msgs, 2))


def handle_payload_error(j):
    if "error" not in j:
        return
    error = j["error"]
    if j["error"] == 1357001:
        error_cls = FBchatNotLoggedIn
    elif j["error"] == 1357004:
        error_cls = FBchatPleaseRefresh
    elif j["error"] in (1357031, 1545010, 1545003):
        error_cls = FBchatInvalidParameters
    else:
        error_cls = FBchatFacebookError
    # TODO: Use j["errorSummary"]
    # "errorDescription" is in the users own language!
    raise error_cls(
        "Error #{} when sending request: {}".format(error, j["errorDescription"]),
        fb_error_code=error,
        fb_error_message=j["errorDescription"],
    )


def handle_graphql_errors(j):
    errors = []
    if j.get("error"):
        errors = [j["error"]]
    if "errors" in j:
        errors = j["errors"]
    if errors:
        error = errors[0]  # TODO: Handle multiple errors
        # TODO: Use `summary`, `severity` and `description`
        raise FBchatFacebookError(
            "GraphQL error #{}: {} / {!r}".format(
                error.get("code"), error.get("message"), error.get("debug_info")
            ),
            fb_error_code=error.get("code"),
            fb_error_message=error.get("message"),
        )


def check_request(r):
    check_http_code(r.status_code)
    content = get_decoded_r(r)
    check_content(content)
    return content

async def async_check_request(r):
    check_http_code(r.status)
    content = r.text(encoding="utf-8")
    check_content(content)
    return content


def check_http_code(code):
    msg = "Error when sending request: Got {} response.".format(code)
    if code == 404:
        raise FBchatFacebookError(
            msg + " This is either because you specified an invalid URL, or because"
            " you provided an invalid id (Facebook usually requires integer ids).",
            request_status_code=code,
        )
    if 400 <= code < 600:
        raise FBchatFacebookError(msg, request_status_code=code)


def check_content(content, as_json=True):
    if content is None or len(content) == 0:
        raise FBchatFacebookError("Error when sending request: Got empty response")


def to_json(content):
    content = strip_json_cruft(content)
    j = parse_json(content)
    return j


def get_jsmods_require(j, index):
    if j.get("jsmods") and j["jsmods"].get("require"):
        try:
            return j["jsmods"]["require"][0][index][0]
        except (KeyError, IndexError):
            print(
                "Error when getting jsmods_require: "
                "{}. Facebook might have changed protocol".format(j)
            )
    return None


def require_list(list_):
    if isinstance(list_, list):
        return set(list_)
    else:
        return set([list_])


def mimetype_to_key(mimetype):
    if not mimetype:
        return "file_id"
    if mimetype == "image/gif":
        return "gif_id"
    x = mimetype.split("/")
    if x[0] in ["video", "image", "audio"]:
        return "%s_id" % x[0]
    return "file_id"




@contextmanager
def get_files_from_paths(filenames):
    files = []
    for filename in filenames:
        files.append(
            (basename(filename), open(filename, "rb"), guess_type(filename)[0])
        )
    yield files
    for fn, fp, ft in files:
        fp.close()


def get_url_parameters(url, *args):
    params = parse_qs(urlparse(url).query)
    return [params[arg][0] for arg in args if params.get(arg)]


def get_url_parameter(url, param):
    return get_url_parameters(url, param)[0]


def prefix_url(url):
    if url.startswith("/"):
        return "https://www.facebook.com" + url
    return url
