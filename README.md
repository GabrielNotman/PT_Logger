# PT_Logger

## 1. Installation
Copy **_config.json_**, **_pt_logger.py_**, and **_pt_logger.sh_** to a folder on the machine you will be running the logger from. The suggested folder is the same as the installation folder for PT: _/var/opt/pt_.

## 2. Create a ThingSpeak Account
If you do not already have a thingSpeak account, you can will need to sign up for one here: https://thingspeak.com/users/sign_up
Once signed up and logged in, _go to Channels->My Channels->New Channel_, you will see a form similar to this one:
![Channel Settings](/img/channelSettings.png?raw=true)
At minimum you will need to check fields 1-5. You should also provide a name for the channel and a description for those fields similar to the ones show.
You will need to copy your __Write API Key__ from the API Keys tab. If you want to make your data publicly viewable, see the sharing tab.

You can format the private or public view charts by clicking the edit button on any given chart. This will bring up the chart options:

![chart 5 Settings](/img/field5.png?raw=true")
You should look at modifying the _Results_ to match the number of entries you wish to view (for hourly logging, 168 will show 1 week). Additionally, for the __Daily Profit__ and __Daily Sales__, the _Type_ should be set to _column_.

## 3. Configuration
You will need to edit _config.json_:
  - __host:__ Only change this if you are running PT on a different machine from the logger. 
  - __port:__ Only change this if you are running PT on a differnt port.
  - __password:__ This needs to be set to your PT monitor login password.
  - __writeApiKey:__ This needs to be set your ThingSpeak Channel's Write API Key.

## 4. Schedule a Cron Job
Run:
```sh
$ crontab -e
```
Add this (assuming the suggested installation folder of _/var/opt/pt_):
```
0 * * * * cd /var/opt/pt && ./pt_logger.sh
```
This will schedule a cron job to run every hour (on the 0 minute mark).



