from dataclasses import dataclass

import click
import desert
import marshmallow
import requests

API_URL: str = "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"


@dataclass
class Page:
    title: str
    extract: str


schema = desert.schema(Page, meta={"unknown": marshmallow.EXCLUDE})


def random_page(language: str = "en") -> Page:
    url = API_URL.format(language=language)

    try:
        # Context manager needed? https://github.com/psf/requests/issues/4136
        with requests.get(url) as response:
            response.raise_for_status()
            data = response.json()
            page = schema.load(data)
            if not page or isinstance(page, list):  # pylance
                raise marshmallow.ValidationError("")
            return page
    except (requests.RequestException, marshmallow.ValidationError) as error:
        message = str(error)
        raise click.ClickException(message) from error
