#!/bin/bash
cfy blueprint upload -b dg-fortimanager ./devicegroup-blueprint.yaml
cfy deployment create --skip-plugins-validation dg-fortimanager -b dg-fortimanager
cfy -vv executions start -d dg-fortimanager install
