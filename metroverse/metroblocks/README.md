# Metroblocks

Metroblocks is a website for analysis and optimization of the Metroverse
NFT trading game. You can see it in action at [metroblocks.io](https://metroblocks.io).

Contributions are more than welcome.

## Developing

The application is a simple Flask app. To run, do the following:

```
# (one-time setup)
pip install virtualenv
virtualenv virt
source ./virt/bin/activate
pip install -r requirements.txt

python application.py
```

## Deploying

You need access to my AWS account in order to deploy. But the service is hosted
on Elastic Beanstalk and is deployed like this:
```
eb deploy test # or 'eb deploy prod' for prod
```
