## discord-bot
Discord is the official means of communication for Choate Programming Union.

This is the home of the new CPU Discord bot.

## Running and Installing
First, setup MongoDB locally or remotely. 
Then, set your environment variables to include your Discord token, database URI, etc.

Finally, run this:

```bash
poetry install
poetry shell
(in the Poetry shell) python run.py
```

## Contributing
All contributions are welcome -- we welcome PRs, new issues, or simply better documentation. If you're here to edit a message template, the templates can be found in `bot/messages.yaml`.
All work is done under the GPL license (see LICENSE) for more.

## Acknowledgments
Our thanks go to Jerry Wang \'20 (CPU Officer 2018-2019, President 2019-2020), who made the first iteration of CPUBot.
