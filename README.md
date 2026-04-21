* Choosing a data format (json, xml, csv)
    * Industry standard for REST APIs
    * Includes metadata (unlike csv)
    * JSON integrates better with libraries e.g. httpx

Future development:
* Include an `api_key` member in the `ElexonClient` class for any future endpoints which require an API key.
A secure way to handle an API key is to encrypt it (e.g. using `dotenvx`), and save the encrypted key in a `.env` file,
which is safe to commit to a public repository. The GitHub secrets manager must then store the `DOTENV_PRIVATE_KEY`
requred to decrypt the API key, injecting it into the runtime environment. This ensures that no secrets are exposed in
the repository, and the API key is not saved in plaintext on any local device.
* Include unit tests for logging.
