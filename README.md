# AI Agent Workflow Demo

A Python command-line demo that takes a business request, shows the plan, and produces a reviewed answer. Three roles share one OpenAI client. Each has a separate job, so you can follow how the original request becomes a final draft.

## Run locally

From the project directory on macOS or Linux, create and activate a virtual environment.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

Set `OPENAI_API_KEY` in your local `.env` file, then start the CLI. A live run requires API access.

```sh
python main.py
```

## How a request moves through the workflow

1. **Planner** asks the model for a JSON list of one to three task descriptions and validates the response. The prompt asks for one step when a single draft will do. The CLI displays the plan before execution.
2. **Worker** executes each step in order. It receives the original request and the previous step’s result, keeping details such as the audience and word limit in view.
3. **Reviewer** checks the draft against the original request. For an email draft, it returns a subject and body. Python assembles the email and checks explicit English limits such as `under 100 words` against the whole text, including the subject and sign-off. The CLI displays the verified email and its word count separately.

A run with `N` steps normally makes `1 + N + 1` model calls. If an email fails format or length validation, only the Reviewer gets one more attempt, bringing the maximum to six calls. A second invalid email stops the workflow before the CLI displays a final answer. Blank input stops before any call. An invalid plan or failed API request stops the workflow at the affected stage.

## Example Workflow

### Step 1: Enter a request

Start the CLI and enter this request.

> Write an email to a customer explaining that their order will arrive two days late. Keep the entire email under 100 words.

### Step 2: Inspect the generated plan

Point to the plan printed before the Worker starts. For this request, an illustrative plan is `["Draft a customer email explaining the two-day delay in under 100 words."]`. Compare it with “Create a marketing plan for a coffee shop,” which might call for identifying a target audience and then building a campaign for that audience. The actual steps can vary by run.

### Step 3: Review the final output

Read the final email and check that it says *two days*. For this request, Python accepts at most 99 whitespace-separated words, including the `Subject:` label and sign-off. A possible final email is shown below.

> Subject: Your order will arrive two days late
>
> Hello,
>
> Your order will arrive two days later than expected. I’m sorry for the delay and for any inconvenience this causes. If the new timing creates a problem, please reply and we’ll help you with your options.
>
> Customer Support

## Run the tests

Run the offline suite from the project directory. It uses Python’s standard library and mocked model responses. It also runs before you install the live API dependencies or configure a key.

```sh
python -m unittest discover -s tests -v
```

## Project layout

```text
main.py                    CLI and workflow orchestration
agents/
  planner.py               Generates and validates the plan
  worker.py                Executes one step at a time
  reviewer.py              Reviews the final draft against the request
services/
  openai_client.py         Shared model client and API error handling
tests/
  test_workflow.py         Offline tests
requirements.txt           Python dependencies
.env.example               Local configuration template
```
