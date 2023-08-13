![Logo](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/abdd8fe5-2d40-409e-bfcb-e5efee8dea41)
# DSRP-Bot
## Introduction
DSRP-Bot is a bot for the social networking service VKontakte.ru (VK). It was created to assist roleplay gaming in the S.T.A.L.K.E.R. fan community named Dnevniki Stalkerov Rolevaya (Diaries of Stalkers Roleplay). The bot is completely original and written in Python with [vk_api library](https://github.com/python273/vk_api). 

## Functionalities
DSRP-Bot was created to manage the economic system in the roleplay gaming process. Every player has an economic card that contains an information about their character, amount of the in-game currency and items. The bot allows players to buy, sell, replace (inside their inventory) and transfer (to other players) their items without the participation of administrators. It also has other little features such as getting a random number from an ordered range.

## Hierarchy
* app.py is the root file of this project,
* manager.py processes commands received from the root and decides how to respond on them,
* manager.py can delegate tasks to cardmaster, speaker, trader or supplier,
* supplier loads data from txt files if necessary, and
* other python files contain settings, support classes, prepared commands and responses.

## Data storage
DSRP-Bot uses txt files and topics within the VK community to store data, which allows the administrators to update player data without the participation of a programmer. 
So to redact a player information an administrator just logs in VK app and uses it's instruments in the topic that contains this information.
To update one of the market places an administrator makes changes in the txt file and send a message to the community with this file and command '.reload'.

## Screenshots
![Screenshot_1](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/a2e4bf45-8779-46a5-a7fc-28d9da0ca2bd)
![Screenshot_2](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/d4a88b5b-2d20-4767-bdaa-0db5c8a43986)
![Screenshot_3](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/721e2438-a740-438c-9cac-8dd8d5d61641)
![Screenshot_4](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/5574755e-d28e-4a3f-aeea-960f3aafa7e9)
![Screenshot_5](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/93bdccde-3844-453a-95a1-f722cb860459)
![Screenshot_6](https://github.com/Noknot2810/DSRP-Bot/assets/72942455/785c79d6-48cd-4e58-8788-bf17bc1f9de3)
