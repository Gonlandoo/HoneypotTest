from numpy import long
from z3 import *
from z3.z3util import get_vars

import global_params
from utils import isReal, isSymbolic, simplify
from vargenerator import Generator


def set_cur_file(c_file):
    global cur_file
    cur_file = c_file
def init_analysis():
    analysis = {
        "gas": 0,
        "gas_mem": 0,
        "money_flow": [("Is", "Ia", "Iv")],  # (source, destination, amount)
        "sload": [],
        "sstore": {},
        "reentrancy_bug":[],
        "money_concurrency_bug": [],
        "time_dependency_bug": {}
    }
    return analysis
def update_analysis(analysis, opcode, stack, mem, global_state, path_conditions_and_vars, solver):
    # gas_increment, gas_memory = calculate_gas(opcode, stack, mem, global_state, analysis, solver)
    # analysis["gas"] += gas_increment
    # analysis["gas_mem"] = gas_memory

    if opcode == "CALL":
        recipient = stack[1]
        transfer_amount = stack[2]
        if isReal(transfer_amount) and transfer_amount == 0:
            return
        if isSymbolic(recipient):
            recipient = simplify(recipient)

        # reentrancy_result = check_reentrancy_bug(path_conditions_and_vars, stack, global_state)

        # analysis["reentrancy_bug"].append(reentrancy_result)

        # analysis["money_concurrency_bug"].append(global_state["pc"])
        # analysis["money_flow"].append( ("Ia", str(recipient), str(transfer_amount)))
    elif opcode == "SUICIDE":
        recipient = stack[0]
        if not isinstance(recipient, (int, long)):
            recipient = simplify(recipient)
        analysis["money_flow"].append(("Ia", str(recipient), "all_remaining"))
# Check if it is possible to execute a path after a previous path
# Previous path has prev_pc (previous path condition) and set global state variables as in gstate (only storage values)
# Current path has curr_pc
def is_feasible(prev_pc, gstate, curr_pc):
    vars_mapping = {}
    new_pc = list(curr_pc)
    for expr in new_pc:
        list_vars = get_vars(expr)
        for var in list_vars:
            vars_mapping[var.decl().name()] = var
    new_pc += prev_pc
    gen = Generator()
    for storage_address in gstate:
        var = gen.gen_owner_store_var(storage_address)
        if var in vars_mapping:
            new_pc.append(vars_mapping[var] == gstate[storage_address])
    solver = Solver()
    solver.set("timeout", global_params.TIMEOUT)
    solver.add(new_pc)
    if solver.check() == unsat:
        return False
    else:
        return True