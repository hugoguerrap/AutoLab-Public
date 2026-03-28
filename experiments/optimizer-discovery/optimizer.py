"""
Optimizer Discovery — Editable Optimizer File
===============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.

Define your CustomOptimizer class here. It must:
1. Inherit from torch.optim.Optimizer
2. Accept (params, lr) at minimum
3. Implement step() with your novel update rule

Baseline: Plain SGD (simplest possible optimizer).
Your goal: discover an update rule that beats Adam/AdamW.
"""

import torch
import math

# ── Learning Rate ──────────────────────────────────────────────
# You can tune this. Default: 0.001
LEARNING_RATE = 0.001

# ── Custom Optimizer ───────────────────────────────────────────

class CustomOptimizer(torch.optim.Optimizer):
    """
    Baseline: Plain SGD.

    The update rule is simple: param = param - lr * gradient

    YOUR MISSION: Replace this with a novel update rule that
    trains faster and reaches higher accuracy than Adam/AdamW.

    Things you can try:
    - Add momentum (exponential moving average of gradients)
    - Add adaptive learning rates (per-parameter, like Adam)
    - Add second moment tracking (gradient variance)
    - Add weight decay (L2 regularization)
    - Add gradient clipping
    - Add learning rate warmup/scheduling
    - Combine ideas in novel ways
    - Invent entirely new update rules

    State variables you can store in self.state[param]:
    - Momentum buffer
    - Second moment estimate
    - Step count
    - Running statistics
    - Anything else you need
    """

    def __init__(self, params, lr=0.001, **kwargs):
        defaults = dict(lr=lr, **kwargs)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        """Perform a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group["lr"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad

                # ═══════════════════════════════════════════
                # YOUR UPDATE RULE HERE
                # Currently: plain SGD
                # Replace this with your novel algorithm
                # ═══════════════════════════════════════════
                p.data.add_(grad, alpha=-lr)

        return loss


# ── Strategy Notes ─────────────────────────────────────────────
STRATEGY_NOTES = """
Experiment 0 — Baseline: Plain SGD

Known optimizers to study and beat:
1. SGD + Momentum: v = beta*v + grad, param -= lr*v
2. Adam: m = beta1*m + (1-beta1)*g, v = beta2*v + (1-beta2)*g^2,
         param -= lr * m_hat / (sqrt(v_hat) + eps)
3. AdamW: Adam + decoupled weight decay
4. RMSprop: v = alpha*v + (1-alpha)*g^2, param -= lr*g/sqrt(v+eps)
5. Adagrad: accumulate g^2, param -= lr*g/sqrt(acc+eps)

Novel ideas to explore:
- Combine momentum + adaptive LR in new ways
- Use gradient sign (like SignSGD) with magnitude tracking
- Hyperbolic or sigmoid-based learning rate adaptation
- Gradient history compression (beyond simple EMA)
- Per-parameter learning rate based on gradient statistics
- Curvature estimation without full Hessian
- Novel bias correction schemes
- Gradient centralization
- Lookahead-style dual update
"""
