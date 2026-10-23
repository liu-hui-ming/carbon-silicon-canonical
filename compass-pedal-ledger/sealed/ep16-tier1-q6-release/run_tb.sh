#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
iverilog -g2012 -Wall -s tb_q6_t_operator -o sim_q6 tb_q6_t_operator.sv t_operator_q6.sv
vvp sim_q6
rm -f sim_q6
