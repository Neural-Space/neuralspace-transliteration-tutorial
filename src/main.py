import click
import yaml
from keyword_listener import KeyphraseListener


@click.command()
@click.option(
    "-k",
    "--keyword",
    type=click.STRING,
    required=True,
    prompt=True,
    help="Keyword which will trigger the bot",
)
@click.option(
    "-c",
    "--config",
    type=click.STRING,
    required=True,
    prompt=True,
    help="Keyword which will trigger the bot",
)
def main(keyword: str, config: str):
    with open(config, "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)

    listener = KeyphraseListener(keyword, config)
    rules = listener.get_rules()
    delete = listener.delete_all_rules(rules)
    set = listener.set_rules(delete)
    listener.get_stream(set)


if __name__ == "__main__":
    main()
