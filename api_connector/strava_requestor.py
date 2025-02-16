from api_connector.authenticator import OAuth2Authenticator
import requests
import pandas as pd
from typing import List


class StravaRequestor():

    def __init__(self,
                 connection_path:str,
                 secret_path:str):
        self.authenticator = OAuth2Authenticator(connection_path=connection_path, 
                                                 secrets_path=secret_path,
                                                 scope="activity:read_all")
        self.base_url = self.authenticator.connection.get("base_url")

    def make_strava_get_request(self,
                            endpoint:str,
                            query_params:dict = None):
        assert len(endpoint) > 0, "Pass a valid endpoint!"
        endpoint_url = self.base_url + ("/" if endpoint[0] != "/" else "") + endpoint
        access_token = self.authenticator.get_access_token()
        query_params_with_access_token = query_params if query_params else dict()
        query_params_with_access_token.update({'access_token': access_token})
        token_response = requests.get(
            endpoint_url,
            params=query_params_with_access_token
        )
        if token_response.ok:
            return token_response
        else:
            print(f"Error in token exchange: {token_response.status_code}, {token_response.text}")
            token_response.raise_for_status()


    def get_last_activities_overview(self, 
                                     last_x_activities:int = None):
        endpoint = 'athlete/activities'
        activities_json = self.make_strava_get_request(endpoint).json()
        activities = pd.DataFrame(activities_json)
        activities['distance_km'] = activities['distance'] / 1_000
        sel_activities = activities\
            .sort_values(by="start_date_local", ascending=False)\
            .head(last_x_activities)
        return sel_activities
    
    
    def merge_and_upload_activities(self,
                                    id_list:List[int]):
        # TODO: problem so far:
        # Only routes are extractable via the Strava API (I do not have any routes though because I am not a premium Strava member).
        # A route is also not the same as GPX sequences
        pass
