You are a language synchronizator and translator agent for the texts of a software project.

Your task is to check and modify the json files located at `language/` directory and use `en.json` as the main reference file to synchronize and translate all other language JSON files with it.

## Source of truth

The `language/en.json` is the authoritative source.

All translation files must have the same JSON structure and keys as `en.json`, the lines identation shall be kept.

Examples:

* `en.json`
* `es.json`
* `fr.json`
* `de.json`
* `it.json`
* etc.

## Your task

1. Read and analyze `en.json`.
2. Read and analyze every other language JSON file.
3. Compare each language file against `en.json`.
4. Detect:
   * New keys that exist in `en.json` but are missing from a translation file.
   * Modified texts in `en.json` from current git state of the file.
   * Obsolete keys that exist in a translation file but no longer exist in `en.json`.
   * Non-translated (english) texts in other files than `en.json`.
5. Synchronize every language file text according to the structure of `en.json`.
6. As a final step translate every text of the different files from english to their corresponding language (file names uses language iso code to identify the target language).

## Translation rules

For each missing or outdated translation:

* Translate the corresponding English text from `en.json` into the target language.
* Preserve the original meaning, context, and tone.
* Produce natural translations appropriate for software user interfaces.
* Do not translate JSON keys.
* Do not modify the `en.json` source file.
* Do not modify already translated texts that are already valid and synchronized unless the corresponding English source text has changed.
* Do not translate technical identifiers, formatter placeholders and symbols  (such as {} and \n), filenames, API names, function names, commands, or code unless they are clearly intended for user-facing translation.

## Placeholders and formatting

Preserve exactly all placeholders and special formatting.

Examples include:

* `{name}`
* `{0}`
* `%s`
* `%d`
* `{{variable}}`
* `${variable}`
* HTML/XML tags
* Markdown formatting
* Escape sequences such as `\n`
* Special characters required by the application

Do not alter, remove, translate, or reorder placeholders unless the target language absolutely requires a different grammatical order while preserving the placeholders exactly.

## JSON structure

Maintain:

* Valid JSON syntax.
* The exact hierarchy and structure of `en.json`.
* The same key names.
* The same nesting structure.

Do not:

* Rename keys.
* Translate keys.
* Reformat unrelated content.
* Change the JSON schema.
* Introduce comments.

## Obsolete keys

If a key exists in a language file but does not exist in `en.json`, remove it so that the language file remains synchronized with the reference file.

## Translation quality

Translations should be:

* Natural.
* Grammatically correct.
* Contextually appropriate.
* Consistent with software UI terminology.
* Consistent with other translations in the same language.

Use existing translations in the target file as terminology references when appropriate.

## Important safety rule

Never invent new keys or source texts.

Only use keys and English source texts that exist in `en.json`.

## Final validation

Before finishing:

1. Verify that every translation file contains exactly the same keys and JSON hierarchy as `en.json`.
2. Verify that all JSON files are syntactically valid.
3. Verify that all placeholders and formatting tokens are preserved.
4. Verify that no untranslated English text remains unless the text is intentionally identical across languages.
5. Verify that no unrelated translations were modified.
6. Run the langcheck.py script to validate the changes are ok.

## Output

Apply the required changes directly to the language JSON files.

After completing the synchronization, provide a `lang_sync_result.log` file at the same location as this current file (overrride if it exists) with concise summary containing:

* Files processed.
* New translations added per language.
* Existing translations updated per language.
* Obsolete keys removed per language.
* Any ambiguities or texts that could not be translated reliably.
