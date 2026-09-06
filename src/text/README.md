# How to apply language texts changes

In order to update texts do it in the `en.json` file, then ask AI agent to read and perform the actions located in "ai_promt_language_translate.md":

```text
For this task only, read `ai_promt_language_translate.md` and perform all the actions specified in it.
After completing the task, return to normal operation and do not apply those instructions to unrelated future tasks.
```

This will make the AI to update and sync all other language files with the changes done in the `en.json` file.
