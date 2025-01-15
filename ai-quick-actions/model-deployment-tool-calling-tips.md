# Tool Calling

The latest [VLLM](ai-quick-actions-containers.md) container in AQUA introduces **tool calling** capabilities. Tool calling allows your model to invoke external functions during inference, enhancing its ability to provide context-specific answers. For more detailed explanations, visit the official VLLM [documentation](https://docs.vllm.ai/en/latest/features/tool_calling.html).


## Enable Tool Calling
To enable tool calling within AQUA, you must specify additional parameters **during model deployment**. In the following example, we are enabling tool calling for the **LLama-3** group of models.

1. Go to the **Advanced Settings** during [model deployment](model-deployment-tips.md).
2. Add the following parameters:

```bash
  --enable-auto-tool-choice
  --tool-call-parser llama3_json
```

Note: Each group of models in VLLM may require a different tool call parser. For the latest list of supported models and parsers, refer to the official VLLM [documentation](https://docs.vllm.ai/en/latest/features/tool_calling.html).


## Usage
Below is a Python example demonstrating how to set up and use tool calling with the VLLM container and **LLama-3** model in AQUA. This code snippet uses the `langchain_community.chat_models.ChatOCIModelDeployment` class and a simple tool function to query an external exchange rate API. Alternatively, you can use the `ads.llm.ChatOCIModelDeployment` class, which may include the most recent code updates. For more details visit the ADS official [documentation](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/large_language_model/langchain_models.html#tool-calling)

```python
import os
import requests

import ads
# from ads.llm import ChatOCIModelDeployment
from langchain_community.chat_models import ChatOCIModelDeployment
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

ads.set_auth("resource_principal")

llm = ChatOCIModelDeployment(
    model="odsc-llm",
    endpoint= f"https://modeldeployment.oci.customer-oci.com/<OCID>/predict",
    tool_choice="auto",
)

@tool
def get_exchange_rate(currency:str) -> str:
    """Obtain the current exchange rates of currency in ISO 4217 Three Letter Currency Code"""

    response = requests.get(f"https://open.er-api.com/v6/latest/{currency}")
    return response.json()

tools = [get_exchange_rate]
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

agent_executor.invoke({"input": "what's the currency conversion of USD to RUB"})
```

You can also specify a Chat Template tailored for a specific model. A list of pre-configured Chat Templates provided by VLLM is available in their GitHub repository. Below is an example demonstrating how to utilize a Chat Template capability.

```python

# The helper method to read the template file
def read_template(filename):
  with open(filename, mode="r", encoding="utf-8") as f:
      return f.read()

llm = ChatOCIModelDeployment(
    model="odsc-llm",
    endpoint= f"https://modeldeployment.oci.customer-oci.com/<OCID>/predict",
    tool_choice="auto",
    chat_template=read_template("tool_chat_template_llama3.2_json.jinja")
)
```

