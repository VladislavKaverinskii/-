import data_loader
import rec_press
import carbides
import thermodytamic
import json
import copy
import random

from base import *


def load_fit_data():
    fit_data = json.loads(open("fit_data.json").read())
    fit_parameters = json.loads(open("fit_parameters.json").read())
    fit_task = json.loads(open("fit_task.json").read())
    return fit_data, fit_parameters, fit_task


def to_initial(solver, fit_parameters, fit_task, initial=True):
    levels = dict()

    for key_1 in solver.parameters:
        data_1 = solver.parameters.get(key_1)
        if isinstance(data_1, dict):
            for key_2 in data_1:
                data_2 = data_1.get(key_2)
                if isinstance(data_2, dict):
                    for key_3 in data_2:
                        data_3 = data_2.get(key_3)
                        if isinstance(data_3, float) or isinstance(data_3, int):

                            for key_1_2 in fit_parameters:
                                if key_1_2 == key_1:
                                    data_1_2 = fit_parameters.get(key_1)
                                    if isinstance(data_1_2, dict):
                                        for key_2_2 in data_1_2:
                                            if key_2_2 == key_2:
                                                data_2_2 = data_1_2.get(key_2)
                                                if isinstance(data_2_2, dict):
                                                    for key_3_2 in data_2_2:
                                                        if key_3_2 == key_3:
                                                            data_3_2 = data_2_2.get(key_3)
                                                            if isinstance(data_3_2, list) and len(data_3_2) == 3:
                                                                if initial:
                                                                    work_value = data_3_2[2]
                                                                else:
                                                                    work_value = data_2[key_3]
                                                                data_2[key_3] = work_value
                                                                min_val = work_value - (work_value - data_3_2[0])*fit_task["d_fit"]
                                                                max_val = work_value + (data_3_2[1] - work_value) * \
                                                                          fit_task["d_fit"]
                                                                levels[key_1 + "|" + key_2 + "|" + key_3] = [min_val, work_value, max_val]


                elif isinstance(data_2, float) or isinstance(data_2, int):
                    for key_1_2 in fit_parameters:
                        if key_1_2 == key_1:
                            data_1_2 = fit_parameters.get(key_1)
                            if isinstance(data_1_2, dict):
                                for key_2_2 in data_1_2:
                                    if key_2_2 == key_2:
                                        data_2_2 = data_1_2.get(key_2)
                                        if isinstance(data_2_2, list):
                                            if initial:
                                                work_value = data_2_2[2]
                                            else:
                                                work_value = data_1[key_2]
                                            data_1[key_2] = work_value
                                            min_val = work_value - (work_value - data_2_2[0]) * fit_task["d_fit"]
                                            max_val = work_value + (data_2_2[1] - work_value) * fit_task["d_fit"]
                                            levels[key_1 + "|" + key_2] = [min_val, work_value, max_val]
    return levels


def get_mask(current_levels):
    N_total = 3 ** len(current_levels)
    mask = list()
    for i in range(N_total):
        current_level = dict()
        for j, key in enumerate(current_levels):
            current_level[key] = current_levels[key][(i // 3 ** j) % 3]

        if current_level not in mask:
            mask.append(current_level)
        else:
            print("!!!!!!!!!!!!!!!!!!")
    return mask


def get_solvers_set(mask, solver):
    solvers = list()
    for row in mask:
        current_solver_obj = copy.deepcopy(solver)
        for mask_key in row:
            mask_keys = mask_key.split("|")
            for key_n in range(len(mask_keys)):
                key = mask_keys[key_n]
                for solver_key_1 in solver.parameters:
                    if solver_key_1 == key:
                        key_n += 1
                        key_2 = mask_keys[key_n]
                        if isinstance(solver.parameters.get(key), dict):
                            for solver_key_2 in solver.parameters[key]:
                                if solver_key_2 == key_2:
                                    if isinstance(solver.parameters.get(key).get(key_2), dict):
                                        key_n += 1
                                        key_3 = mask_keys[key_n]
                                        for solver_key_3 in solver.parameters[key][key_2]:
                                            if solver_key_3 == key_3:
                                                if (isinstance(solver.parameters.get(key).get(key_2).get(key_3), float)
                                                    or isisntance(solver.parameters.get(key).get(key_2).get(key_2),
                                                                  int)):
                                                    current_solver_obj.parameters[key][key_2][key_3] = row[mask_key]
                                    elif (isinstance(solver.parameters.get(key).get(key_2), float)
                                            or isisntance(solver.parameters.get(key).get(key_2), int)):
                                        current_solver_obj.parameters[key][key_2] = row[mask_key]

        solvers.append(current_solver_obj)
    return solvers


def perform():
    solver = MainSolver()
    solver.read_data()
    fit_data, fit_parameters, fit_task = load_fit_data()
    current_levels = to_initial(solver, fit_parameters, fit_task)

    random.seed()

    best_fit = 1E100
    counter = 0
    while (best_fit**0.5)*100 >= fit_task["total_tolerance"] and counter < fit_task["max_iteration"]:
        counter += 1
        print("iteration ", counter)
        print("*************************")
        mask = get_mask(current_levels)
        k = int(fit_task["random_multiplicity"] * len(mask))
        if k < 1:
            k = 1
        mask_2 = random.sample(mask, k)
        solvers = get_solvers_set(mask_2, solver)

        print("len(solvers)", len(solvers))
        best_option = solvers[0]


        for solver_obj in solvers:
            summ_difference = 0.0
            N = 0
            for data_block in fit_data:
                solver_obj.task.base = data_block["initial"].get("base")
                solver_obj.init_t = data_block["initial"].get("init_t")
                solver_obj.D_0 = data_block["initial"].get("D_0")
                solver_obj.e_deform = data_block["initial"].get("e_deform")
                solver_obj.v_deform = data_block["initial"].get("v_deform")
                solver_obj.lattice_type = data_block["initial"].get("lattice_type")
                #print(solver_obj.parameters)
                current_recrystalization_result = solver_obj.recrystalization_simulation()
                # print("current_recrystalization_result")
                # print(current_recrystalization_result)

                current_fit_list = data_block.get("fit")
                if isinstance(current_fit_list, dict):
                    for fit_parameter_key in current_fit_list:
                        if fit_parameter_key in current_recrystalization_result:
                            for position in current_recrystalization_result[fit_parameter_key]:
                                for fit_position in current_fit_list[fit_parameter_key]:
                                    if abs(fit_position[0] - position) < solver_obj.task.d_tau / 2.0:
                                        fit_position_value = fit_position[1] / 100.0
                                        # print(fit_position[0], position)
                                        # print(current_recrystalization_result[fit_parameter_key][position])
                                        # print(fit_position_value)
                                        summ_difference += (2*(current_recrystalization_result[fit_parameter_key][position] - fit_position_value)/(1E-20 + current_recrystalization_result[fit_parameter_key][position] + fit_position_value))**2
                                        N += 1
                                        # print((2*(current_recrystalization_result[fit_parameter_key][position] - fit_position_value)/(1E-20 + current_recrystalization_result[fit_parameter_key][position] + fit_position_value))**2)
            res_difference = summ_difference / float(N)
            if res_difference < best_fit:
                best_fit = res_difference
                best_option = solver_obj
                print(best_fit)
                print(best_option.parameters)
                print("------------------------")

        current_levels = to_initial(best_option, fit_parameters, fit_task, initial=False)








if __name__ == "__main__":
    perform()




