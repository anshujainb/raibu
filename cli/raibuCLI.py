import click
import requests
import json
import yaml

link = "localhost"

__author__ = "Anshu Jain"

@click.group()
def main():
    """
    Simple CLI for controlling Raibu tool for application deployment.
    """
    pass

@main.command()
@click.argument('query')
def provision(query):
    """This will provision number of EC2 VMs on AWS cloud."""
    
    url_format = "http://" + link + ":5000/Launch"

    data=json.loads(yamlToJson(query))

    response = requests.post(url_format, json = data)
    rp=json.dumps(response.json(), sort_keys=True,indent=4,separators=(',',':'))
    click.echo(rp) 

@main.command()
@click.argument('query')
def deploy(query):
    """This will deploy client's application on number of EC2 VMs on AWS cloud."""
    
    url_format = "http://" + link + ":5001/deploy"

    data=json.loads(yamlToJson(query))

    response = requests.post(url_format, json = data)
    rp=json.dumps(response.json(), sort_keys=True,indent=4,separators=(',',':'))
    click.echo(rp)


def yamlToJson(YamlFile):
    with open(YamlFile) as f:
        dataMap = yaml.safe_load(f)
        
    return (json.dumps(dataMap))


if __name__ == "__main__":
    main()
