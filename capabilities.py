"""The capability registry: what the app can do, who may do it, and the one way to do it.

Each action is declared once, next to its implementation (todos.py, view.py), and every caller
runs it through `execute`: the screen as the person, the chat as the agent. So there is one
owner per operation, and authority is checked where the work happens, not by what a caller was
shown: an action missing from the agent's tools is also refused if the agent calls it anyway.

No domain here: this module knows actions, callers and policies, never todos.
"""

import hashlib
import json
from contextlib import nullcontext
from copy import deepcopy
from dataclasses import dataclass, field

EFFECTS = ('read', 'write', 'presentation')
SURFACES = ('ui', 'embedded_agent')
# Who calls, and from where. The adapter says who is calling; a model's arguments never do.
SURFACE_OF = {'person': 'ui', 'agent': 'embedded_agent'}
JSON_TYPES = {'string': str, 'integer': int, 'number': (int, float), 'boolean': bool,
              'array': list, 'object': dict, 'null': type(None)}


class ActionError(ValueError):
    """A request the app refuses. The message says what would work instead."""


@dataclass(frozen=True)
class Guard:
    """A declared semantic check. Inputs are explicit; execution authority stays in code.

    Most guards look for a problem (yes refuses). A guard with require_yes=True instead
    requires a positive answer. Extra evidence needs a reason, so a proposed action cannot
    accidentally leak into a check intended to judge the user's words alone.
    """
    name: str
    question: str
    refusal: str
    threshold: float = 0.5  # for probability providers; binary answers use require_yes directly
    inputs: tuple = ('words',)
    reason: str = ''
    provider: str = 'decisions'
    require_yes: bool = False

    def refuses(self, probability):
        if type(probability) is bool:
            return probability != self.require_yes
        return probability <= self.threshold if self.require_yes else probability >= self.threshold



@dataclass(frozen=True)
class Action:
    id: str                 # stable, e.g. 'todos.complete'
    capability: str         # the group it belongs to, e.g. 'todos'
    description: str        # what the model reads: purpose, when to use it, limits, neighbours
    params: dict            # JSON Schema properties; all required, nothing extra
    effects: tuple          # from EFFECTS; never empty
    handler: object         # callable(ctx, **args) -> a result that says what is true
    tool: str | None = None  # the name a model is offered; None when no model is offered it
    version: int = 1
    surfaces: tuple = SURFACES
    policy: dict = field(default_factory=lambda: {'person': 'allow', 'agent': 'allow'})
    # Impact and reversibility are separate decisions, both declared here and both enforced by
    # register(): an agent may not simply do what cannot be taken back, or what touches many.
    undone_by: str | None = None  # the action that takes this one back; None: nothing can
    impact: str = 'one'     # 'one' item, or 'many'
    needs_current_read: bool = False  # changes an existing item: an agent must have read the current state
    facts: tuple = ()  # short truths about the app this action touches, incl. what it does not do
    propose: object = None  # callable(ctx, **args), run instead of handler when the policy is 'approval'
    guard_description: str = ''  # concise operation semantics for guards; not added to chat tools
    guards: tuple = ()  # names of Guards an interface may enforce before this runs

    def descriptor(self):
        """Everything but the code: what a catalog or an inspector sees."""
        return {'action_id': self.id, 'capability_id': self.capability, 'action_version': self.version,
                'tool': self.tool, 'description': self.description,
                'input_schema': schema(self.params), 'effects': list(self.effects), 'surfaces': list(self.surfaces),
                'policy': dict(self.policy), 'impact': self.impact,
                'recovery': {'mode': 'compensate', 'by': self.undone_by} if self.undone_by else {'mode': 'none'},
                'needs_current_read': self.needs_current_read, 'facts': list(self.facts), 'guards': list(self.guards),
                'guard_description': self.guard_description}


