#!/bin/bash
cfy blueprint upload -b fortimanager ./blueprint.yaml
cfy deployment create --skip-plugins-validation fortimanager -b fortimanager
cfy -vv executions start -d fortimanager install
