# databases-searcher

Python 3 Flask application to search the libanswers FAQ searcher.

## Requires

* Python 3.10.8

### Development Setup

See [docs/DevelopmentSetup.md](docs/DevelopmentSetup.md).

## Environment Configuration

The application requires a ".env" file in the root directory to provide
server-specific information (i.e., those parts of the configuration that
may vary based on whether the server is a test/qa/production server).

A sample "env_example" file has been provided to assist with this process.
Simply copy the "env_example" file to ".env" and fill out the parameters as
appropriate.

The configured .env file should not be checked into the Git repository.

### Running in Docker

```bash
$ docker build -t docker.lib.umd.edu/databases-searcher .
$ docker run -it --rm -p 5000:5000 --env-file=.env --read-only docker.lib.umd.edu/databases-searcher
```

### Building for Kubernetes

```bash
$ docker buildx build . --builder=kube -t docker.lib.umd.edu/databases-searcher:VERSION --push
```

### App Caveats

⚠️ This app utilizes an unpublished LibGuides API. Springshare could change
API behavior without warning.

### Endpoints

This will start the webapp listening on the default port 5000 on localhost
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/>

/ping endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/ping>

/search:

```bash
http://127.0.0.1:5000/search?q=science
```

Example:

```bash
curl 'http://127.0.0.1:5000/search?q=science'
{
  "endpoint": "databases",
  "module_link": "https://lib.guides.umd.edu/az.php?q=science",
  "page": 1,
  "per_page": 3,
  "query": "science",
  "results": [
    {
      "description": null,
      "item_format": "database",
      "link": "https://proxy-um.researchport.umd.edu/login?url=http://link.springer.com/search?facet-discipline=%22Computer+Science%22",
      "title": "Springer eBooks in Computer Science"
    },
    {
      "description": "The Web of Science Core Collection provides comprehensive coverage of the sciences, social sciences, and arts, and humanities across journals, books and conference proceedings. It indexes more than 5,700 major journals across 164 scientific disciplines. The best database for finding what papers have cited other papers. Cited references can be traced forward in time. Web of Science Training Materials available here: http://wokinfo.com/training_support/training/web-of-science",
      "item_format": "database",
      "link": "https://proxy-um.researchport.umd.edu/login?url=https://webofscience.com/",
      "title": "Web of Science Core Collection"
    },
    {
      "description": "Essential Science Indicators can determine the influential individuals, institutions, papers, publications, and countries in their field of study as well as emerging research areas that can impact their work. This unique and comprehensive compilation of science performance statistics and science trends data is based on journal article publication counts and citation data from Thomson Reuters databases. It is an analytical resource for policymakers, administrators, analysts and information specialists in government agencies, universities, corporations, private laboratories, publishing companies and foundations, as well as members of the scientific press and recruiters. Essential Science Indicators (ESI) is useful tool to help answer questions about research performance. For example: Which institutions produce the most highly-cited research in a particular field? Where does our institution rank in this group? Who are the most influential researchers in this field? Is our institutions citation activity on an upward or downward trend? How did changes in funding influence the impact of research in a particular country or institute? Which are the hottest topics in research right now? How does my article's citation count compare to similar articles? ESI produces a variety of metrics and features such as Top 1% of Scientists and Institutions; Top 50% of Journals and Countries/Territories; Highly Cited Papers: Top 1% of cited papers per discipline; Hot Papers: Papers from the last two years that were cited the most (top 0.1%) in the last 2 months; Research Fronts: Creates clusters of highly cited articles, useful for identifying ground breaking discoveries",
      "item_format": "database",
      "link": "https://proxy-um.researchport.umd.edu/login?url=https://esi.clarivate.com/IndicatorsAction.action",
      "title": "Essential Science Indicators"
    }
  ],
  "total": 140
}
```

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.2.x/cli/?highlight=debug%20mode

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
