import numpy as np
import tensorflow as tf

import util.util_consistency_constraints as ucc
import util.util_ml_model as umm

""" Script for training the ML model on pre-processed data.

Description:
    This module contains the settings and main loop for training the ML model

-*- coding: utf-8 -*-

Legal:
    (C) Copyright IBM 2018.

    This code is licensed under the Apache License, Version 2.0. You may
    obtain a copy of this license in the LICENSE.txt file in the root 
    directory of this source tree or at 
    http://www.apache.org/licenses/LICENSE-2.0.

    Any modifications or derivative works of this code must retain this
    copyright notice, and modified files need to carry a notice 
    indicating that they have been altered from the originals.

    IBM-Review-Requirement: Art30.3
    Please note that the following code was developed for the project 
    VaVeL at IBM Research -- Ireland, funded by the European Union under 
    the Horizon 2020 Program.
    The project started on December 1st, 2015 and was completed by 
    December 1st, 2018. Thus, in accordance with Article 30.3 of the 
    Multi-Beneficiary General Model Grant Agreement of the Program, 
    there are certain limitations in force  up to December 1st, 2022. 
    For further details please contact Jakub Marecek 
    (jakub.marecek@ie.ibm.com) or Gal Weiss (wgal@ie.ibm.com).

If you use the code, please cite our paper:
https://arxiv.org/abs/1810.09425

Authors: 
    Philipp Hähnel <phahnel@hsph.harvard.edu>

Last updated:
    2019 - 08 - 01

"""

tf.logging.set_verbosity(tf.logging.INFO)


def get_parameters():
    """
    use 'mesh_size': 2 for synthetic example
    use 'mesh_size': 12 for Dublin example
    select 'tiles': [i, j, k] for the tiles i, j, k that are part of the run
    The synthetic example has the two tiles 6 and 7.
    :return:
    """
    param = {  # data parameters
        'case': 'Demo',  # retrieves utilities based on this tag
        'mesh_size': 2,  # tag which identifies pre-processed data
        'tiles': [6, 7],  # list of id's of each of the sub-domain
        # model hyper-parameters
        'num_iterations': 20,
        'num_hidden_layers': 4,
        'num_nodes': 42,
        'num_epochs': 200,
        'batch_size': 128,
        'l2_reg_coefficient': 0.0001,  # weights are regularized with l2 norm
        'starter_learning_rate': 0.001,
        'decay_factor': 0.96,  # exponential decay
        'train_to_test_split': 0.9,  # train_% + test_% = 1
        'add_previous_labels_to_input': False,
        # ToDo: allow True in update of consistency constraint data
        # consistency constraints
        'use_consistency_constraints': False,
        'cc_reg_coefficient': 1,  # lambda
        'kappa': 0.5,
        'epsilon': 0.1,
        'cc_update_version': 'version 3',
        # check util.util_consistency_constraints
        # saving of output
        'do_save_benchmark': False,
        'do_save_cc': False,
        'do_save_model': False,
        'do_save_estimates': False,
        'iterations_to_save_estimates': [0] + list(range(4, 10000, 5)),
        'do_print_status': True,
        # for reproducibility
        'random_seed': None
        # None or (int) < 2147483648. If None, it's taken at random
    }
    return param


def main():
    param = get_parameters()
    if param['random_seed'] is None:
        param['random_seed'] = np.random.randint(2147483647)
    np.random.seed(param['random_seed'])

    if param['do_print_status']:
        print(f'Using pre-processed data for {param["case"]} '
              # f'with tag {param["tag"]}.'
              )
        print(f'Hidden layers: {param["num_hidden_layers"]}\t '
              f'nodes: {param["num_nodes"]}\t')
        print(f'Lambda: {param["cc_reg_coefficient"]}\t '
              f'kappa: {param["kappa"]}\t '
              f'epsilon: {param["epsilon"]}\n')
        print('Loading data ...')
    collections = umm.get_collections()
    mesh = umm.get_mesh(collections['util'], **param)
    data = umm.get_data(collections['data'], mesh, **param)
    if param['do_print_status']:
        print('Data loaded successfully.')

    for iteration in range(param['num_iterations']):
        mlp_times = umm.run_recursion_cycle(data, mesh, iteration,
                                            collections['pred'], **param)
        if param['use_consistency_constraints']:
            ucc.update_consistency_constraints(data, mesh, iteration, **param)
        if param['do_print_status']:
            print(f'Average MLP run time for all data of one tile: '
                  f'{np.average(mlp_times):.6f}s')
            print(f'Standard Deviation: {np.std(mlp_times):.6f}s')
            print('')

    return None


if __name__ == '__main__':
    main()
