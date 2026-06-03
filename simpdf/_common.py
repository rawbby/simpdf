def _apply_constraints(obj, sym_params, sym_defaults, relations):
    state = {k: v for k, v in sym_params if v is not None}

    def propagate():
        changed = True
        while changed:
            changed = False
            for out_v, in_v, func in relations:
                args = [state.get(v) for v in in_v]
                if all(a is not None for a in args):
                    res = func(*args)
                    if res is not None:
                        if state.get(out_v) is not None:
                            if abs(state[out_v] - res) > 1e-6:
                                raise ValueError("Contradictory typography constraints provided")
                        else:
                            state[out_v] = res
                            changed = True

    propagate()
    for k, v in sym_defaults:
        if state.get(k) is None:
            state[k] = v
            propagate()

    for k, _ in sym_defaults:
        if state.get(k) is None:
            raise ValueError("Contradictory typography constraints after applying defaults")

    for k, _ in sym_defaults:
        setattr(obj, k, float(state[k]))
