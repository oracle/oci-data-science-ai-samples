# Latest inference containers supported in AI Quick Actions

|Server|Version|Supported Formats|Supported Shapes| Supported Models/Architectures                                                                                                  |
|------|-------|-----------------|----------------|---------------------------------------------------------------------------------------------------------------------------------|
|[vLLM](https://github.com/vllm-project/vllm/releases/tag/v0.6.2)|0.6.2|safe-tensors|A10, A100, H100| [v0.6.2 supported models](https://docs.vllm.ai/en/v0.6.2/models/supported_models.html#supported-models)                         |
|[Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference/releases/tag/v2.0.1)|2.0.1.4|safe-tensors|A10, A100, H100| [v2.0.1 supported models](https://github.com/huggingface/text-generation-inference/blob/v2.0.1/docs/source/supported_models.md) |
|[Llama-cpp](https://github.com/abetlen/llama-cpp-python/releases/tag/v0.2.78)|0.2.78.0|gguf|Amphere ARM| [llama.cpp@fd5ea0f supported models](https://github.com/ggerganov/llama.cpp/tree/fd5ea0f897ecb3659d6c269ef6f3d833e865ead7)                                                                                                      |


<!-- 
The below content is hidden in the markdown, useful for updating the above table:

- Steps to find supported models list: 
1. vLLM
    - Visit the vLLM documentation page for supported models https://docs.vllm.ai/en/latest/models/supported_models.html
    - In the bottom right, switch to the required vLLM version. 

2. TGI
    - Visit the supported models page in TGI github repo https://github.com/huggingface/text-generation-inference/blob/main/docs/source/supported_models.md
    - Select the version tag on the left pane, for example v2.0.1. 
3. Llama-cpp-python
    - Visit the llama-cpp-python repo and select the version tag. For example: https://github.com/abetlen/llama-cpp-python/tree/v0.2.78/vendor
    - Click on the llama.cpp commit used by this version.
    - Scroll down in the readme page and find the section on Supported Models. Link to the section if a hyperlink is available, else link the markdown.
-->   