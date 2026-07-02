"""
PPO Reinforcement Learning Scheduling Agent.
Uses stable-baselines3 PPO with a custom Gym environment.
Toggle between rule-based and RL via config: USE_RL_AGENT=true

CURRENT STATE: Rule-based is default (stable, no training needed).
RL agent runs in inference mode if a trained model exists at rl/models/scheduling_ppo.zip.

To train: run `python services/rl_agent.py --train`
"""
import os
import numpy as np
from typing import Optional

USE_RL = os.getenv("USE_RL_AGENT", "false").lower() == "true"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../rl/models/scheduling_ppo.zip")


def rl_available() -> bool:
    """Check if stable-baselines3 + trained model are both available."""
    try:
        import stable_baselines3  # noqa
        return USE_RL and os.path.exists(MODEL_PATH)
    except ImportError:
        return False


# ── Custom Gym Environment ────────────────────────────────────────────────────
def build_env():
    """
    Build a simple scheduling Gym environment for training.
    State: [urgency, wait_time, fairness_index, slots_available]
    Action: 0=assign_earliest_slot, 1=assign_fairness_adjusted_slot, 2=defer
    Reward: urgency_reward + fairness_reward - wait_penalty
    """
    try:
        import gymnasium as gym
        from gymnasium import spaces

        class SchedulingEnv(gym.Env):
            metadata = {"render_modes": []}

            def __init__(self):
                super().__init__()
                # Observation: [urgency(1-5), wait_hours, fairness(0-1), slots_pct(0-1)]
                self.observation_space = spaces.Box(
                    low=np.array([1, 0, 0, 0], dtype=np.float32),
                    high=np.array([5, 168, 1, 1], dtype=np.float32),
                )
                # Actions: 0=assign_early, 1=assign_fair, 2=defer
                self.action_space = spaces.Discrete(3)
                self.state = None
                self.step_count = 0

            def reset(self, seed=None, options=None):
                super().reset(seed=seed)
                self.state = np.array([
                    np.random.uniform(1, 5),   # urgency
                    np.random.uniform(0, 72),   # wait hours
                    np.random.uniform(0.5, 1),  # fairness
                    np.random.uniform(0.1, 1),  # slots available
                ], dtype=np.float32)
                self.step_count = 0
                return self.state, {}

            def step(self, action):
                urgency, wait, fairness, slots = self.state
                reward = 0.0

                if action == 0:  # assign_early
                    reward = urgency * 2 - wait * 0.1 + fairness * 3
                elif action == 1:  # assign_fair_adjusted
                    reward = urgency + fairness * 5 - wait * 0.05
                elif action == 2:  # defer
                    reward = -urgency * 2  # penalize deferring urgent cases

                # Constrained MDP: penalize unfairness
                if fairness < 0.6:
                    reward -= 5

                self.step_count += 1
                done = self.step_count >= 50

                # Update state
                self.state = np.array([
                    np.random.uniform(1, 5),
                    max(0, wait - 2),
                    min(1, fairness + 0.01 if action == 1 else fairness - 0.01),
                    max(0, slots - 0.02),
                ], dtype=np.float32)

                return self.state, reward, done, False, {}

            def render(self):
                pass

        return SchedulingEnv()
    except ImportError:
        return None


def train_agent(timesteps: int = 50_000):
    """Train the PPO agent and save model."""
    try:
        from stable_baselines3 import PPO
        env = build_env()
        if env is None:
            print("gymnasium not installed. Run: pip install gymnasium stable-baselines3")
            return

        os.makedirs(os.path.join(os.path.dirname(__file__), "../rl/models"), exist_ok=True)
        print(f"Training PPO agent for {timesteps} timesteps...")
        model = PPO("MlpPolicy", env, verbose=1, learning_rate=3e-4, n_steps=512)
        model.learn(total_timesteps=timesteps)
        model.save(MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
    except ImportError:
        print("stable-baselines3 not installed. Run: pip install stable-baselines3")


def rl_predict_action(urgency: float, wait_hours: float, fairness: float, slots_pct: float) -> int:
    """
    Use trained PPO model to predict the best scheduling action.
    Returns: 0=early, 1=fairness_adjusted, 2=defer
    Falls back to rule-based if model not available.
    """
    if not rl_available():
        # Rule-based fallback
        if urgency >= 4:
            return 0  # assign_early for high urgency
        elif fairness < 0.7:
            return 1  # fairness-adjusted if fairness is low
        return 0

    from stable_baselines3 import PPO
    model = PPO.load(MODEL_PATH)
    obs = np.array([urgency, wait_hours, fairness, slots_pct], dtype=np.float32)
    action, _ = model.predict(obs, deterministic=True)
    return int(action)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Train the PPO agent")
    parser.add_argument("--timesteps", type=int, default=50_000)
    args = parser.parse_args()
    if args.train:
        train_agent(args.timesteps)
    else:
        print("RL Agent Status:")
        print(f"  USE_RL_AGENT: {USE_RL}")
        print(f"  Model exists: {os.path.exists(MODEL_PATH)}")
        print(f"  RL active: {rl_available()}")
        # Demo prediction
        action = rl_predict_action(urgency=4.0, wait_hours=5.0, fairness=0.8, slots_pct=0.5)
        print(f"  Demo prediction (urgency=4): action={action} ({'early' if action==0 else 'fair' if action==1 else 'defer'})")
