import os
import sys
from unittest.mock import MagicMock, patch, ANY
import types

sys.modules['transformers'] = types.ModuleType('transformers')
sys.modules['transformers'].pipeline = lambda *a, **k: None
sys.modules['langchain'] = types.ModuleType('langchain')
sys.modules['langchain'].LLMChain = object
sys.modules['langchain'].PromptTemplate = types.SimpleNamespace(from_template=lambda t: t)
sys.modules['langchain.llms'] = types.ModuleType('langchain.llms')
sys.modules['langchain.llms'].HuggingFacePipeline = object

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.story_generator import generate_story


@patch('src.story_generator.LLMChain')
@patch('src.story_generator.HuggingFacePipeline')
@patch('src.story_generator.pipeline')
def test_generate_story_uses_default_model(pipeline_mock, hf_mock, llmchain_mock):
    prompt = "Once upon a time"
    expected = "A brave hero emerged."

    # Mock pipeline from transformers
    fake_pipeline = MagicMock()
    pipeline_mock.return_value = fake_pipeline

    # Mock HuggingFacePipeline to return an object used by LLMChain
    hf_instance = MagicMock()
    hf_mock.return_value = hf_instance

    # Mock LLMChain.run to return expected text
    chain_instance = MagicMock()
    chain_instance.run.return_value = expected
    llmchain_mock.return_value = chain_instance

    result = generate_story(prompt)

    pipeline_mock.assert_called_once_with('text-generation', model='gpt2')
    hf_mock.assert_called_once_with(pipeline=fake_pipeline)
    llmchain_mock.assert_called_once_with(prompt=ANY, llm=hf_instance)
    chain_instance.run.assert_called_once_with(prompt)

    assert result == expected


@patch('src.story_generator.LLMChain')
@patch('src.story_generator.HuggingFacePipeline')
@patch('src.story_generator.pipeline')
def test_generate_story_custom_model(pipeline_mock, hf_mock, llmchain_mock):
    prompt = "In a galaxy"
    model = "distilgpt2"
    expected = "far away..."

    fake_pipeline = MagicMock()
    pipeline_mock.return_value = fake_pipeline

    hf_instance = MagicMock()
    hf_mock.return_value = hf_instance

    chain_instance = MagicMock()
    chain_instance.run.return_value = expected
    llmchain_mock.return_value = chain_instance

    result = generate_story(prompt, model_name=model)

    pipeline_mock.assert_called_once_with('text-generation', model=model)
    hf_mock.assert_called_once_with(pipeline=fake_pipeline)
    llmchain_mock.assert_called_once_with(prompt=ANY, llm=hf_instance)
    chain_instance.run.assert_called_once_with(prompt)

    assert result == expected
