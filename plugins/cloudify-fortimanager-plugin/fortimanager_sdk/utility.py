########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the Licens
from cloudify.exceptions import NonRecoverableError, RecoverableError
import traceback
import yaml
import logging
import ast
import re
import xmltodict
from jinja2 import Template
import requests
from . import LOGGER_NAME
from .exceptions import (
    RecoverableStatusCodeCodeException,
    ExpectationException,
    WrongTemplateDataException,
    NonRecoverableResponseException,
    RecoverableResponseException)

from pyFMG.fortimgr import FortiManager

logger = logging.getLogger(LOGGER_NAME)


#  request_props (port, ssl, verify, hosts )
def process(params, template, request_props):

    logger.debug(
        'process params:\n'
        'params: {}\n'
        'template: {}\n'
        'request_props: {}'.format(params, template, request_props))

    template_yaml = yaml.load(template)

    result_properties = {}

    for call in template_yaml['api_calls']:
        call_with_request_props = request_props.copy()

        logger.debug('call: \n {}'.format(call))

        # enrich params with items stored in runtime props by prev calls
        params.update(result_properties)

        template_engine = Template(str(call))
        rendered_call = template_engine.render(params)
        call = ast.literal_eval(rendered_call)  #unicode to dict

        logger.debug('rendered call: \n {}'.format(call))

        call_with_request_props.update(call)

        logger.info(
            'call_with_request_props: \n {}'.format(call_with_request_props))
        response = _send_request(call_with_request_props)
 #       _process_response(response, call, result_properties)
    return result_properties


def _send_request(call):
    logger.info(
        '_send_request request_props:{}'.format(call))
    host = call['host']
    username = call.get('username')
    password = call.get('password')
    use_ssl = call.get('use_ssl', False)
    verify_ssl = call.get('verify_ssl', False)

    url = call.get('path')
    method = call.get('method')
    data = call.get('data', {})

    with FortiManager(host,
                      username,
                      password,
                      debug=False,
                      use_ssl=use_ssl,
                      verify_ssl=verify_ssl,
                      disable_request_warnings=True) as fmg_instance:
        if method == "GET":
            response = fmg_instance.get(url)
            logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
            _check_response_status_code(response, call)
            return response
        # if method == "ADD":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response
        # if method == "UPDATE":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response
        # if method == "SET":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response
        # if method == "DELETE":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response
        # if method == "REPLACE":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response
        # if method == "CLONE":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response
        # if method == "EXECUTE":
        #     response = fmg_instance.add(url, **data)
        #     logger.debug('---> Method: {} \n response: \n {}'.format(method, response))
        #     _check_response_status_code(response, call)
        #     return response


def _check_response_status_code(response, call):
    response_code = response[0]
    response_error_message = response[1]
    nonrecoverable_codes = call.get('nonrecoverable_codes', [])
    recoverable_codes = call.get('recoverable_codes', [])

    logger.debug('RESPCODE: %s' % type(response_code))
    logger.debug('RECCODE: %s' % type(recoverable_codes[0]))
    logger.debug('RESPCODE == RECCODE: %s' % response_code == recoverable_codes[0])

    if response_code == 1:
        logger.debug('--???->response code: \n {}'.format(response_code))
        raise NonRecoverableResponseException(response_error_message)

    if response_code in nonrecoverable_codes:
        logger.debug('--!!!->response code: \n {}'.format(response_code))
        raise NonRecoverableResponseException('nonrecoverable_code: {}'.format(response_code))

    if response_code in recoverable_codes:
        logger.debug('--xxx-->response_code: \n {}'.format(response_code))
        raise RecoverableResponseException('recoverable_code: {}'.format(response_code))
