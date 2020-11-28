import json
from helpers.retrying import Retrying


def make_request(request_function, fail_on_status_code=True, **kwargs):
    retrying_success, response = Retrying().start(
        lambda: request_function(**kwargs),
        lambda res: \
            res.ok and
            (
                    'errors' in (body := json.loads(res.content.decode())) and
                    body['errors'] is False
            ) or
            'errors' not in (body)
    )

    if not retrying_success and fail_on_status_code:
        raise Exception(response.content.decode())
    else:
        return response