def schema(params):
    """A strict object schema: the caller must send exactly these fields, with these types."""
    return {'type': 'object', 'properties': params, 'required': list(params), 'additionalProperties': False}


class Registry:
    def __init__(self, app_id):
        self.app_id = app_id
        self.transaction = lambda ctx: nullcontext()  # the application supplies its storage boundary
        self._by_id, self._by_tool, self._guards = {}, {}, {}

    def guard(self, guard):
        if guard.name in self._guards:
            raise ValueError(f'Guard {guard.name} is already registered.')
        if guard.provider not in ('decisions', 'chat'):
            raise ValueError('Unknown guard provider.')
        if not guard.inputs or len(set(guard.inputs)) != len(guard.inputs):
            raise ValueError('Guard inputs must be nonempty and unique.')
        if set(guard.inputs) - {'words', 'conversation', 'state', 'action', 'current_date', 'calendar', 'tool_meanings'}:
            raise ValueError('Unknown guard input.')
        if guard.inputs != ('words',) and not guard.reason:
            raise ValueError('Additional guard evidence needs a reason.')
        if not 0 <= guard.threshold <= 1:
            raise ValueError('Guard threshold must be a probability.')
        self._guards[guard.name] = guard
        return guard

    def guard_named(self, name):
        return self._guards[name]

    @property
    def guards(self):
        return list(self._guards.values())

    def register(self, action):
        if action.id in self._by_id:
            raise ValueError(f'Action {action.id} is already registered.')
        if action.tool and action.tool in self._by_tool:
            raise ValueError(f'Tool {action.tool} already belongs to {self._by_tool[action.tool].id}.')
        if not callable(action.handler):
            raise ValueError(f'{action.id}: handler must be callable.')
        if set(action.policy.values()) - {'allow', 'approval', 'forbidden'}:
            raise ValueError(f'{action.id}: unknown policy decision.')
        if not action.effects or set(action.effects) - set(EFFECTS):
            raise ValueError(f'{action.id}: effects must be some of {EFFECTS}.')
        if set(action.surfaces) - set(SURFACES):
            raise ValueError(f'{action.id}: surfaces must be some of {SURFACES}.')
        if 'write' in action.effects and action.policy.get('agent') == 'allow':
            if action.undone_by is None:
                raise ValueError(f'{action.id} cannot be taken back, so the agent may not simply do it: '
                                 "make its agent policy 'approval' or 'forbidden'.")
            if action.impact != 'one':
                raise ValueError(f"{action.id} touches many items: make its agent policy 'approval' or 'forbidden'.")
        if set(action.guards) - set(self._guards):
            raise ValueError(f'{action.id}: no guard named {sorted(set(action.guards) - set(self._guards))}.')
        if 'approval' in action.policy.values() and action.propose is None:
            raise ValueError(f'{action.id}: an approval policy needs propose, the request it makes instead.')
        self._by_id[action.id] = action
        if action.tool:
            self._by_tool[action.tool] = action
        return action

    def action(self, id, **declared):
        """Register the function below as this action's handler, so a declaration sits on its code."""
        def bind(handler):
            self.register(Action(id=id, capability=id.split('.')[0], handler=handler, **declared))
            return handler
        return bind

    def get(self, action_id):
        return self._by_id.get(action_id)

    def by_tool(self, tool):
        return self._by_tool.get(tool)

    @property
    def actions(self):
        return list(self._by_id.values())  # registration order

    def tools_for(self, surface, actor, order):
        """The OpenAI strict function schemas this caller is offered, in the order the interface
        chose (order is presentation, so the interface owns it). It must name exactly the tools the
        caller may be offered. An offer is not permission: `execute` checks again."""
        offered = {a.tool: a for a in self.actions
                   if a.tool and surface in a.surfaces and a.policy.get(actor, 'forbidden') != 'forbidden'}
        if sorted(order) != sorted(offered):
            raise ValueError(f'The {surface} order must name exactly {sorted(offered)}; got {order}.')
        # A tool's description is its purpose and then its facts: what the model reads when it chooses.
        return [{'type': 'function', 'function': {'name': t, 'strict': True,
                                                  'description': ' '.join((offered[t].description, *offered[t].facts)),
                                                  'parameters': schema(offered[t].params)}} for t in order]

    def catalog(self):
        """What the app can do, as JSON. The revision changes with any descriptor change, wording
        included, so a run can say exactly which contract it measured."""
        actions = [a.descriptor() for a in self.actions]
        guards = {g.name: {'question': g.question, 'threshold': g.threshold, 'refusal': g.refusal,
                           'inputs': list(g.inputs), 'reason': g.reason, 'provider': g.provider,
                           'require_yes': g.require_yes}
                  for g in self._guards.values()}
        revision = hashlib.sha256(json.dumps({'actions': actions, 'guards': guards},
                                             sort_keys=True).encode()).hexdigest()[:12]
        return {'contract_version': 1, 'app_id': self.app_id, 'catalog_revision': revision, 'actions': actions,
                'guards': guards}


