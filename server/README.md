# 

## How to run
- Backend ( `/server` Directory )
    - **STEP 1** : Install Poetry ( [Install Poetry](https://python-poetry.org/docs/) )
    - **STEP 2** : Install Project Dependencies ( `poetry install` )
    - **STEP 3** : Copy `/server/.env.example` to `/server/.env` and configure variables
    - **STEP 4** : Run `poetry run start` 
    - **STEP 5** : 🚀

## Additional Configurations & Common Pitfalls
- VSCode (and other IDEs)
    - *Problem* Poetry creates a venv for its dependencies. This may cause issues with intellisense.
    - *Solution* Navigate to `/server` and run `poetry env info` to view Virtualenv settings. Copy the Path of the python venv and set it as the interperter path in VSCode.

## Conventions 
### Commit Messages
- `:gitmoji: (Scope): Message In Title Case`