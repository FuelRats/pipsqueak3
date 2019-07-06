#!/usr/bin/env bash
source /mechasqueak/.teamcity_tools/shared_lib.sh

function run_list_files() {
  echo "##teamcity[blockOpened name='Directory listing']"
  ls -a
  echo "##teamcity[blockClosed name='Directory listing']"
}

function get_pylint_count() {
  local output="$1"  # String containing Pylint's output
  local type="$2"    # The Pylint message type to search for. (e.g. "fatal", "error", etc.)
  local out_line
  # Single out the line from pylint's "Messages by category" section
  # for the message type given.
  out_line=$(echo "${output}" | grep -e "^|${type}")
  if [[ -z "${out_line}" ]]; then
    # If we can't find a matching line, simply return a count of 0.
    echo "0"
  else
    # Split the line we found into an array, and return the message count.
    # Example value for `out_line`:
    #   |convention |6      |6        |=          |
    local IFS='| '
    local result_array
    read -r -a result_array <<< "${out_line}"
    echo "${result_array[2]}"
  fi
  return 0
}

function run_pylint() {
  local output
  output=$(pylint src)
  local pylint_exit=$?  # Save pylint's exit code while we parse its output.
  echo "##teamcity[blockOpened name='Pylint']"
  echo "${output}"  # Add pylint's output to the build log so we can review it.
  echo "##teamcity[blockClosed name='Pylint']"
  local c_fatal; local c_error; local c_warning; local c_refactor; local c_convention;
  c_fatal=$(get_pylint_count "${output}" "fatal")
  c_error=$(get_pylint_count "${output}" "error")
  c_warning=$(get_pylint_count "${output}" "warning")
  c_refactor=$(get_pylint_count "${output}" "refactor")
  c_convention=$(get_pylint_count "${output}" "convention")
  # Run the exit code through pylint-exit to see if we should consider this fatal.
  if ! python pylint-exit "${pylint_exit}"; then
    # If so, output an error code for TeamCity including the message counts, and exit.
    local counts="${c_fatal}F ${c_error}E ${c_warning}W ${c_refactor}R ${c_convention}C"
    echo "##teamcity[buildProblem description='Pylint failed! (${counts})' identity='pylint']"
    return 1
  fi
  return 0
}

function run_pycodestyle() {
  echo "##teamcity[blockOpened name='Pycodestyle']"
  pycodestyle src
  echo "##teamcity[blockClosed name='Pycodestyle']"
  return $?
}

function main() {
  run_list_files
  check_cwd
  run_pylint || exit 1
  run_pycodestyle || exit 1
  echo "done!"
}

main "$@"
echo
exit 0
