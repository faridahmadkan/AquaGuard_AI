def evaluate_detection(y_true, y_pred):
    yt=list(map(bool,y_true)); yp=list(map(bool,y_pred))
    if len(yt)!=len(yp): raise ValueError("Label and prediction lengths must match")
    tp=sum(a and b for a,b in zip(yt,yp))
    fp=sum((not a) and b for a,b in zip(yt,yp))
    fn=sum(a and (not b) for a,b in zip(yt,yp))
    tn=sum((not a) and (not b) for a,b in zip(yt,yp))
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"TP":tp,"FP":fp,"FN":fn,"TN":tn,"Precision":precision,"Recall":recall,"F1":f1}
