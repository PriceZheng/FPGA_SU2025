import os
import subprocess
import time
from os import path
from utility import run_HLS_synthesis, parse_xml_into_graph  # Adjust as needed
import shutil

### === Configuration === ###
top_func_name = "fn1"          # Change this to your top-level function
case_name = "dfg_0"              # Case name without extension
directory = "./"               # Path to your working directory

### === Step 1: Run HLS Synthesis === ###
print("[*] Running Vitis HLS synthesis...")
status = run_HLS_synthesis(top_func_name, directory, case_name, impl=True)
if status != 0:
    print("[*] HLS synthesis or export failed.")
    exit(1)

### === Step 2: Parse XML and Generate Graph === ###
print("[*] Parsing .adb XML and building graphs...")
parse_xml_into_graph(directory)

### === Step 3: Generate Bitstream via Vivado === ###
###add_files -fileset constrs_1 my_constraints.xdc - add this if want to add constraint file
def run_vivado_bitgen():
    print("[*] Writing Vivado TCL script for bitstream generation...")
    tcl_script = f"""
create_project my_vivado_proj ./vivado_proj -part xc7a100t-2ftg256

add_files ./project_tmp/solution_tmp/impl/ip
update_ip_catalog
ipx::open_core ./project_tmp/solution_tmp/impl/ip/{top_func_name}_v1_0/{top_func_name}_v1_0.xci
ipx::upgrade_core
ipx::close_core

create_bd_design design_1
make_wrapper -files [get_files design_1.bd] -top
add_files -norecurse ./vivado_proj/design_1/hdl/design_1_wrapper.v
update_compile_order -fileset sources_1

launch_runs synth_1 -jobs 4
wait_on_run synth_1

launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

write_bitstream -force ./vivado_proj/final_output.bit
exit
    """

    with open("generate_bitstream.tcl", "w") as f:
        f.write(tcl_script)

    print("[*] Launching Vivado in batch mode...")

    project_path = os.path.join(directory, 'project_tmp')
    if os.path.exists(project_path):
        shutil.rmtree(project_path)

    print("[*] Bitstream generated at ./vivado_proj/final_output.bit")

run_vivado_bitgen()
print("[*] Full flow complete!")
