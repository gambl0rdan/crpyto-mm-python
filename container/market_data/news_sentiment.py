import requests
import json
import threading
# http://127.0.0.1:5000/get-bitcoin-latest
URL = "https://brighter-news-api-heroku.herokuapp.com/get-bitcoin-latest"


class RequestWrapper:


# class SentimentWorker(threading.Thread):
#
#     def __init__(self, threadID, name):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.name = name

    data = []

    def __init__(self):
        pass

    def start(self):
        # in seconds
        t = perpetualTimer(60 * 2, get_request)
        t.start()


def get_request():

    # api_url = '{0}account'.format(api_url_base)
    #
    api_url = URL
    response = requests.get(api_url, headers=[])

    if response.status_code == 200:
        resp = json.loads(response.content.decode('utf-8'))
        if 'result' in resp:
            RequestWrapper.data.append(resp['result'])
            print(RequestWrapper.data)
    else:
        pass
        # return None


class perpetualTimer:

    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


# t1 = SentimentWorker(1, "my-thread")
# t1.start()
# results = get_response()
# print(data)

