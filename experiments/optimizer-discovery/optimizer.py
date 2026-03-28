"""
Optimizer Discovery — Editable Optimizer File
===============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.
"""

import torch
import math

LEARNING_RATE = 0.002  # Higher initial LR with warmup + decay

class CustomOptimizer(torch.optim.Optimizer):
    """
    Experiment 2: Adam + Gradient Centralization + LR Warmup + Cosine Decay.

    Novel additions over standard Adam:
    1. Gradient centralization: subtract mean of gradient (for non-bias params)
    2. Warmup: linearly increase LR for first 100 steps
    3. Cosine LR decay: smoothly reduce LR over training
    """

    def __init__(self, params, lr=0.002, beta1=0.9, beta2=0.999, eps=1e-8,
                 weight_decay=0.01, warmup_steps=100, total_steps=4700):
        defaults = dict(lr=lr, beta1=beta1, beta2=beta2, eps=eps,
                        weight_decay=weight_decay, warmup_steps=warmup_steps,
                        total_steps=total_steps)
        super().__init__(params, defaults)

    def _get_lr_scale(self, step, warmup_steps, total_steps):
        """Warmup + cosine decay schedule."""
        if step < warmup_steps:
            return step / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            base_lr = group["lr"]
            beta1 = group["beta1"]
            beta2 = group["beta2"]
            eps = group["eps"]
            wd = group["weight_decay"]
            warmup = group["warmup_steps"]
            total = group["total_steps"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad

                # Initialize state
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["m"] = torch.zeros_like(p.data)
                    state["v"] = torch.zeros_like(p.data)

                state["step"] += 1
                t = state["step"]
                m, v = state["m"], state["v"]

                # Learning rate with warmup + cosine decay
                lr = base_lr * self._get_lr_scale(t, warmup, total)

                # Gradient centralization: subtract mean for weight matrices
                if grad.dim() > 1:
                    grad = grad - grad.mean(dim=tuple(range(1, grad.dim())), keepdim=True)

                # Decoupled weight decay
                if wd > 0:
                    p.data.mul_(1 - lr * wd)

                # Update moments
                m.mul_(beta1).add_(grad, alpha=1 - beta1)
                v.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                # Bias correction
                m_hat = m / (1 - beta1 ** t)
                v_hat = v / (1 - beta2 ** t)

                # Update parameters
                p.data.addcdiv_(m_hat, v_hat.sqrt().add_(eps), value=-lr)

        return loss

STRATEGY_NOTES = """
Exp 1: Adam reimplementation = 0.9217 (stability gap vs AdamW 0.9640)
Exp 2: Added gradient centralization + warmup + cosine decay.
  - GC: removes gradient mean for weight matrices (Wang et al. 2020)
  - Warmup: prevents early overshoot
  - Cosine: smooth LR reduction for better convergence
  - Higher initial LR (0.002) to compensate for decay
"""
