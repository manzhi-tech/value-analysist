import yaml
from pathlib import Path

class AgentConfigLoader:
    @staticmethod
    def load_yaml(file_path: Path | str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_configs(agent_dir: Path | str):
        """
        从指定目录加载 agents.yaml 和 tasks.yaml。
        """
        path = Path(agent_dir)
        agents_config = AgentConfigLoader.load_yaml(path / "agents.yaml")
        tasks_config = AgentConfigLoader.load_yaml(path / "tasks.yaml")
        return agents_config, tasks_config
