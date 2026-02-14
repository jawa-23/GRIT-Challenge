
from sklearn.metrics import mean_absolute_error

def MAE(y_true, y_pred):
    return float(mean_absolute_error(y_true, y_pred))
