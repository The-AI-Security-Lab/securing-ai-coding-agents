# Know Before You Go

This guide prepares you for **Securing AI Coding Agents: From Guardrails to
Verification**, a 90-minute virtual workshop from the AI Security Lab. It is
written for a broad audience and supports both people who want to run the
exercises and people who want to follow the instructor.

## What you will learn

The workshop connects two parts of an AI coding-agent security workflow:

- how to govern and harden an agent's capabilities with clear controls;
- how to verify those controls with repeatable security checks and evidence;
- how to interpret a small set of expected and unexpected outcomes without
  treating a single demonstration as a complete security guarantee.

Claude Code and Codex are both covered. You do not need to install both tools
to participate.

## The two labs

### Lab 1 — Govern and harden AI coding agents

The first lab examines practical guardrails for AI coding agents. You will
consider what an agent is allowed to do, which controls should govern those
capabilities, and how to make a hardened configuration understandable and
reviewable.

### Lab 2 — Verify security controls

The second lab introduces a compact verification workflow:

1. define basic security evals for the controls under discussion;
2. exercise a small golden dataset with known expected outcomes;
3. run a deterministic Python harness so the same checks can be repeated; and
4. collect evidence that makes the result inspectable.

The verification exercise is intentionally bounded. It demonstrates how to
test a stated property and preserve evidence; it does not claim to establish
the security of every agent, model, repository, or production environment.

## Choose your participation pathway

### Hands-on

Choose this route if you want to execute the exercises on your own machine.
Complete the validated technical setup and preflight instructions that will be
published before the event, then use the workshop materials and synthetic
fixtures provided for the labs.

### Instructor-led

Choose this route if you prefer to watch, discuss, and reason through the
exercises with the instructor. You can follow the concepts, expected outcomes,
and evidence review without running the commands locally. This is a supported
way to participate, especially for a large virtual audience or when local
compatibility is uncertain.

## If Claude Code or Codex is new to you

You do not need prior experience with both tools. Before the workshop, it is
helpful to know how to:

- open a terminal and work in a directory provided for the exercise;
- recognize which application or agent is being demonstrated;
- read a command before running it and stop if its effect is unclear; and
- distinguish an agent's proposed action from an action you have actually
  approved or executed.

The final preflight will identify the supported route for the event. Do not
install an agent, select a version, or configure a provider based on this guide
alone.

## Authentication and access

If you take the hands-on route, the selected agent pathway may require an
appropriate subscription, organizational entitlement, or API access. The exact
requirement depends on the validated exercise path and will be stated in the
final setup instructions. No subscription tier, cost, or provider arrangement
is established by this guide.

You will also need permission to use your terminal and to run the workshop
commands in the directory and environment you choose. If your organization
restricts terminal use, developer tools, external services, or local file
access, use the instructor-led pathway unless your administrator has approved
the hands-on setup.

## GitHub access

The workshop may use public repository material. A GitHub account is not
universally required merely to view or download a public repository.

Forking a repository and pushing changes are different actions: they require an
account and the relevant permission to create a fork or write to the
destination. Follow the final workshop instructions for any repository
interaction that is actually needed. Do not assume that you must push changes
to the workshop repository.

## Optional isolated environments

You may choose to use an isolated environment, such as a separate user
profile, development workspace, or other locally approved boundary, if it is
compatible with the final exercises and permitted by your organization. An
isolated environment is optional unless the validated lab pathway says
otherwise. Do not introduce a virtual machine, container, or other dependency
solely because it is available; wait for the final compatibility guidance.

## Use synthetic workshop materials safely

The workshop is designed around synthetic materials. Use only the fixtures and
examples supplied or explicitly approved for the exercises.

- Do not paste real credentials, API keys, source code, customer data, or
  production configuration into the workshop exercises.
- Do not point an exercise at a production repository, production account, or
  real external destination.
- Keep generated logs and evidence in the designated workshop location, and
  remove them or handle them according to your organization's policy afterward.

The purpose of synthetic materials is to make the security boundary safe to
inspect and repeat; it is not permission to test systems you do not own or
have authorization to use.

## Complete the setup and preflight

Before the event:

1. choose hands-on or instructor-led participation;
2. read the validated technical setup when it is published;
3. confirm that you have the required access for your chosen pathway;
4. run the published preflight in a safe, approved environment; and
5. keep the workshop guide available so you can switch to instructor-led
   participation if local setup is unavailable or incompatible.

Exact installation commands, Python version requirements, agent setup, and
repository commands are intentionally not included here. Validated setup
instructions and the lab materials will be published separately before the
event.

For updates and further learning, visit the [AI Security Lab](https://www.aisecuritylab.com/).
