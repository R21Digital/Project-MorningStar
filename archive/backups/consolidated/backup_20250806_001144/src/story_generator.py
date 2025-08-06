from langchain import LLMChain, PromptTemplate
from langchain.llms import HuggingFacePipeline
from transformers import pipeline


def generate_story(prompt: str, model_name: str = "gpt2") -> str:
    """Generate a short story using a HuggingFace model via LangChain."""
    text_gen = pipeline("text-generation", model=model_name)
    hf_llm = HuggingFacePipeline(pipeline=text_gen)
    template = PromptTemplate.from_template("{prompt}")
    chain = LLMChain(prompt=template, llm=hf_llm)
    return chain.run(prompt)
