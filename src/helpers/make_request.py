import time

max_retries = 20
multiplier = 1.1

def make_request(request_function, fail_on_status_code=True, waiting_time: float = 5, retries=1, **kwargs):
    response = request_function(**kwargs)

    if (response.ok):
        return response

    # if server error, retry the request
    if (retries <= max_retries and response.status_code >= 500):
        print(f"Retrying #{retries}: {response.content.decode()}\n")
        time.sleep(waiting_time)
        return make_request(
            request_function,
            fail_on_status_code,
            waiting_time=waiting_time * multiplier,
            retries=retries + 1,
            **kwargs)

    # if max_retries is exceeded or error is 4XX
    if (fail_on_status_code):
        raise Exception(response.content.decode())
    else:
        return response
