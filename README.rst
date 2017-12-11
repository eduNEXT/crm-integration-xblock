README for CRM integration XBlock

Testing with Docker
-------------------

This XBlock comes with a Docker test environment ready to build, based on the xblock-sdk workbench. To build it, run::

        $ docker build -t crm-integration-xblock .

Then, to run the docker image you built::

        $ docker run -d -p 8000:8000 --name crm-integration-xblock crm-integration-xblock

The XBlock SDK Workbench, including this XBlock, will be available on the list of XBlocks at http://localhost:8000
