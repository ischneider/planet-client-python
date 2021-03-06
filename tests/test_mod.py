# Copyright 2015 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Test the low-level client up to the request/response level. That is, verify
a request is made to the expected URL and the response is as provided. Unless
specifically needed (e.g., JSON format), the response content should not
matter'''

import os

from planet import api
import pytest
import requests_mock

# have to clear in case key is picked up via env
if api.auth.ENV_KEY in os.environ:
    os.environ.pop(api.auth.ENV_KEY)


@pytest.fixture()
def client():
    return api.Client('foobar')


def test_assert_client_execution_success(client):
    '''verify simple mock success response'''
    with requests_mock.Mocker() as m:
        uri = os.path.join(client.base_url, 'whatevs')
        m.get(uri, text='test', status_code=200)
        assert 'test' == client._get('whatevs').get_body().get_raw()


def test_missing_api_key():
    '''verify exception raised on missing API key'''
    client = api.Client(api_key=None)
    try:
        client._get('whatevs').get_body()
    except api.exceptions.InvalidAPIKey as ex:
        assert str(ex) == 'No API key provided'
    else:
        assert False


def test_status_code_404(client):
    '''Verify 404 handling'''
    with requests_mock.Mocker() as m:
        uri = os.path.join(client.base_url, 'whatevs')
        m.get(uri, text='test', status_code=404)
        try:
            client._get('whatevs').get_body()
        except api.exceptions.MissingResource as ex:
            assert str(ex) == 'test'
        else:
            assert False


def test_status_code_other(client):
    '''Verify other unexpected HTTP status codes'''
    with requests_mock.Mocker() as m:
        uri = os.path.join(client.base_url, 'whatevs')
        # yep, this is totally made up
        m.get(uri, text='emergency', status_code=911)
        try:
            client._get('whatevs').get_body()
        except api.exceptions.APIException as ex:
            assert str(ex) == '911: emergency'
        else:
            assert False


def test_fetch_scene_info_scene_id(client):
    '''Verify get_scene_metadata path handling'''
    with requests_mock.Mocker() as m:
        uri = os.path.join(client.base_url, 'scenes/ortho/x22')
        m.get(uri, text='bananas', status_code=200)
        client.get_scene_metadata('x22').get_raw() == 'bananas'
