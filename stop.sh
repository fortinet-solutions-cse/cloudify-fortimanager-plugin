#!/bin/bash
cfy executions start -d fortimanager uninstall
cfy deployments delete fortimanager
cfy blueprints delete fortimanager
