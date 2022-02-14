from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
from anchor import anchor_tabular
from explainer import Explainer

if "__main__" == __name__:
    # prepare data
    print("Preparing data...")
    data = pd.read_csv("data/wheat_seeds.csv")
    # y = pd.read_csv("data/german_labels.csv")
    # X_df = data
    # X = data
    i_idx = 111
    X_df = data.drop(columns=["Type"])
    X = data.drop(columns=["Type"]).to_numpy()
    y = data["Type"].to_numpy()
    instance = X[i_idx].reshape(1, -1)
    print(y[155], y[3], y[111])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # prepare model
    print("Preparing classifier...")
    model = RandomForestClassifier(n_estimators=10)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print("Classifier accuracy:", sum(preds == y_test) / len(y_test))


    # get anchor-exp explanation
    # explainer = anchor_tabular.AnchorTabularExplainer(["0", "1", "2"], X_df.columns, X_train)
    # exp = explainer.explain_instance(instance, model.predict, 0.95)
    # conditions = exp.names()
    # precision = round(exp.precision(), 2)
    # coverage = round(exp.coverage(), 2)
    # print(conditions, precision, coverage)

    # get explanation
    exp = Explainer(X_df)
    anchor = exp.explain_bottom_up(instance, model, tau=0.95)
    # print("Precision:", anchor.mean)
    # print("Coverage:", anchor.coverage)
    # print("Sampled:", anchor.n_samples)
    print(anchor.get_explanation())
    anchor = exp.explain_beam_search(instance, model, tau=0.95, B=3)
    # print("Precision:", anchor.mean)
    # print("Coverage:", anchor.coverage)
    # print("Sampled:", anchor.n_samples)
    print(anchor.get_explanation())
    anchor = exp.explain_bayesian_optimiziation(instance, model, evaluations=64, samples_per_iteration=500, tau=0.8)
    print(anchor.get_explanation())
    # print("Precision:", anchor.mean)
    # print("Coverage:", anchor.coverage)
    # print("Sampled:", anchor.n_samples)
    # print("Rules", anchor.rules)

    