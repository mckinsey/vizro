# How to run your dashboard in development

Typically when you create a dashboard, there are two distinct stages:

1. Development. This is when you build your app. You make frequent changes to your code and want a simple way to see how the dashboard looks after each change. At this point, you may, or may not, want to make it possible for other people to access your dashboard.
1. Production. When you complete development of your app, you _deploy_ it to production. The dashboard should be accessible to other people.

This page describes methods to run your dashboard _in development_. When you are ready to deploy your app to production, read our [guide to deployment](deploy.md).

Vizro is built on top of [Dash](https://dash.plotly.com/), which itself uses [Flask](https://flask.palletsprojects.com/). Most of our guidance on how to run a Vizro app in development or production is very similar to guidance on Dash and Flask.
