# PRRI-HoloGameV2026

A retro game for the HoloGameV platform developed by students and the [Artificial Intelligence Laboratory](https://ai.foi.hr/) at the [University of Zagreb Faculty of Organization and Informatics](https://www.foi.unizg.hr/). The game is developed using [TIC-80](https://tic80.com/). More details available at [itch.io](https://ailab-foi.itch.io/prri-hologamev2026). 

## Instructions

To start and/or test the game you need to install [TIC-80](https://tic80.com/). Position your console to the `src` folder and run:

```
tic80 --fs .
```

When TIC80 starts run:

```
load hologamev.py
```

And then run the game with:

```
run
```

To test the controller, you need to edit `gamepad\config.py` and change the `executable` setting of the `hologamev` game to the path of the TIC80 executable.

When done, position your console in the gamepad subfolder and you can start the server with:

```
python server.py
```

Use your mobile device to open the controller interface in the browser at the IP address of your computer on port 5000.

# Credits

A previous version of this game has been developed [here](https://github.com/AILab-FOI/PRRI-HoloGameV2024/tree/main) and [here](https://github.com/AILab-FOI/PRRI-HoloGameV2025).

## Acknowledgements

This work has been supported in part by the Croatian Science Foundation under the project number [IP-2019-04-5824](http://dragon.foi.hr:8888/ohai4games).

