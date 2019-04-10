'''
Process the .json file generated by transfer_learning_cnn_cv.py.
It generates:
    1. average training/validating accuracy over the 10 folds when picking
       the epoch with the best MCC.
    2. average training/validating MCC over the 10 folds when picking the epoch
       with the best validation MCC.
    3. the ROC curve of the 10 folds when picking the epoch with the best validation MCC.
    4. the mean ROC curve of the 10 folds.
'''
import numpy as np
from scipy import interp
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import json
import matplotlib.pyplot as plt
import argparse

def getArgs():
    parser = argparse.ArgumentParser('python')
    parser.add_argument('-op',
                        default='cat_vs_dog',
                        required=False,
                        choices = ['cat', 'dog', 'cat_vs_dog'],
                        help='show results of cross validation for cats vs control or dogs vs control')
    return parser.parse_args()

# mean of max of sublists of list
def meanMax(list):
    lenList = len(list)
    listMax = [] # max element of each sub list
    for i in range(lenList):
        listMax.append(max(list[i]))
        listMaxMean = np.mean(listMax)
    return listMaxMean

# plot the roc curves for each fold picking the epoch with best validation MCC
# input is a list containing dictionaries containing fpr, tpr and thresholds of
# each fold. Each dictionary is generated when the validation MCC is best for
# that fold.
# code from:https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc_crossval.html
def rocPlot(list):
    k = len(list) # number of folds
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)
    fig=plt.figure(figsize=(14, 8))
    for i in range(k):
        rocDict = list[i]
        fpr = rocDict['fpr']
        tpr = rocDict['tpr']
        thresholds = rocDict['thresholds']
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        plt.plot(fpr, tpr, lw=1, alpha=0.3,label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

    plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',label='Chance', alpha=.8)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, color='b',
    label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.4,label=r'$\pm$ 1 std. dev.')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic curve')
    plt.legend(loc="lower right")
    plt.show()
#--------------------------end of rocPlot-----------------------------------------

if __name__ == "__main__":
    # get the operation mode: control_vs_heme or control_vs_nucleotide
    args = getArgs()
    op = args.op
    print('post-processing data for '+op)

    # read the corresponding .json file
    with open('./log/'+op+'_cv'+'.json', 'r') as fp:
        loadedList = json.load(fp)

    # unpack
    train_acc_history_list = loadedList[0]
    val_acc_history_list = loadedList[1]
    train_loss_history_list = loadedList[2]
    val_loss_history_list = loadedList[3]
    train_mcc_history_list = loadedList[4]
    val_mcc_history_list = loadedList[5]
    best_mcc_roc_list = loadedList[6]

    print('Average validation accuracy over 5 folds:{:.4f}'.format(meanMax(val_acc_history_list)))
    print('Average validation MCC over 5 folds:{:.4f}'.format(meanMax(val_mcc_history_list)))

    rocPlot(best_mcc_roc_list)