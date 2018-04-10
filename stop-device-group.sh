#!/bin/bash
cfy executions start -d dg-fortimanager uninstall
cfy deployments delete dg-fortimanager
cfy blueprints delete dg-fortimanager
