"""
UPE-78 AI Control Layer
Agent orchestration, control theory, and multi-agent coordination
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict
import heapq
import time


@dataclass
class AgentState:
    """State representation for an agent"""
    id: int
    position: np.ndarray
    velocity: np.ndarray
    energy: float = 100.0
    status: str = "active"  # active, idle, terminated
    task_queue: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class AgentSwarm:
    """
    Multi-agent swarm with spatial hashing and topology-aware coordination.

    Supports up to 200+ agents with O(n) collision detection.
    """

    def __init__(self, n_agents: int = 200, spatial_dim: int = 3,
                 cell_size: float = 10.0, spatial_hashing: bool = True):
        self.n_agents = n_agents
        self.spatial_dim = spatial_dim
        self.cell_size = cell_size
        self.use_spatial_hash = spatial_hashing

        self.agents: Dict[int, AgentState] = {}
        self._spatial_grid: Dict[Tuple, List[int]] = defaultdict(list)
        self._time = 0.0

        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize agent population"""
        for i in range(self.n_agents):
            pos = np.random.randn(self.spatial_dim) * 100
            vel = np.random.randn(self.spatial_dim) * 5
            self.agents[i] = AgentState(
                id=i,
                position=pos,
                velocity=vel,
                energy=100.0,
                status="active"
            )
            self._add_to_grid(i, pos)

    def _get_cell(self, position: np.ndarray) -> Tuple:
        """Get spatial hash cell for position"""
        return tuple((position / self.cell_size).astype(int))

    def _add_to_grid(self, agent_id: int, position: np.ndarray):
        """Add agent to spatial grid"""
        if self.use_spatial_hash:
            cell = self._get_cell(position)
            self._spatial_grid[cell].append(agent_id)

    def _remove_from_grid(self, agent_id: int, position: np.ndarray):
        """Remove agent from spatial grid"""
        if self.use_spatial_hash:
            cell = self._get_cell(position)
            if agent_id in self._spatial_grid[cell]:
                self._spatial_grid[cell].remove(agent_id)

    def _get_neighbors(self, agent_id: int) -> List[int]:
        """Get neighboring agents using spatial hashing (O(1) average)"""
        if not self.use_spatial_hash:
            # Brute force O(n)
            return [a for a in self.agents if a != agent_id]

        agent = self.agents[agent_id]
        cell = self._get_cell(agent.position)

        neighbors = []
        # Check 3x3x3 neighborhood of cells
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    neighbor_cell = (cell[0]+dx, cell[1]+dy, cell[2]+dz)
                    neighbors.extend(self._spatial_grid.get(neighbor_cell, []))

        return [n for n in neighbors if n != agent_id]

    def update(self, dt: float = 0.1, forces: Dict[int, np.ndarray] = None):
        """
        Update all agents with physics integration.

        Args:
            dt: Time step
            forces: Optional external forces per agent
        """
        if forces is None:
            forces = {}

        # Clear grid for rehashing
        self._spatial_grid.clear()

        for agent_id, agent in self.agents.items():
            if agent.status != "active":
                continue

            # Get neighbors for local interaction
            neighbors = self._get_neighbors(agent_id)

            # Compute flocking forces (separation, alignment, cohesion)
            sep = np.zeros(self.spatial_dim)
            align = np.zeros(self.spatial_dim)
            cohesion = np.zeros(self.spatial_dim)

            for neighbor_id in neighbors:
                neighbor = self.agents[neighbor_id]
                diff = agent.position - neighbor.position
                dist = np.linalg.norm(diff) + 1e-6

                # Separation
                if dist < 20.0:
                    sep += diff / dist

                # Alignment
                align += neighbor.velocity

                # Cohesion
                cohesion += neighbor.position

            if len(neighbors) > 0:
                align /= len(neighbors)
                cohesion = cohesion / len(neighbors) - agent.position

            # Apply forces
            accel = sep * 2.0 + align * 0.5 + cohesion * 0.1
            if agent_id in forces:
                accel += forces[agent_id]

            # Integrate
            agent.velocity += accel * dt
            agent.velocity = np.clip(agent.velocity, -50, 50)  # Speed limit
            agent.position += agent.velocity * dt
            agent.energy -= 0.01 * dt * np.linalg.norm(agent.velocity)

            # Rehash
            self._add_to_grid(agent_id, agent.position)

        self._time += dt

    def orchestrate(self, target: str = "discovery", 
                    strategy: str = "distributed") -> dict:
        """
        Orchestrate swarm toward target objective.

        Args:
            target: Objective type (discovery, defense, exploration)
            strategy: Coordination strategy

        Returns:
            Performance metrics
        """
        # Generate target forces based on strategy
        forces = {}

        if strategy == "distributed":
            # Each agent explores independently with weak attraction to center
            center = np.mean([a.position for a in self.agents.values()], axis=0)
            for agent_id, agent in self.agents.items():
                to_center = center - agent.position
                forces[agent_id] = to_center * 0.01

        elif strategy == "centralized":
            # All agents converge to single target
            target_pos = np.random.randn(self.spatial_dim) * 50
            for agent_id, agent in self.agents.items():
                to_target = target_pos - agent.position
                forces[agent_id] = to_target * 0.05

        elif strategy == "gradient":
            # Follow gradient field (simulated)
            for agent_id, agent in self.agents.items():
                # Simulated gradient toward origin
                grad = -agent.position * 0.001
                forces[agent_id] = grad

        # Run simulation
        for _ in range(100):
            self.update(dt=0.1, forces=forces)

        return self.get_metrics()

    def get_metrics(self) -> dict:
        """Return swarm performance metrics"""
        positions = np.array([a.position for a in self.agents.values()])
        velocities = np.array([a.velocity for a in self.agents.values()])
        energies = [a.energy for a in self.agents.values()]

        # Compute swarm cohesion
        center = np.mean(positions, axis=0)
        dispersion = np.mean(np.linalg.norm(positions - center, axis=1))

        return {
            "n_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.status == "active"),
            "mean_energy": np.mean(energies),
            "dispersion": dispersion,
            "mean_velocity": np.mean(np.linalg.norm(velocities, axis=1)),
            "simulation_time": self._time
        }

    def assign_task(self, agent_id: int, task: str):
        """Assign task to specific agent"""
        if agent_id in self.agents:
            self.agents[agent_id].task_queue.append(task)

    def broadcast(self, task: str):
        """Broadcast task to all agents"""
        for agent in self.agents.values():
            agent.task_queue.append(task)


