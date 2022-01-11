from copy import deepcopy
import enum
import ConfigSpace as CS
import ConfigSpace.hyperparameters as CSH
import pandas as pd
import numpy as np
import random

from custom_anchor import TabularAnchor
from lucb import get_best_candidate

class Explainer:

    def __init__(self, X : pd.DataFrame) -> None:
        self.X = X
        self.features = list(X.columns)
        self.quantiles = {}
        # { feature : [bound1, bound2, bound3] }
        for f in self.features:
            self.quantiles[f] = np.quantile(X[f], np.arange(0,1, 0.05))# [0.25, 0.5, 0.75])
        
        self.feature2index = {f : self.features.index(f) for f in self.features}
        self.cs = get_configspace_for_dataset(X)
        

    def explain_bottom_up(self, instance, model, tau=0.95):
        # initialise empty Anchor
        anchor = TabularAnchor(self.cs)
        # get quantiles of instance
        rules = generate_rules_for_instance(self.quantiles, instance, self.feature2index)
        random.shuffle(rules)
        while True:
            # add unused rules to current anchor
            candidates = generate_candidates(anchor, rules)
            if candidates == []:
                exit("No anchors found, ¯\_(ツ)_/¯")
            # all this LUCB?
            anchor = get_best_candidate(candidates, instance, model)
            print("Current best:", (anchor.mean), anchor.rules)
            import time
            time.sleep(2)
            if anchor.mean >= tau:
                break
            # else:
            #     while anchor.lb <= tau and tau <= anchor.up:
            #         pass
            #         # sample instance
            #         # predict instance
            #         # update candidates' precision and bounds
                # if anchor.lb > tau:
                #     break
        return anchor

    def explain_beam_search(self):
        """
        A* = []
        A_0 = []
        while True:
            candidates = [A + a_i for a_i in features if cov(A + a_i) > cov(A)]
            A_t = get_b_best_candidates(candidates)
            if not A_t:
                break
            for A in [A for A in A_t if lb(A) > tau]:
                if cov(A) > cov(A*):
                    A* = A
        return A*
        """
        raise NotImplementedError()

def get_configspace_for_dataset(X : pd.DataFrame):
    cs = CS.ConfigurationSpace()
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#basics-dtypes
    for f in X.columns:
        if X[f].dtype in ("category", "string", "object", "boolean"):
            hp = CSH.CategoricalHyperparameter(f, choices=X[f].unique())
        elif "Int" in str(X[f].dtype):
            hp = CSH.UniformIntegerHyperparameter(f, lower=X[f].min(), upper=X[f].max(), log=False)
        elif "float" in str(X[f].dtype):
            hp = CSH.UniformFloatHyperparameter(f, lower=X[f].min(), upper=X[f].max(), log=False)

        cs.add_hyperparameter(hp)
    return cs

def generate_rules_for_instance(quantiles, instance, feature2index):
    if len(instance.shape) >= 2:
        instance = instance.squeeze(0)
    rules = []
    for f, f_quantile in quantiles.items():
        f_idx = feature2index[f]
        for i, bound in enumerate(f_quantile):
            if i == 0:
                if instance[f_idx] <= bound:
                    rules.append((f, "<=", bound))
                    break

            if i == len(f_quantile) - 1:
                if instance[f_idx] >= bound:
                    rules.append((f, ">=", bound))
                    break
            
            if instance[f_idx] > bound and instance[f_idx] < f_quantile[i+1]:
                rules.append((f, ">=", bound, "<=", f_quantile[i+1]))
                break

    return rules

def generate_candidates(anchor, rules):
    print("CALL GENERATE CANDIDATES")
    anchors_copy = [deepcopy(anchor) for _ in range(len(rules))]
    new_anchors=  []
    for i, rule in enumerate(rules):
        # This might need to check whether combined rules still make sense
        if rule[0] in anchor.get_current_features():
            # compare old feature, operator and value
            n_f, n_o, n_v = new_rule
            for old_rule in anchor.rules:
                if old_rule[0] == n_f:
                    o_f, o_o, o_v = old_rule

            # l < x < u OK
            # u > x > l OK
            continue
        new = anchors_copy[i] 
        new.add_rule(rule)
        new_anchors.append(new)

    return new_anchors

