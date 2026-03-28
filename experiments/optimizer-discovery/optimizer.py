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
    Experiment 8: Dual Momentum + GC + Clip + Cosine + Gradient Noise.

    Novel: Inject decaying Gaussian noise into gradients.
    - Acts as implicit regularization (like dropout for gradients)
    - Noise magnitude decays with 1/sqrt(t) schedule
    - Helps escape sharp minima → flatter loss surface → better generalization
    - Should close the train/val gap and lower val_loss

    Based on: "Adding Gradient Noise Improves Learning" (Neelakantan et al.)
    but combined with our dual momentum framework.
    """

    def __init__(self, params, lr=0.002, beta1=0.9, beta2=0.999, beta3=0.99,
                 eps=1e-8, weight_decay=0.01, warmup_steps=100,
                 total_steps=4700, max_grad_norm=1.0, blend=0.7,
                 noise_scale=0.01):
        defaults = dict(lr=lr, beta1=beta1, beta2=beta2, beta3=beta3,
                        eps=eps, weight_decay=weight_decay,
                        warmup_steps=warmup_steps, total_steps=total_steps,
                        max_grad_norm=max_grad_norm, blend=blend,
                        noise_scale=noise_scale)
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

        all_params = [p for g in self.param_groups for p in g["params"] if p.grad is not None]
        if all_params:
            torch.nn.utils.clip_grad_norm_(all_params, self.param_groups[0]["max_grad_norm"])

        for group in self.param_groups:
            base_lr = group["lr"]
            beta1, beta2, beta3 = group["beta1"], group["beta2"], group["beta3"]
            eps = group["eps"]
            wd = group["weight_decay"]
            warmup, total = group["warmup_steps"], group["total_steps"]
            blend = group["blend"]
            noise_scale = group["noise_scale"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad.clone()
                state = self.state[p]

                if len(state) == 0:
                    state["step"] = 0
                    state["m_fast"] = torch.zeros_like(p.data)
                    state["m_slow"] = torch.zeros_like(p.data)
                    state["v"] = torch.zeros_like(p.data)

                state["step"] += 1
                t = state["step"]
                lr = base_lr * self._get_lr_scale(t, warmup, total)

                # Gradient centralization
                if grad.dim() > 1:
                    grad = grad - grad.mean(dim=tuple(range(1, grad.dim())), keepdim=True)

                # Gradient noise injection (decays as 1/sqrt(t))
                if noise_scale > 0:
                    noise_std = noise_scale / math.sqrt(t)
                    grad = grad + torch.randn_like(grad) * noise_std

                # Weight decay
                if wd > 0:
                    p.data.mul_(1 - lr * wd)

                # Dual momentum
                state["m_fast"].mul_(beta1).add_(grad, alpha=1 - beta1)
                state["m_slow"].mul_(beta3).add_(grad, alpha=1 - beta3)
                state["v"].mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                m_fast_hat = state["m_fast"] / (1 - beta1 ** t)
                m_slow_hat = state["m_slow"] / (1 - beta3 ** t)
                v_hat = state["v"] / (1 - beta2 ** t)

                m_blended = blend * m_fast_hat + (1 - blend) * m_slow_hat
                p.data.addcdiv_(m_blended, v_hat.sqrt().add_(eps), value=-lr)

        return loss

STRATEGY_NOTES = """
Exp 1: Adam = 0.9217
Exp 2: Adam+GC+warmup+cosine = 0.9865
Exp 3: Dual momentum+GC+clip = 0.9877 (CHAMPION)
Exp 4-7: Various tweaks, none beat 0.9877
Exp 8: Gradient noise injection — noise_std = 0.01/sqrt(t)
  - Regularization via noise should close overfitting gap
  - Train/val gap: 0.01 vs 0.055 → noise may help flatten loss surface
"""
