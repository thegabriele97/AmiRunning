import fitbitPackage.fitbit
import fitbitPackage.gather_keys_oauth2 as Oauth2
import datetime

class FitbiAapi:
    __client_id__ = None
    __client_secret__ = None
    __server__ = None
    __access_token__ = None
    __refresh_token__ = None
    __auth_client__ = None

    def __init__(self, client_id, client_secret):
        self.__client_id__ = client_id
        self.__client_secret__ = client_secret
        self.__server__ = Oauth2.OAuth2Server(self.__client_id__, self.__client_secret__)
    
    def get_authorize_url(self):
        return self.__server__.get_authorize_url()

    def start_response_poll(self):
        self.__server__.start_response_poll()
        self.__access_token__ = str(self.__server__.fitbit.client.session.token['access_token'])
        self.__refresh_token__ = str(self.__server__.fitbit.client.session.token['refresh_token'])
        self.__auth_client__ = fitbitPackage.fitbit.Fitbit(self.__client_id__, self.__client_secret__, oauth2=True, access_token=self.__access_token__, refresh_token=self.__refresh_token__)

    def get_auth_client(self) -> fitbitPackage.fitbit.Fitbit:
        return self.__auth_client__


def get_right_dateFormat(offset: int = 0) -> str:
    return str((datetime.datetime.now() - datetime.timedelta(days=offset)).strftime("%Y-%m-%d"))
