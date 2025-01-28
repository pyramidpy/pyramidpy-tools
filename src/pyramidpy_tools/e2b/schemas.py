from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CodeBlockHighlight(BaseModel):
    """Represents a highlighted section in a code block"""

    start: int = Field(description="The start index of the highlighted section")
    end: int = Field(description="The end index of the highlighted section")


class CodeBlock(BaseModel):
    """Represents a block of code with optional highlighting"""

    code: str = Field(
        description="The code to display, do not include backticks or language"
    )
    language: str = Field(description="The language of the code")
    highlighted_sections: Optional[List[CodeBlockHighlight]] = Field(
        description="The highlighted sections of the code if any", default=None
    )


class CodeResultOutput(BaseModel):
    """Represents the output of code execution"""

    text: Optional[str] = Field(
        description="The text output of the code execution", default=None
    )
    html: Optional[str] = Field(
        description="The HTML output of the code execution", default=None
    )
    markdown: Optional[str] = Field(
        description="The Markdown output of the code execution", default=None
    )
    svg: Optional[str] = Field(
        description="The SVG output of the code execution", default=None
    )
    png: Optional[str] = Field(
        description="The PNG output of the code execution", default=None
    )
    jpeg: Optional[str] = Field(
        description="The JPEG output of the code execution", default=None
    )
    pdf: Optional[str] = Field(
        description="The PDF output of the code execution", default=None
    )
    latex: Optional[str] = Field(
        description="The LaTeX output of the code execution", default=None
    )
    json: Optional[Dict[str, Any]] = Field(
        description="The JSON output of the code execution", default=None
    )
    javascript: Optional[str] = Field(
        description="The JavaScript output of the code execution", default=None
    )
    data: Optional[Dict[str, Any]] = Field(
        description="Additional data output of the code execution", default=None
    )
    graph: Optional[Dict[str, Any]] = Field(
        description="The graph output of the code execution", default=None
    )
    extra: Optional[str] = Field(
        description="Any extra output of the code execution", default=None
    )
    is_main_result: bool = Field(
        description="Whether this data is the result of the cell", default=False
    )

    def is_data_source(self) -> bool:
        """Check if this output contains data that can be used as a data source"""
        return bool(self.data or self.graph or self.json or self.javascript)


class CodeResult(BaseModel):
    """Represents the complete result of code execution"""

    logs: Optional[str | List[str]] = Field(
        description="The logs of the code execution", default=None
    )
    output: str = Field(description="The output of the code execution")
    files: Optional[List[str]] = Field(
        description="Files generated during execution", default=None
    )
    data_sources: Optional[List[Dict[str, Any]]] = Field(
        description="Data sources generated during execution", default=None
    )
    error: Optional[str] = Field(
        description="Error message if the execution failed", default=None
    )
    results: Optional[List[CodeResultOutput]] = Field(
        description="The results of the code execution", default=None, exclude=True
    )

    def to_llm_result(self) -> str:
        """Convert the result to a format suitable for LLM consumption"""
        if not self.error:
            return f"""
             Code executed successfully. 
             NB! Any files generated are directly shown to the user. You do not need to relink them.
             logs: {self.logs}
             output: {self.output}
             files: {self.files}
            """
        else:
            return f"""
                Code execution failed.
                logs: {self.logs}
                output: {self.output}
                files: {self.files}
                error: {self.error}
            """


class E2BConfig(BaseModel):
    """Configuration for E2B code execution"""

    api_key: str = Field(description="The API key for e2b_code_interpreter")
    timeout: int = Field(
        default=3000, description="Timeout for code execution in milliseconds"
    )
