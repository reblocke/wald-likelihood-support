# Privacy

## Scope

The app is designed for aggregate numerical estimates and settings. It neither requires nor is
designed to receive patient-level records, names, dates, identifiers, free text, or protected
health information (PHI).

Do not enter PHI or other identifying or confidential data. Client-side architecture reduces
transmission and retention, but it is not a compliance certification or authorization to process
regulated data.

## Data flow

User input is read by the page, sent through `postMessage` to a same-origin Web Worker, processed
by Python in Pyodide, and returned to the page for display/export. Inputs exist only in page and
worker memory for the current page session. Restarting the worker or closing/reloading the page
removes application-held values.

## Guardrails

The application design has:

- no backend or database;
- no user account or authentication system;
- no telemetry or analytics;
- no local storage or session storage;
- no IndexedDB or service-worker data cache;
- no input values in URL query strings or fragments;
- no cookies;
- no application logging of inputs or protected health information;
- no hidden persistence;
- no upload or sharing path; and
- no automatic clipboard or download action.

Static requests fetch HTML, CSS, JavaScript, Plotly, Pyodide, and generated Python files. User
values are not included in request URLs, headers, or bodies. CDN operators can observe ordinary
network metadata such as IP address and requested static asset, but not values entered into this
app.

## Exports

The five-column CSV, dashboard PNG, and figure-only PNG are created locally only after an explicit
button press. Caption copying is also explicit. The browser and operating system determine where
downloads and clipboard contents are retained. The app does not upload, reopen, or manage those
outputs.

Users are responsible for reviewing an output before sharing it and for handling downloaded or
copied values according to their local policy. Avoid screenshots or committed fixtures containing
sensitive real-world inputs.

## Development and testing

- Use synthetic or clearly public aggregate fixtures only.
- Never place entered values in test names, URLs, logs, analytics events, screenshots, issue
  reports, or committed artifacts.
- Browser privacy tests inspect URLs, request bodies, storage, cookies, and production source for
  prohibited data paths.
- Error messages may identify an invalid field but must not echo the user’s value, a traceback, or
  a local filesystem path.

## Change gate

Every new input, fixture, URL, log, export, dependency, or deployment change requires privacy
review. If storage, a server, telemetry, analytics, sharing, or upload is proposed, stop before
implementation and document:

1. the exact data elements and purpose;
2. network and storage flow;
3. retention and deletion;
4. access and authentication;
5. third parties and jurisdictions;
6. consent and user notice; and
7. applicable institutional, legal, and compliance assumptions.

Those capabilities are outside the current authorized scope.
