import streamlit as st
import os
import subprocess
import openai
import logging
from typing import Dict, Any, List

# =========================
# LOGGING MANAGER
# =========================
class LoggingManager:
    def __init__(self, log_level: str = "INFO"):
        self.log_level = log_level
        self._setup_logger()

    def _setup_logger(self):
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

    def log_info(self, msg: str) -> None:
        logging.info(msg)

    def log_error(self, msg: str) -> None:
        logging.error(msg)

    def log_debug(self, msg: str) -> None:
        logging.debug(msg)


# =========================
# DOCUMENT PARSERS
# =========================
class DocumentParser:
    def __init__(self, file_bytes: bytes, filename: str):
        self.file_bytes = file_bytes
        self.filename = filename
        self.raw_content = ""
        self.parsed_sections = {}

    def parse_design(self) -> Dict[str, str]:
        """
        Basic text extraction. In real usage, you could detect file type
        and parse PDFs, DOCX, etc. more robustly.
        """
        try:
            self.raw_content = self.file_bytes.decode("utf-8", errors="ignore")
        except:
            self.raw_content = ""

        self.parsed_sections = {
            "Overview": self.raw_content[:200],
            "Details": self.raw_content[200:400]
        }
        return self.parsed_sections

    def extract_classes(self) -> List[str]:
        """
        Mock method to identify classes from the text.
        """
        # You might do a regex search for "class MyClass" etc.
        return ["SampleClassFromDoc"]


class ThirdPartyDocParser:
    def __init__(self, file_bytes: bytes, filename: str):
        self.file_bytes = file_bytes
        self.filename = filename
        self.raw_content = ""
        self.parsed_integration_points = {}

    def parse_docs(self) -> Dict[str, Any]:
        """
        Parse the third-party docs for integration details.
        """
        try:
            self.raw_content = self.file_bytes.decode("utf-8", errors="ignore")
        except:
            self.raw_content = ""

        self.parsed_integration_points = {
            "API_Endpoints": ["https://api.thirdparty.com/v1/resource"]
        }
        return self.parsed_integration_points

    def summarize_docs(self) -> Dict[str, Any]:
        """
        Filter the raw content to only keep relevant integration sections.
        """
        return self.parsed_integration_points


# =========================
# CODE MANAGER
# =========================
class CodeManager:
    def __init__(self):
        self.current_code = ""

    def store_code(self, code: str) -> None:
        self.current_code = code

    def get_code(self) -> str:
        return self.current_code

    def apply_patches(self, patch: Dict[str, Any]) -> None:
        """
        Placeholder for patch/diff application logic.
        """
        pass


