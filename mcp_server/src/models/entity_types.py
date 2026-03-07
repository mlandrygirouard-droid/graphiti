"""Entity type definitions for Graphiti MCP Server — code-centric schema."""

from pydantic import BaseModel, Field


class Module(BaseModel):
    """A source file in the codebase (.rs, .py, .svelte, .ts). The hub node — most edges route through modules.

    Expected relationships:
    - DEPENDS_ON another Module (import-level dependency)
    - DEFINES a Symbol (function, class, component)
    - Task READS or EDITS this Module
    - Bug RESOLVED_IN this Module
    - Decision INFLUENCES this Module
    """

    path: str = Field(
        ...,
        description='Relative path from project root',
    )
    layer: str = Field(
        default='',
        description='Architectural layer derived from path (service, feature, component, etc.)',
    )
    stack: str = Field(
        default='',
        description='Which stack: backend or frontend',
    )
    language: str = Field(
        default='',
        description='Programming language: rust, python, svelte, typescript',
    )
    file_name: str = Field(
        default='',
        description="File name without path, e.g. 'channel_service.rs'",
    )


class Symbol(BaseModel):
    """A named code construct: function, method, class, component, store, export, action, or loader.

    Expected relationships:
    - Module DEFINES this Symbol
    - This Symbol CALLS another Symbol
    """

    kind: str = Field(
        default='',
        description='Symbol kind: function, method, component, class, store, export, action, loader',
    )
    is_exported: bool = Field(
        default=False,
        description="Whether this symbol is part of the module's public interface",
    )
    module_path: str = Field(
        ...,
        description='Path of the containing module',
    )
    return_type: str = Field(
        default='',
        description='Return type annotation if available',
    )
    qualified_name: str = Field(
        ...,
        description="Symbol name, e.g. 'validate_token', 'ChannelList'",
    )


class Task(BaseModel):
    """A logical unit of work spanning one or more sessions. Represents intent — what the agent was trying to accomplish.

    Expected relationships:
    - READS a Module (viewed without modifying)
    - EDITS a Module (modified code)
    - DELETES a Module (removed file)
    - DISCOVERS a Bug
    - FIXES a Bug
    - Decision MOTIVATED_BY this Task
    """

    title: str = Field(
        ...,
        description="What was being done, e.g. 'Implement webhook retry with exponential backoff'",
    )
    status: str = Field(
        default='in_progress',
        description='Outcome: in_progress, completed, or abandoned',
    )
    project_path: str = Field(
        default='',
        description='Claude project path for traceability',
    )


class Bug(BaseModel):
    """A defect that was investigated, diagnosed, or fixed. Only extract when there is a clear problem-diagnosis-fix arc.

    Expected relationships:
    - Task DISCOVERS this Bug
    - Task FIXES this Bug
    - RESOLVED_IN a Module (where the fix was applied)
    """

    title: str = Field(
        ...,
        description='One-line description of the bug',
    )
    severity: str = Field(
        default='',
        description='Impact severity: low, medium, high, critical',
    )
    root_cause: str = Field(
        default='',
        description='What caused the bug, if identified',
    )


class Decision(BaseModel):
    """An architectural or implementation choice with rationale. Only extract when alternatives are explicitly weighed.

    Expected relationships:
    - INFLUENCES a Module (shaped its design)
    - MOTIVATED_BY a Task (made in context of task)
    """

    title: str = Field(
        ...,
        description="What was decided, e.g. 'Use decorator pattern for permission checks'",
    )
    rationale: str = Field(
        default='',
        description='Why this approach was chosen',
    )


ENTITY_TYPES: dict[str, type[BaseModel]] = {
    'Module': Module,
    'Symbol': Symbol,
    'Task': Task,
    'Bug': Bug,
    'Decision': Decision,
}
