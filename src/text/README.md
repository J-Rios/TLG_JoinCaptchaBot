# How to apply language texts changes

In order to update texts do it in the `en.json` file, then ask AI agent to read and perform the actions located in "ai_promt_language_translate.md":

```text
Read and perform the task defined in the `ai_promt_language_translate.md` file.
```

This will make the AI to translate all language files texts to the corresponding languages according to `en.json` file (reference language).

Note: Due undeterministic behaviour of AI this is not a fully-trusted way to translate the languages, cause AI could understand this task specification in different ways. It could work today, but maybe a tomorrow AI model change could give a not totally working result. Always use it carefully and manually review translation results.
