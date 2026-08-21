from app.data_generator import generate
from app.features import add,FEATURES
from app.ml import train,predict
def test_features():
    assert all(x in add(generate("pump",60)).columns for x in FEATURES)
def test_train():
    m=train();assert m["samples"]>0 and 0<=m["roc_auc"]<=1
def test_predict():
    train();a,f=predict(generate("compressor",60,"compressor_overheat"));assert 0<=a<=1 and 0<=f<=1
