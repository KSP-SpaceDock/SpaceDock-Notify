## Project retired

This project is no longer in use. It was in charge of finding CKAN modules affected by a SpaceDock event and notifying the NetKAN webhooks. It translated a SpaceDock mod id to one or more CKAN module identifiers by searching the NetKAN repo.

This was replaced by functionality on the CKAN side created in https://github.com/KSP-CKAN/NetKAN-Infra/pull/48 and activated on the SpaceDock side in https://github.com/KSP-SpaceDock/SpaceDock/pull/246. Finally it was removed from SpaceDock's startup sequence in https://github.com/KSP-SpaceDock/SpaceDock/pull/259.

## Old readme

SpaceDock's HTTP notifier for CKAN. Seperate project as it depends on NetKAN-meta.  
  
Setup (after cloning):  

```sh
git clone https://github.com/KSP-CKAN/NetKAN  
virtualenv -p /usr/bin/python3 .  
. bin/activate  
pip install -r requirements.txt  
python app.py  
(edit config.ini)  
python app.py  
```
