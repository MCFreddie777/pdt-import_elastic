def make_request(request_function, fail_on_status_code=True, **kwargs):
    response = request_function(**kwargs)

    if (fail_on_status_code and response.ok is False):
        raise Exception(response.content.decode())

    return response