# =========================
# TEST MANAGER
# =========================
class TestManager:
    def __init__(self):
        self.test_code = ""

    def generate_unit_tests(self, code: str) -> str:
        """
        Create a basic unit test file for demonstration.
        """
        self.test_code = (
            "import unittest\n\n"
            "class TestGeneratedCode(unittest.TestCase):\n"
            "    def test_sample(self):\n"
            "        self.assertTrue(True)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        )
        return self.test_code

    def generate_integration_tests(self, code: str, third_party_info: Dict[str, Any]) -> str:
        integration_test_code = (
            "import unittest\n\n"
            "class TestIntegration(unittest.TestCase):\n"
            "    def test_third_party_api(self):\n"
            f"        self.assertIn('https://api.thirdparty.com/v1/resource', {third_party_info['API_Endpoints']})\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        )
        return integration_test_code

    def run_tests(self, test_code_str: str) -> Dict[str, Any]:
        """
        Attempt to run the tests in a subprocess.
        """
        try:
            with open("temp_test_file.py", "w") as f:
                f.write(test_code_str)

            result = subprocess.run(["python", "temp_test_file.py"], capture_output=True, text=True)
            passed = (result.returncode == 0)
            logs = result.stdout + "\n" + result.stderr
        except Exception as e:
            passed = False
            logs = f"Error running tests: {e}"

        # Clean up
        if os.path.exists("temp_test_file.py"):
            os.remove("temp_test_file.py")

        return {"passed": passed, "logs": logs}


# =========================
# DOCUMENTATION GENERATOR
# =========================
class DocumentationGenerator:
    def __init__(self):
        self.doc_content = ""

    def compile_implementation_doc(self, code: str, tests_summary: str) -> str:
        """
        Combine code, test coverage, or other info into a final doc.
        """
        self.doc_content = (
            "# Implementation Documentation\n\n"
            "## Generated Code\n\n"
            f"```python\n{code}\n```\n\n"
            "## Test Summary\n\n"
            f"```\n{tests_summary}\n```\n"
        )
        return self.doc_content

    def generate_scope_and_assumptions(
        self, scope: Dict[str, Any], assumptions: Dict[str, Any], out_of_scope: List[str]
    ) -> str:
        scope_section = "\n".join([f"- {k}: {v}" for k, v in scope.items()])
        assumptions_section = "\n".join([f"- {k}: {v}" for k, v in assumptions.items()])
        oos_section = "\n".join([f"- {item}" for item in out_of_scope])

        additional_doc = (
            "## Scope\n" f"{scope_section}\n\n"
            "## Assumptions\n" f"{assumptions_section}\n\n"
            "## Out of Scope\n" f"{oos_section}\n\n"
        )
        self.doc_content += additional_doc
        return self.doc_content

    def finalize_documentation(self) -> str:
        return self.doc_content


# =========================
# GENERATIVE & ADVERSARIAL AGENTS
# =========================

class GenerativeAgent:
    """
    Calls the OpenAI API to generate code from the user’s requirements.
    """
    def __init__(self, model_engine: str = "gpt-4"):
        # We'll retrieve the API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.model_engine = model_engine
        openai.api_key = self.openai_api_key  # Set the OpenAI key for calls

    def propose_code(self, requirements: Dict[str, Any]) -> str:
        """
        Use openai.ChatCompletion to generate initial code based on the requirements.
        """
        if not self.openai_api_key:
            return "# ERROR: No OpenAI API key provided.\n"

        # Construct a system message describing the role
        system_content = (
            "You are a top-tier Python engineer. "
            "Generate Python code that implements the following design requirements:\n\n"
            f"{requirements}"
        )

        # Make a ChatCompletion call
        try:
            response = openai.ChatCompletion.create(
                model=self.model_engine,
                messages=[
                    {"role": "system", "content": system_content},
                    {
                        "role": "user",
                        "content": (
                            "Please generate a Python class or function that addresses the "
                            "above requirements. Include docstrings and follow best practices."
                        ),
                    }
                ],
                temperature=0.2,
            )
            code = response.choices[0].message.content
            return code
        except Exception as e:
            return f"# ERROR: Failed to call OpenAI API. Details: {e}\n"

    def refine_code(self, current_code: str, improvements: Dict[str, Any]) -> str:
        """
        Use openai.ChatCompletion to refine the existing code based on the suggested improvements.
        We'll pass the current code and the improvement instructions.
        """
        if not self.openai_api_key:
            return "# ERROR: No OpenAI API key provided.\n"

        system_content = (
            "You are a top-tier Python engineer. "
            "Refine the following code based on the improvement instructions. "
            "Apply only the relevant changes needed:\n\n"
        )

        improvement_instructions = "\n".join(
            [f"- {k}: {v}" for k, v in improvements.items() if v]
        )

        prompt = f"{system_content}\nCurrent Code:\n{current_code}\n\nImprovements:\n{improvement_instructions}"

        try:
            response = openai.ChatCompletion.create(
                model=self.model_engine,
                messages=[
                    {"role": "system", "content": system_content},
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
            )
            refined_code = response.choices[0].message.content
            return refined_code
        except Exception as e:
            return f"# ERROR: Failed to refine code via OpenAI. Details: {e}\n"


class AdversarialAgent:
    """
    Also calls the OpenAI API to review and critique the code,
    providing suggestions for improvements.
    """
    def __init__(self, code_quality_criteria: List[str] = None, model_engine: str = "gpt-4"):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        openai.api_key = self.openai_api_key
        self.model_engine = model_engine
        self.code_quality_criteria = code_quality_criteria or ["PEP8", "Logging", "Error Handling"]

    def review_code(self, code: str) -> Dict[str, Any]:
        """
        Uses OpenAI to review the code and decide if improvements are needed.
        Returns a dict with `needs_improvement` and `review_comments`.
        """
        if not self.openai_api_key:
            return {"needs_improvement": False, "review_comments": "No OpenAI API key."}

        # Summarize the code quality criteria
        criteria_str = ", ".join(self.code_quality_criteria)

        system_content = (
            "You are a code reviewer focusing on the following criteria: "
            f"{criteria_str}. Please check the code and see if improvements are needed."
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model_engine,
                messages=[
                    {"role": "system", "content": system_content},
                    {
                        "role": "user",
                        "content": (
                            f"Here is the code:\n\n{code}\n\n"
                            "Do we need to improve anything based on the criteria?"
                        ),
                    }
                ],
                temperature=0.2,
            )

            review_text = response.choices[0].message.content
            # Simple heuristic: if the word "No improvements" or "No issues" is in the text, assume no improvement needed
            needs_improvement = True
            if "no improvements" in review_text.lower() or "no issues" in review_text.lower():
                needs_improvement = False

            return {"needs_improvement": needs_improvement, "review_comments": review_text}
        except Exception as e:
            return {
                "needs_improvement": True,
                "review_comments": f"Error reviewing code: {e}"
            }

    def suggest_improvements(self, code: str) -> Dict[str, Any]:
        """
        Use OpenAI to provide structured improvement instructions
        or a short bullet list of recommended changes.
        """
        if not self.openai_api_key:
            return {"add_docstrings": False, "fix_pep8": False, "optimize_function_calls": False}

        system_content = (
            "You are a code reviewer. Provide a structured set of recommended improvements "
            "for the following code. Do not return the entire code; only return a JSON-like structure "
            "that summarizes the needed changes in short bullet points."
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model_engine,
                messages=[
                    {"role": "system", "content": system_content},
                    {
                        "role": "user",
                        "content": f"Code:\n{code}\n\nPlease list improvements in a JSON format."
                    }
                ],
                temperature=0.2,
            )
            # Attempt to parse a JSON-like structure from the response:
            improvements_text = response.choices[0].message.content
            # For safety, we'll do a naive parse. In a real scenario, use json.loads if valid JSON is guaranteed.
            # Here, let's do a simple approach:
            improvements_dict = {}
            if "docstring" in improvements_text.lower():
                improvements_dict["add_docstrings"] = True
            if "pep8" in improvements_text.lower():
                improvements_dict["fix_pep8"] = True
            if "optimize" in improvements_text.lower():
                improvements_dict["optimize_function_calls"] = True

            return improvements_dict
        except Exception as e:
            return {
                "add_docstrings": False,
                "fix_pep8": False,
                "optimize_function_calls": False,
                "error": str(e)
            }


# =========================
# AGENT ORCHESTRATOR
# =========================
class AgentOrchestrator:
    def __init__(self,
                 gen_agent: GenerativeAgent,
                 adv_agent: AdversarialAgent,
                 code_manager: CodeManager,
                 test_manager: TestManager):
        self.generative_agent = gen_agent
        self.adversarial_agent = adv_agent
        self.code_manager = code_manager
        self.test_manager = test_manager

    def orchestrate_generation(self, requirements: Dict[str, Any]) -> None:
        proposed_code = self.generative_agent.propose_code(requirements)
        self.code_manager.store_code(proposed_code)

    def orchestrate_review(self) -> None:
        code = self.code_manager.get_code()
        review_findings = self.adversarial_agent.review_code(code)
        if review_findings.get("needs_improvement"):
            improvements = self.adversarial_agent.suggest_improvements(code)
            refined_code = self.generative_agent.refine_code(code, improvements)
            self.code_manager.store_code(refined_code)

    def finalize_code(self) -> str:
        return self.code_manager.get_code()

    def iterative_generation_review_cycle(self,
                                          requirements: Dict[str, Any],
                                          max_iterations: int = 3) -> str:
        """
        Repeats the generate → review → refine steps up to `max_iterations`
        or until no improvements are needed.
        """
        for _ in range(max_iterations):
            self.orchestrate_generation(requirements)
            code = self.code_manager.get_code()
            review_findings = self.adversarial_agent.review_code(code)

            if not review_findings.get("needs_improvement"):
                # No improvements needed, break early
                break

            # If improvements are needed, refine
            improvements = self.adversarial_agent.suggest_improvements(code)
            refined_code = self.generative_agent.refine_code(code, improvements)
            self.code_manager.store_code(refined_code)

        return self.finalize_code()


# =========================
# STREAMLIT APP
# =========================
def main():
    st.title("AI-Powered Code Generator (Adversarial/GAN-like) with OpenAI")

    logger = LoggingManager(log_level="DEBUG")

    code_manager = CodeManager()
    test_manager = TestManager()
    doc_generator = DocumentationGenerator()

    # Initialize Agents (and Orchestrator)
    gen_agent = GenerativeAgent(model_engine="gpt-4")  # or "gpt-3.5-turbo"
    adv_agent = AdversarialAgent(model_engine="gpt-4") # or "gpt-3.5-turbo"
    orchestrator = AgentOrchestrator(gen_agent, adv_agent, code_manager, test_manager)

    st.markdown("## 1. Upload Design Document")
    design_file = st.file_uploader("Upload your design doc (PDF, DOCX, TXT, MD...)", type=None)
    third_party_file = st.file_uploader("Upload third-party doc (optional)", type=None)

    if "requirements" not in st.session_state:
        st.session_state["requirements"] = {}

    if st.button("Parse Documents"):
        if design_file is not None:
            parser = DocumentParser(design_file.read(), design_file.name)
            sections = parser.parse_design()
            classes_found = parser.extract_classes()

            st.session_state["requirements"]["parsed_sections"] = sections
            st.session_state["requirements"]["classes"] = classes_found

            st.write("### Parsed Design Document Sections")
            st.write(sections)
            st.write("### Identified Classes")
            st.write(classes_found)
        else:
            st.warning("Please upload a design document first.")

        if third_party_file is not None:
            tp_parser = ThirdPartyDocParser(third_party_file.read(), third_party_file.name)
            integration_info = tp_parser.parse_docs()
            st.session_state["requirements"]["third_party"] = integration_info
            st.write("### Third-Party Integration Info")
            st.write(integration_info)

    st.markdown("## 2. Generate & Review Code")
    if st.button("Generate Code (GAN Cycle)"):
        if "parsed_sections" in st.session_state["requirements"]:
            final_code = orchestrator.iterative_generation_review_cycle(
                st.session_state["requirements"], max_iterations=3
            )
            st.write("### Final Generated Code")
            st.code(final_code, language="python")
        else:
            st.warning("No requirements found. Please parse documents first.")

    st.markdown("## 3. Generate & Run Tests")
    if st.button("Generate and Run Tests"):
        code = code_manager.get_code()
        if code.strip():
            unit_test_code = test_manager.generate_unit_tests(code)
            st.write("### Generated Unit Test Code")
            st.code(unit_test_code, language="python")

            third_party_info = st.session_state["requirements"].get("third_party", {})
            if third_party_info:
                integration_test_code = test_manager.generate_integration_tests(code, third_party_info)
                st.write("### Generated Integration Test Code")
                st.code(integration_test_code, language="python")
            else:
                integration_test_code = ""

            st.write("### Running Unit Tests...")
            results_unit = test_manager.run_tests(unit_test_code)
            st.write(f"**Passed?** {results_unit['passed']}")
            st.write("**Logs**")
            st.text(results_unit['logs'])

            if integration_test_code.strip():
                st.write("### Running Integration Tests...")
                results_integration = test_manager.run_tests(integration_test_code)
                st.write(f"**Passed?** {results_integration['passed']}")
                st.write("**Logs**")
                st.text(results_integration['logs'])

            # Summarize test logs
            test_summary = "Unit Test Results:\n" + results_unit['logs']
            if integration_test_code.strip():
                test_summary += "\nIntegration Test Results:\n" + results_integration['logs']

            st.session_state["test_summary"] = test_summary
        else:
            st.warning("No generated code found. Please generate code first.")

    st.markdown("## 4. Create Documentation Artifact")
    if st.button("Generate Documentation"):
        code = code_manager.get_code()
        tests_summary = st.session_state.get("test_summary", "")
        doc_content = doc_generator.compile_implementation_doc(code, tests_summary)

        # Example scope/assumptions/out-of-scope
        scope = {"Feature A": "Fully Implemented", "Feature B": "Partial"}
        assumptions = {"Python Version": "3.9+", "Libraries": "Streamlit, openai"}
        out_of_scope = ["Advanced security", "CI/CD pipeline", "Performance/Load Testing"]

        final_doc = doc_generator.generate_scope_and_assumptions(scope, assumptions, out_of_scope)
        st.write("### Final Documentation")
        st.markdown(final_doc)

        st.download_button(
            label="Download Documentation (Markdown)",
            data=final_doc,
            file_name="implementation_doc.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()
