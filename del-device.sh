#!/bin/bash
cfy -vv executions start -d device-fortimanager uninstall
cfy deployments delete device-fortimanager
cfy blueprints delete device-fortimanager
