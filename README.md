# Remark

This application is work in progress. I initially wanted to create a tool to easily fuse routes together, because I accidentially saved activities in between. 
However, Strava's API currently does not provide the necessary functionality for non-premium members.

# Strava Connector

The Strava Connector provides tools for easy connection to the Strava API. It simplifies the OAuth2 authentication process for the Strava API and handles requests to obtain access and refresh tokens.

Additionally, the StravaRequestor class can extract recent activities from your Strava account. This class is designed to be easily extendable, allowing for further customization and functionality enhancements. The base functionality is supposed to be extended (Work in Progress!).

Please compare demo.ipynb for an example of how to use the source code.


# Requirements

This code requires a valid Strava account. 
You will only be able to see whatever you are allowed to see in Strava. 


The usage of this is bound to the usage restrictions listed here: https://developers.strava.com/




# Setup

After cloning the repository, you'll need to set up the virtual environment. Follow these steps to create and activate a Python virtual environment:

1. **Create the Environment:**

   Run the following command to create a virtual environment named "venv":

   ```bash
   python -m venv venv
   ```

   > **Note**: Depending on your system configuration, you may need to use `python3` instead of `python`.

2. **Activate the Environment:**

   The command to activate the environment varies based on your operating system:

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

3. **Install Requirements:**

   Once the environment is activated, install all the required packages by running:

   ```bash
   pip install -r requirements.txt
   ```


## Getting initial secrets

You will need to add a `secrets.json` file into the source code directory. This file must contain at least your Strava client ID and client secret. You can obtain these credentials through the Strava UI by following the instructions [here](https://developers.strava.com/docs/getting-started/#account).

Here is an example of how your `secrets.json` file should be structured. Copy the following JSON template and replace `<your client id (int)>` and `<your client secret hash (str)>` with your actual client ID and client secret.

```json
{
  "client_id": <your client id (int)>,
  "client_secret": "<your client secret hash (str)>"
}
```
