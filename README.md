# home-assistant-themeparks-integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

A Home Assistant integration that shows Theme Park waiting times using the ThemeParks.wiki API

Now available in the default store!

## How it works

When you add the themeparks integration you choose a themepark from the list. It then adds an entity for each ride, which looks like this:

<img width="1256" alt="Screenshot 2022-08-16 at 09 52 04" src="https://user-images.githubusercontent.com/613776/184842205-491f83d0-2da3-471f-9490-9cdb12650d48.png">

The state of each entity is the current wait time, and is updated every 5 minutes, so you can either use the entity card to show this, or the history card to show the history:

<img width="994" alt="Screenshot 2022-08-16 at 09 53 07" src="https://user-images.githubusercontent.com/613776/184842334-f758df62-a688-4e2c-99cb-7f177d37d416.png">

You can of course add whichever rides you need to.


## Advanced usage

A smart move would be to set automations when your ride of choice hits a low wait time, and then turn that automation on when you are at the park.


## Todo / Missing Features

* The device added for a theme park doesn't show any information or link to the entities. Looks like a quick fix.
* No customisations.


