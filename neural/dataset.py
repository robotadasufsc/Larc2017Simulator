import cv2
import numpy as np
import os


def load(dataset_dir='./dataset', use_y_as_string=False, verbose=True, test_perc=0):
    '''load all generic data'''
    directory = dataset_dir
    # x = input
    # y = output
    x = {}
    y = {}
    tag_counter = {}
    for root, _, files in os.walk(directory, topdown=False):
        for name in files:
            # dataset's subfolder are tags name
            tag_name = os.path.join(root, name).split('/')[-2]
            if tag_name in tag_counter:
                tag_counter[tag_name] += 1
            else:
                tag_counter[tag_name] = 0
                x[tag_name] = []
                y[tag_name] = []
            X = cv2.imread(os.path.join(root, name), cv2.IMREAD_GRAYSCALE)
            x[tag_name].append(X)
            if use_y_as_string:
                y[tag_name].append(tag_name)
            else:
                y[tag_name].append(len(tag_counter) - 1)

    # Final variables
    x_train = []
    x_test = []
    y_train = []
    y_test = []
    X = []
    Y = []
    if verbose:
        print('Dataset:')
    for i in x.keys():
        n_samples = len(x[i]) - 1
        if test_perc != 0:
            train = x[i][:int(n_samples * test_perc)]
            test = x[i][int(n_samples * test_perc):]
            if verbose:
                print('\t%s (train / test): %d / %d ' %
                      (i, len(train), len(test)))
            x_train.extend(train)
            x_test.extend(test)
            train = y[i][:int(n_samples * test_perc)]
            test = y[i][int(n_samples * test_perc):]
            y_train.extend(train)
            y_test.extend(test)
        else:
            X.extend(x[i])
            Y.extend(y[i])
            if verbose:
                print('\t%s: %d ' % (i, len(x[i])))

    if test_perc != 0:
        return np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test)
    else:
        return np.array(X), np.array(Y)
