
For all JSON language files located inside language/ directory (exception en.json file; use it as source of trust), detects and translate all english texts to each corresponding language of that file.

Rules:
- NEVER modify language/en.json or any non JSON file.
- Never check or use any other files than the ones located inside "language/" and the "langcheck.py" file. 
- Do not create any new file (exception is "lang_translate_result.log").
- Do the translation from your own AI knowledge about languages (don't use any external service neither create any script for performing the translation).
- Preserve correct existing translations. Do not retranslate unnecessarily.
- Never translate JSON keys.
- Preserve format placeholders, variables, HTML/XML tags, Markdown, escape sequences, URLs, code, usernames and technical identifiers exactly.
- Run the langcheck.py script for final validating if changes in all files are OK.
- Ensure all english texts got translated.

At the end, create or overwrite lang_translate_result.log next to this instruction file with a concise summary of:
- Files processed.
- New keys translated on each file.
- Any unresolved issues and reasons for them.
- Final langcheck.py stdout-stderr result.
