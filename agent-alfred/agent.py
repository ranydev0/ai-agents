from smolagents import InferenceClientModel
from smolagents import CodeAgent
from tools.light import switch_light
from tools.weather import get_weather
from tools.gmail import create_draft_email
import yaml


model = InferenceClientModel(
    max_tokens=2096,
    temperature=0.5,
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    custom_role_conversions=None,
    provider="nscale",
)

with open("prompts.yaml", "r") as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[switch_light, get_weather, create_draft_email],
    additional_authorized_imports=["pandas", "datetime"],
    max_steps=6,
    verbosity_level=1,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates,
)
