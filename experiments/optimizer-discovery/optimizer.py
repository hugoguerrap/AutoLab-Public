"""
Optimizer Discovery — Editable Optimizer File
===============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.
"""

import torch
import math

LEARNING_RATE = 0.002

class CustomOptimizer(torch.optim.Optimizer):
    """
    Experiment 3: Dual-Momentum Adam + GC + Warmup + Cosine + Grad Clip.

    Novel: Two momentum tracks at different timescales.
    - Fast momentum (beta1=0.9): captures recent gradient direction
    - Slow momentum (beta3=0.99): provides long-range stability
    - Blended update: weighted combination of both
    - Plus gradient centralization, warmup, cosine decay, gradient clipping
    """

    def __init__(self, params, lr=0.002, beta1=0.9, beta2=0.999, beta3=0.99,
                 eps=1e-8, weight_decay=0.01, warmup_steps=100,
                 total_steps=4700, max_grad_norm=1.0, blend=0.7):
        defaults = dict(lr=lr, beta1=beta1, beta2=beta2, beta3=beta3,
                        eps=eps, weight_decay=weight_decay,
                        warmup_steps=warmup_steps, total_steps=total_steps,
                        max_grad_norm=max_grad_norm, blend=blend)
        super().__init__(params, defaults)

    def _get_lr_scale(self, step, warmup_steps, total_steps):
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

        # Global gradient clipping across all params
        all_params = []
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is not None:
                    all_params.append(p)

        if all_params:
            torch.nn.utils.clip_grad_norm_(all_params, self.param_groups[0]["max_grad_norm"])

        for group in self.param_groups:
            base_lr = group["lr"]
            beta1 = group["beta1"]
            beta2 = group["beta2"]
            beta3 = group["beta3"]
            eps = group["eps"]
            wd = group["weight_decay"]
            warmup = group["warmup_steps"]
            total = group["total_steps"]
            blend = group["blend"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad

                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["m_fast"] = torch.zeros_like(p.data)   # fast momentum
                    state["m_slow"] = torch.zeros_like(p.data)   # slow momentum
                    state["v"] = torch.zeros_like(p.data)         # second moment

                state["step"] += 1
                t = state["step"]

                lr = base_lr * self._get_lr_scale(t, warmup, total)

                # Gradient centralization for weight matrices
                if grad.dim() > 1:
                    grad = grad - grad.mean(dim=tuple(range(1, grad.dim())), keepdim=True)

                # Decoupled weight decay
                if wd > 0:
                    p.data.mul_(1 - lr * wd)

                # Dual momentum
                m_fast = state["m_fast"]
                m_slow = state["m_slow"]
                v = state["v"]

                m_fast.mul_(beta1).add_(grad, alpha=1 - beta1)
                m_slow.mul_(beta3).add_(grad, alpha=1 - beta3)
                v.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                # Bias correction
                m_fast_hat = m_fast / (1 - beta1 ** t)
                m_slow_hat = m_slow / (1 - beta3 ** t)
                v_hat = v / (1 - beta2 ** t)

                # Blend fast and slow momentum
                m_blended = blend * m_fast_hat + (1 - blend) * m_slow_hat

                # Update
                p.data.addcdiv_(m_blended, v_hat.sqrt().add_(eps), value=-lr)

        return loss

STRATEGY_NOTES = """
Exp 1: Adam reimplementation = 0.9217
Exp 2: Adam+GC+warmup+cosine = 0.9865 (BEATS AdamW!)
Exp 3: Dual momentum (fast+slow blend) + grad clip + all exp2 features.
  - Fast momentum (beta1=0.9): responsive to recent gradients
  - Slow momentum (beta3=0.99): long-range stability
  - Blend=0.7: 70% fast, 30% slow
  - Gradient clipping: prevents instability
"""
