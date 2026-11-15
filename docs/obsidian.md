# Read and review in Obsidian

## Open the vault

1. Install [Obsidian](https://obsidian.md).
2. Choose **Open folder as vault** and select the repository folder (`Knowledge_AI_Engineering` after a `git clone`).
3. Open [00-moc-ai-engineering.md](../00-moc-ai-engineering.md).

## Review with spaced repetition

The files follow the syntax of the community plugin **Spaced Repetition**, which is not installed by default:

1. In **Settings → Community plugins**, enable community plugins, then find and install **Spaced Repetition**.
2. The plugin discovers topics through the `#flashcards` tag on line 2 of each file.
3. Configure the plugin:
   - **Separator for multiline flashcards**: keep `?`.
   - **Characters denoting the end of clozes and multiline flashcards**: enter `---`. This is essential: otherwise, each answer stops at its first blank line.
   - **Convert folders to decks and subdecks**: enable it to get a deck per section.
   - **Show context in cards**: enable it to display the topic title above each question.
4. Start a review from the sidebar icon or command palette. The palette also lets you review only the open note.

> The plugin stores scheduling **in the cards themselves**, as `<!--SR:...-->` comments after each card. These comments appear in Git diffs when you version the vault.

## Without Obsidian

The files are simple Markdown and can be read in any editor. Only links in `[[...]]` format are not clickable outside Obsidian.
