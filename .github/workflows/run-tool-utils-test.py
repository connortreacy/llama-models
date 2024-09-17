name: "[ARC][CPU]  Run Tool Utils Tests"
on:

  # TODO: Add later when all tests are accounted for.
  #
  #pull_request:
  #  branches:
  #    - 'main'
  #  paths:
  #    - 'models/llama3/api/*.py'
  #

  push:
    branches:
      - "ci_cd_testing"
  workflow_dispatch:
    inputs:
      runner:
        description: 'GHA Runner Scale Set label to run workflow on.'
        required: true
        default: llama-models-gha-runnes-gpu

      debug:
        description: 'Run debugging steps?'
        required: false
        default: "true"

      sleep_time:
        description: '[DEBUG] sleep time for debugging'
        required: true
        default: "60"

      branch:
        description: "Branch parameter to control which branch to checkout"
        required: true
        default: "main"

jobs:
  execute_workflow:
    name: Execute workload on Self-Hosted CPU k8s runner
    defaults:
      run:
        shell: bash # default shell to run all steps for a given job.
    runs-on: ${{ github.event.inputs.runner != '' && github.event.inputs.runner || 'llama-models-gha-runnes-gpu' }}
    steps:
      - name: "[DEBUG] Get runner container OS information"
        id: os_info
        if: ${{ github.event.inputs.debug == 'true' }}
        run: |
            cat /etc/os-release

      - name: "Checkout 'meta-llama/llama-models' repository"
        id: checkout
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.branch }}

      - name: "[DEBUG] Content of the repository after checkout"
        id: content_after_checkout
        if: ${{ github.event.inputs.debug == 'true' }}
        run: |
            ls -la ${GITHUB_WORKSPACE}

      - name: "Forced sleep_600"
        id: forced_sleep_600
        run: |
            sleep 600

      # Place sleep step before the test execution to "exec" into the test k8s POD and run tests manually to identify what dependencies are being used.
      - name: "[DEBUG] sleep"
        id: sleep
        if: ${{ github.event.inputs.debug == 'true' && github.event.inputs.sleep_time != '' }}
        run: |
            sleep ${{ inputs.sleep_time }}

      - name: "Installing 'apt' required packages"
        id: apt_install
        run: |
          sudo apt update -y
          sudo apt upgrade -y
          sudo apt install python3-pip -y

      - name: "Installing 'llama-models' dependencies"
        id: pip_install
        run: |
          echo "[STEP] Installing 'llama-models' models"
          pip install -U pip setuptools
          pip install -r requirements.txt

      - name: Run tests
        id: run_tests
        run: |
          echo "Running tests on Self-Hosted k8s ARC Runner"
          cd $GITHUB_WORKSPACE && python3 -m unittest models/llama3/api/tests_tool_utils.py

      - name: Publish Test Summary
        id: test_summary
        uses: test-summary/action@v2
        with:
          paths: "**/*.xml"
        if: always()