def execute(registry, action_id, args, *, actor, ctx):
    """The one way to run an action, for every caller: resolve, check authority, validate, run."""
    action = registry.get(action_id)
    if action is None:
        raise ActionError(f'No action {action_id}.')
    policy = action.policy.get(actor, 'forbidden')
    if SURFACE_OF.get(actor) not in action.surfaces or policy == 'forbidden':
        can = [who for who, surface in SURFACE_OF.items()
               if surface in action.surfaces and action.policy.get(who, 'forbidden') != 'forbidden']
        raise ActionError(f'The {actor} cannot {action_id}; only the {" or the ".join(can) or "nobody"} can.')
    validate(action, args)
    # The owning store supplies the transaction; the registry knows no domain fields.
    with registry.transaction(ctx):
        result = action.propose(ctx, **args) if policy == 'approval' else action.handler(ctx, **args)
        # Evidence belongs to this invocation, not to mutable objects changed by later calls.
        return deepcopy(result)


def validate(action, args):
    """Exactly the declared fields, of the declared JSON types, before any handler runs."""
    if not isinstance(args, dict):
        raise ActionError(f'{action.id} takes an object with {sorted(action.params)}.')
    missing, extra = set(action.params) - set(args), set(args) - set(action.params)
    if missing or extra:
        raise ActionError(f'{action.id} takes exactly {sorted(action.params)}; '
                          + '; '.join(filter(None, [missing and f'missing {sorted(missing)}',
                                                    extra and f'unexpected {sorted(extra)}'])) + '.')
    for name, spec in action.params.items():
        _check(f'{action.id} {name}', args[name], spec)


def _check(where, value, spec):
    types = spec.get('type', [])
    types = [types] if isinstance(types, str) else types
    # bool is an int in Python, not in JSON
    if types and not any(isinstance(value, JSON_TYPES[t]) and not (isinstance(value, bool) and t in ('integer', 'number'))
                         for t in types):
        raise ActionError(f'{where} must be {" or ".join(types)}; got {value!r}.')
    if 'enum' in spec and value not in spec['enum']:
        raise ActionError(f'{where} must be one of {", ".join(map(str, spec["enum"]))}; got {value!r}.')
    if isinstance(value, list) and 'items' in spec:
        for item in value:
            _check(where, item, spec['items'])
    if isinstance(value, dict) and 'properties' in spec:  # an object inside a list: exactly its fields
        missing, extra = set(spec['properties']) - set(value), set(value) - set(spec['properties'])
        if missing or extra:
            raise ActionError(f'{where} items take exactly {sorted(spec["properties"])}; got {sorted(value)}.')
        for name, inner in spec['properties'].items():
            _check(f'{where} {name}', value[name], inner)


REGISTRY = Registry(app_id='evalbasics')  # the app's one registry: todos.py and view.py declare into it
