# BMRS Settlement Analytics

This is my submission for the Associate Trading Developer — Technical Exercise.
For more information about the requirements of this task, see
[smartest-dev-technical-exercise.md](smartest-dev-technical-exercise.md)

---

## Setup

All the instructions in this README are targeting **Linux / MacOS** unless explicitly stated otherwise.

1. Ensure **Python 3.10** or greater is installed.
   * Verify the installation in a terminal by running `python --version` or `python3 --version`.
2. Clone the repository and navigate to the directory root.
3. Create a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment (recommended):
   #### Linux / MacOS
   ```bash
   source venv/bin/activate
   ```
   #### Windows (PowerShell)
   ```powershell
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Execution

The following command generates a report for the previous settlement day:
   ```bash
   python main.py
   ```

## Tests

The following command runs the full test suite:
   ```bash
   pytest
   ```

## Assumptions and Trade-offs

TODO

## Notes

* Choosing a data format (json, xml, csv)
    * Industry standard for REST APIs
    * Includes metadata (unlike csv)
    * JSON integrates better with libraries e.g. httpx
* The `SettlementProcessor` maps the downstream Elexon field names to new names.
This ensures that if Elexon were to rename any of them, our code only has to change once rather than everywhere the
field is referenced.
* Assumption: A UK Settlement Day runs from 23:00 to 23:00 GMT, but the Elexon API handles this abstraction.

Future development:
* Include an `api_key` member in the `ElexonClient` class for any future endpoints which require an API key.
A secure way to handle an API key is to encrypt it (e.g. using `dotenvx`), and save the encrypted key in a `.env` file,
which is safe to commit to a public repository. The GitHub secrets manager must then store the `DOTENV_PRIVATE_KEY`
requred to decrypt the API key, injecting it into the runtime environment. This ensures that no secrets are exposed in
the repository, and the API key is not saved in plaintext on any local device.
* Include unit tests for logging.
* Modify the `tenacity` decorator in the client to only retry specific errors i.e. most 500 errors should be retried
but most 400 errors should not.
* Add a second method in the client for retrieving the Indicated Imbalance Volumes (IIV);
currently the settlement system prices only return a `netImbalanceVolume`.
* Structure the project so that the logic from `main.py` is moved to another file within the `energy_report` package,
and `main.py` just the entry point for the script.
* Allow the user to specify the desired report date when running the script.
