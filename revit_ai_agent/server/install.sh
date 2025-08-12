#!/usr/bin/env bash
# Bootstrap script for Ubuntu deployment (Prompt 1 scaffold)
# TODO: Enhance error handling, idempotency, and environment validation.

set -euo pipefail

sudo apt update && sudo apt install -y python3.11 python3.11-venv git
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ansible-playbook ansible/playbook.yml -i localhost,
