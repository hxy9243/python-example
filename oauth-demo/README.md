OAuth with Google Demo
====

This is an example of creating an app login with Google's OAuth service, along with configuration
to deploy to Google AppEngine.

# Deployment

To start running the app, you'll need to register and configure your own app for Google OAuth service at:

https://console.cloud.google.com/apis/credentials
https://console.cloud.google.com/apis/credentials/consent

And saves `client-secret.json` to this folder.

# Development

To develope/test it locally, run:

```
DEBUG=1 OAUTHLIB_INSECURE_TRANSPORT=1 gunicorn -b :5000 --log-level DEBUG app.app:app
```

To deploy to Google App Engine, create your app at:

https://console.cloud.google.com/appengine/services

And follow instructions on Google Cloud SDK:

