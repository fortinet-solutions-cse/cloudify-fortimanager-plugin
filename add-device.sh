#!/bin/bash
cfy blueprint upload -b device-fortimanager ./fortigate-adddel-blueprint.yaml
cfy deployment create --skip-plugins-validation device-fortimanager -b device-fortimanager
cfy -vv executions start -d device-fortimanager install