class ControlTheory:
    """Control theory implementations for agent systems"""

    @staticmethod
    def pid_controller(error: float, integral: float, derivative: float,
                        Kp: float = 1.0, Ki: float = 0.1, Kd: float = 0.5) -> float:
        """PID control output"""
        return Kp * error + Ki * integral + Kd * derivative

    @staticmethod
    def lqr_gain(A: np.ndarray, B: np.ndarray, Q: np.ndarray, 
                 R: np.ndarray) -> np.ndarray:
        """
        Compute LQR gain matrix.

        Solves discrete-time algebraic Riccati equation.
        """
        # Simplified iterative solution
        P = Q.copy()
        for _ in range(1000):
            P_new = Q + A.T @ P @ A - A.T @ P @ B @ np.linalg.inv(R + B.T @ P @ B) @ B.T @ P @ A
            if np.linalg.norm(P_new - P) < 1e-6:
                break
            P = P_new

        K = np.linalg.inv(R + B.T @ P @ B) @ B.T @ P @ A
        return K

    @staticmethod
    def kalman_filter(x: np.ndarray, P: np.ndarray, z: np.ndarray,
                      F: np.ndarray, H: np.ndarray, Q: np.ndarray, 
                      R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Kalman filter update step.

        Args:
            x: State estimate
            P: Error covariance
            z: Measurement
            F: State transition
            H: Measurement matrix
            Q: Process noise
            R: Measurement noise

        Returns:
            Updated (x, P)
        """
        # Predict
        x_pred = F @ x
        P_pred = F @ P @ F.T + Q

        # Update
        y = z - H @ x_pred
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)

        x_new = x_pred + K @ y
        P_new = (np.eye(len(x)) - K @ H) @ P_pred

        return x_new, P_new


class Orchestrator:
    """High-level orchestrator for multi-agent systems"""

    def __init__(self, max_agents: int = 1000):
        self.max_agents = max_agents
        self.swarms: Dict[str, AgentSwarm] = {}
        self._tasks = []
        self._metrics = defaultdict(list)

    def create_swarm(self, name: str, n_agents: int, **kwargs) -> AgentSwarm:
        """Create named swarm"""
        swarm = AgentSwarm(n_agents=n_agents, **kwargs)
        self.swarms[name] = swarm
        return swarm

    def coordinate_swarms(self, objective: str) -> dict:
        """Coordinate multiple swarms toward objective"""
        results = {}

        for name, swarm in self.swarms.items():
            metrics = swarm.orchestrate(target=objective)
            results[name] = metrics
            self._metrics[name].append(metrics)

        return results

    def get_aggregate_metrics(self) -> dict:
        """Get aggregate metrics across all swarms"""
        total_agents = sum(s.get_metrics()["n_agents"] for s in self.swarms.values())
        active_agents = sum(s.get_metrics()["active_agents"] for s in self.swarms.values())

        return {
            "total_swarms": len(self.swarms),
            "total_agents": total_agents,
            "active_agents": active_agents,
            "efficiency": active_agents / total_agents if total_agents > 0 else 0
        }
