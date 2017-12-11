README for CRM integration XBlock

Enabling in Studio
-------------------

After successful installation, you can activate this component for a
course following these steps:

* From the main page of a specific course, navigate to `Settings -> Advanced Settings` from the top menu.
* Check for the `Advanced Module List` policy key, and Add ``"crm-integration"``` to the policy value list.
* Click the "Save changes" button.


Testing with Docker
-------------------

This XBlock comes with a Docker test environment ready to build, based on the xblock-sdk workbench. To build it, run::

        $ docker build -t crm-integration-xblock .

Then, to run the docker image you built::

        $ docker run -d -p 8000:8000 --name crm-integration-xblock crm-integration-xblock

The XBlock SDK Workbench, including this XBlock, will be available on the list of XBlocks at http://localhost:8000
