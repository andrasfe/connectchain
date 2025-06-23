# Copyright 2023 American Express Travel Related Services Company, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.
"""Unit Test for ValidLLMChain"""
import os
from unittest import TestCase
from unittest.mock import patch

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from connectchain.chains import ValidLLMChain
from connectchain.utils.exceptions import OperationNotPermittedException


def my_sanitizer(query: str) -> str:
    """Sanitizer function"""
    if query == "BADWORD":
        raise OperationNotPermittedException(f"Illegal execution detected: {query}")

    return query


class TestValidLLMChain(TestCase):
    """Test Class for ValidLLMChain"""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_run(self):
        """Test run method of ValidLLMChain"""
        prompt_template = "Tell me about the rare bird, {rare_bird_type}."
        prompt = PromptTemplate(input_variables=["rare_bird_type"], template=prompt_template)

        # create mock ChatOpenAI instance
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key="12345",
            openai_api_base="stub",
        )

        chain = ValidLLMChain(llm=llm, prompt=prompt, output_sanitizer=my_sanitizer)
        # patch LLMChain.run() using with patch.object
        with patch.object(
            LLMChain, "run", return_value="Interesting information about the Streak-backed Oriole."
        ):
            chain.run("Streak-backed Oriole")
        with patch.object(LLMChain, "run", return_value="BADWORD"):
            try:
                chain.run("BADWORD")
            except OperationNotPermittedException as e:
                print(f"Execution aborted. I/O operation detected: {e}")
